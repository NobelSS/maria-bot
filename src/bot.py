import os
import json
import time
import asyncio
import discord
from discord.ext import commands, tasks
from .config import DISCORD_TOKEN
from .riot_client import RiotClient
from . import database

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

riot = RiotClient()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_active_games.start()

@bot.command()
async def track(ctx, *, riot_id):
    """Adds a player to track. Format: GameName#Tag"""
    if '#' not in riot_id:
        await ctx.send("Please provide Riot ID in format GameName#Tag")
        return

    name, tag = riot_id.split('#')
    try:
        existing = database.get_all_users()
        if any(u['riot_id'].lower() == riot_id.lower() for u in existing):
             await ctx.send(f"Already tracking {riot_id}")
             return

        account = riot.get_account(name, tag)
        if not account:
            await ctx.send(f"Could not find summoner {riot_id}")
            return
            
        puuid = account['puuid']
        if database.add_user(riot_id, puuid):
            await ctx.send(f"Now tracking {riot_id}")
        else:
            await ctx.send(f"Error adding {riot_id} to database.")
            
    except Exception as e:
        await ctx.send(f"Error tracking user: {str(e)}")

@bot.command()
async def untrack(ctx, *, riot_id):
    """Stops tracking a player."""
    if database.remove_user(riot_id):
        await ctx.send(f"Stopped tracking {riot_id}")
    else:
        await ctx.send(f"{riot_id} is not being tracked.")

@bot.command()
async def subscribe(ctx):
    """Subscribe to receive game notifications via DM."""
    user_id = str(ctx.author.id)
    if database.add_subscriber(user_id):
        try:
            await ctx.author.send("You have subscribed to Maria-Bot notifications! I will DM you when tracked players start/end games.")
            await ctx.send(f"{ctx.author.mention} checked your DMs!")
        except discord.Forbidden:
             await ctx.send(f"{ctx.author.mention} I cannot DM you. Please enable DMs from server members.")
             database.remove_subscriber(user_id)
    else:
        await ctx.send(f"{ctx.author.mention} You are already subscribed.")

@bot.command()
async def unsubscribe(ctx):
    """Unsubscribe from game notifications."""
    user_id = str(ctx.author.id)
    if database.remove_subscriber(user_id):
        await ctx.send(f"{ctx.author.mention} Unsubscribed from notifications.")
    else:
        await ctx.send(f"{ctx.author.mention} You were not subscribed.")

pending_end_checks = {}
MATCH_FETCH_DELAY = 120
MATCH_FETCH_TIMEOUT = 600

@tasks.loop(minutes=1)
async def check_active_games():
    subscribers = database.get_subscribers()
    users = database.get_all_users()
    if not users:
        return

    now = time.time()

    for riot_id in list(pending_end_checks.keys()):
        info = pending_end_checks[riot_id]
        elapsed = now - info['ended_at']
        if elapsed >= MATCH_FETCH_DELAY:
            match = cleanup_and_get_match(info['puuid'], info['game_id'])
            if match:
                await notify_subscribers(subscribers, "end", riot_id, match=match, puuid=info['puuid'])
                del pending_end_checks[riot_id]
            elif elapsed >= MATCH_FETCH_TIMEOUT:
                print(f"Giving up fetching end match for {riot_id} after {MATCH_FETCH_TIMEOUT}s")
                del pending_end_checks[riot_id]

    for user in users:
        riot_id = user['riot_id']
        puuid = user['puuid']
        last_known_game = user['last_game_id']

        try:
            game = riot.get_active_game(puuid)

            if game:
                game_id = str(game['gameId'])
                if last_known_game != game_id:
                    database.update_last_game(riot_id, game_id)
                    await notify_subscribers(subscribers, "start", riot_id, game=game, puuid=puuid)
            else:
                # Game ended — queue a delayed match-data fetch
                if last_known_game and riot_id not in pending_end_checks:
                    database.update_last_game(riot_id, None)
                    pending_end_checks[riot_id] = {
                        'puuid': puuid,
                        'game_id': last_known_game,
                        'ended_at': now
                    }
                    print(f"{riot_id} game ended, will fetch results in {MATCH_FETCH_DELAY}s")

        except Exception as e:
            print(f"Error checking {riot_id}: {e}")

async def notify_subscribers(subscribers, event_type, riot_id, **kwargs):
    embed = None
    if event_type == "start":
        embed = create_game_start_embed(riot_id, kwargs['game'], kwargs['puuid'])
    elif event_type == "end":
        embed = create_game_end_embed(riot_id, kwargs['match'], kwargs['puuid'])
        
    if not embed:
        return

    channel = discord.utils.get(bot.get_all_channels(), name='league-feed')
    if channel:
         await channel.send(embed=embed)

    for user_id in subscribers:
        try:
            user = await bot.fetch_user(int(user_id))
            if user:
                await user.send(embed=embed)
        except discord.Forbidden:
            print(f"Cannot DM user {user_id} - they might have DMs closed.")
        except Exception as e:
            print(f"Error sending DM to {user_id}: {e}")

def create_game_start_embed(riot_id, game, user_puuid):
    embed = discord.Embed(title="🎮 Match Started!", color=0x00ff00)
    embed.description = f"**{riot_id}** has started a match!"
    
    mode = game.get('gameMode', 'Unknown')
    embed.add_field(name="Mode", value=mode, inline=True)
    
    participants = game.get('participants', [])
    
    user_team = None
    
    for p in participants:
         if p.get('puuid') == user_puuid:
             user_team = p.get('teamId')
             break
    
    if user_team:
        opponents = [p for p in participants if p.get('teamId') != user_team]
        op_list = []
        
        for op in opponents[:5]:
            try:
                summ_id = op.get('summonerId')
                name = op.get('summonerName', 'Unknown')
                
                is_bot = op.get('bot', False)
                if is_bot:
                    continue

                if summ_id:
                    entries = riot.get_league_entries(summ_id)
                    rank_str = "Unranked"
                    win_rate_str = ""
                    
                    for entry in entries:
                        if entry['queueType'] == 'RANKED_SOLO_5x5':
                            tier = entry['tier']
                            rank = entry['rank']
                            wins = entry['wins']
                            losses = entry['losses']
                            total_games = wins + losses
                            
                            win_rate = 0
                            if total_games > 0:
                                win_rate = int((wins / total_games) * 100)
                                
                            rank_str = f"{tier} {rank}"
                            win_rate_str = f"({win_rate}% WR)"
                            break
                    
                    if win_rate_str:
                        op_list.append(f"**{name}**: {rank_str} {win_rate_str}")
                    else:
                        op_list.append(f"**{name}**: {rank_str}") 
                else:
                    op_list.append(f"**{name}**: Unknown")
            except Exception:
                op_list.append(f"**{op.get('summonerName', 'Unknown')}**: (Error)")
        
        if op_list:
            embed.add_field(name="Opponents", value="\n".join(op_list), inline=False)

    return embed

def create_game_end_embed(riot_id, match, puuid):
    participant = next((p for p in match['info']['participants'] if p['puuid'] == puuid), None)
    if not participant:
        return None

    win = participant['win']
    kills = participant['kills']
    deaths = participant['deaths']
    assists = participant['assists']
    kda = f"{kills}/{deaths}/{assists}"
    champion = participant['championName']

    cs = participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0)
    damage = participant.get('totalDamageDealtToChampions', 0)
    gold = participant.get('goldEarned', 0)
    vision = participant.get('visionScore', 0)
    game_duration_s = match['info'].get('gameDuration', 0)
    minutes = game_duration_s // 60
    seconds = game_duration_s % 60

    kda_ratio = round((kills + assists) / max(deaths, 1), 2)

    result_text = "Victory 🏆" if win else "Defeat 💀"
    color = 0x00ff00 if win else 0xff0000

    embed = discord.Embed(title="🏁 Match Ended", color=color)
    embed.description = f"**{riot_id}** just finished a match as **{champion}**!"
    embed.add_field(name="Result", value=result_text, inline=True)
    embed.add_field(name="Duration", value=f"{minutes}m {seconds}s", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)  # spacer
    embed.add_field(name="KDA", value=f"{kda} ({kda_ratio})", inline=True)
    embed.add_field(name="CS", value=str(cs), inline=True)
    embed.add_field(name="Vision Score", value=str(vision), inline=True)
    embed.add_field(name="DMG to Champions", value=f"{damage:,}", inline=True)
    embed.add_field(name="Gold Earned", value=f"{gold:,}", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)  # spacer
    return embed

def cleanup_and_get_match(puuid, game_id):
    try:
        matches = riot.get_match_history(puuid, count=1)
        if matches:
            latest_match_id = matches[0]
            if str(game_id) in latest_match_id:
                return riot.get_match_details(latest_match_id)
    except Exception:
        pass
    return None