import os
import sys
import asyncio
import json

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

from src.riot_client import RiotClient
from src import database

# --- Configuration ---
TEST_RIOT_ID = "ErrorUnknownName#NOPE" 

async def test_database():
    print("\n--- Testing Database Functions ---")
    
    print("1. Initializing DB...")
    database.init_db()
    print("   [PASS] DB Initialized")

    print(f"2. Adding user {TEST_RIOT_ID}...")
    success = database.add_user(TEST_RIOT_ID, "test_puuid_12345")
    if success:
        print(f"   [PASS] User added.")
    else:
        print(f"   [FAIL] User might already exist.")

    print("3. Getting all users...")
    users = database.get_all_users()
    print(f"   [PASS] Users found: {len(users)}")
    for u in users:
        print(f"     - {u['riot_id']} (PUUID: {u['puuid']})")

    print("4. Updating last game ID...")
    database.update_last_game(TEST_RIOT_ID, "SG2_1234567890")
    print("   [PASS] Updated last game.")

    print("5. Removing user...")
    removed = database.remove_user(TEST_RIOT_ID)
    if removed:
        print("   [PASS] User removed.")
    else:
        print("   [FAIL] User not found to remove.")

    print("6. Testing Subscriptions...")
    sub_id = "123456789"
    database.add_subscriber(sub_id)
    subs = database.get_subscribers()
    print(f"   [PASS] Subscribers: {subs}")
    database.remove_subscriber(sub_id)
    print("   [PASS] Subscriber removed.")

async def test_riot_api():
    print("\n--- Testing Riot API Functions ---")

    riot = RiotClient()
    print(f"Region: {riot.region}, Account routing: {riot.account_routing}, Match routing: {riot.match_routing}")

    if "TestID" in TEST_RIOT_ID:
        print("\n[WARNING] You are using a placeholder Riot ID.")
        return

    if '#' not in TEST_RIOT_ID:
        print("\n[ERROR] Invalid format. Use Name#Tag")
        return

    name, tag = TEST_RIOT_ID.split('#')

    # 1. Get Account (PUUID)
    print(f"\n1. get_account({name}, {tag})...")
    account = riot.get_account(name, tag)
    if not account:
        print("   [FAIL] Could not find account. Check the Riot ID or API Key.")
        return

    print(f"   [PASS] Account found: {account['gameName']}#{account['tagLine']}")
    print(f"   PUUID: {account['puuid']}")
    puuid = account['puuid']

    # 2. Get Summoner
    print(f"\n2. get_summoner_by_puuid({puuid[:10]}...)...")
    summoner = None
    try:
        summoner = riot.get_summoner_by_puuid(puuid)
        if summoner:
            print(f"   [PASS] Summoner ID: {summoner.get('id', 'N/A')}")
        else:
            print("   [FAIL] Summoner not found.")
    except Exception as e:
        print(f"   [DEBUG] Error: {e}")

    # 3. Get League Entries (Rank)
    if summoner and 'id' in summoner:
        summoner_id = summoner['id']
        print(f"\n3. get_league_entries({summoner_id})...")
        try:
            entries = riot.get_league_entries(summoner_id)
            if entries:
                print(f"   [PASS] Entries found: {len(entries)}")
                for entry in entries:
                    print(f"     - {entry['queueType']}: {entry['tier']} {entry['rank']} ({entry['wins']}W/{entry['losses']}L)")
            else:
                print("   [PASS] Unranked (no entries found)")
        except Exception as e:
            print(f"   [FAIL] Error fetching league entries: {e}")
    else:
        print("\n3. Skipping League Entries (no summoner ID)")

    # 4. Check if currently IN GAME
    print(f"\n4. Is {TEST_RIOT_ID} currently in a game?")
    try:
        game = riot.get_active_game(puuid)
        if game:
            mode = game.get('gameMode', 'Unknown')
            game_type = game.get('gameType', 'Unknown')
            duration_s = game.get('gameLength', 0)
            minutes = duration_s // 60
            seconds = duration_s % 60
            print(f"   [YES] Currently IN GAME!")
            print(f"   Mode:     {mode} ({game_type})")
            print(f"   Duration: {minutes}m {seconds}s so far")
            # Find the tracked player's champion
            for p in game.get('participants', []):
                if p.get('puuid') == puuid:
                    print(f"   Champion: {p.get('championId', 'Unknown')}")
                    break
        else:
            print(f"   [NO] {TEST_RIOT_ID} is NOT currently in a game.")
    except Exception as e:
        print(f"   [FAIL] Error checking active game: {e}")

    # 5. Get Match History
    print(f"\n5. get_match_history({puuid[:10]}...)...")
    try:
        matches = riot.get_match_history(puuid, count=1)
    except Exception as e:
        print(f"   [FAIL] Error fetching match history: {e}")
        return

    if not matches:
        print("   [FAIL] No matches found.")
        return

    print(f"   [PASS] Latest Match ID: {matches[0]}")

    # 6. Get Match Details & Stats
    match_id = matches[0]
    print(f"\n6. get_match_details({match_id})...")
    try:
        details = riot.get_match_details(match_id)
    except Exception as e:
        print(f"   [FAIL] Error fetching match details: {e}")
        return

    if details:
        game_duration_sec = details['info']['gameDuration']
        if game_duration_sec > 10000:
            game_duration_sec //= 1000

        minutes = game_duration_sec // 60
        seconds = game_duration_sec % 60
        print(f"   [PASS] Game Mode: {details['info']['gameMode']} ({minutes}m {seconds}s)")

        me = next((p for p in details['info']['participants'] if p['puuid'] == puuid), None)
        if me:
            win_status = "VICTORY" if me['win'] else "DEFEAT"
            kills, deaths, assists = me['kills'], me['deaths'], me['assists']
            kda_ratio = (kills + assists) / max(1, deaths)
            cs = me.get('totalMinionsKilled', 0) + me.get('neutralMinionsKilled', 0)

            print("\n   --- LATEST MATCH STATS ---")
            print(f"   Result:   {win_status}")
            print(f"   Champion: {me['championName']}")
            print(f"   KDA:      {kills}/{deaths}/{assists} ({kda_ratio:.2f})")
            print(f"   Damage:   {me.get('totalDamageDealtToChampions', 0):,}")
            print(f"   CS:       {cs}")
            print(f"   Vision:   {me.get('visionScore', 0)}")
            print(f"   Gold:     {me.get('goldEarned', 0):,}")
            print("   --------------------------\n")
        else:
            print("   [FAIL] Could not find the player in the match data.")
    else:
        print("   [FAIL] Could not fetch match details.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        TEST_RIOT_ID = sys.argv[1]
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(test_database())
    loop.run_until_complete(test_riot_api())