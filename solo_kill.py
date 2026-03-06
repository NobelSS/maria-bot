import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
GAME_NAME = "KayShawn258"
TAG_LINE = "6969"

# REGION: 'sea' is the correct routing for the new SG2/SEA server merge
REGION_MATCH = "sea"    
REGION_ACCOUNT = "asia" 

def get_puuid(game_name, tag_line):
    url = f"https://{REGION_ACCOUNT}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json().get('puuid') if response.status_code == 200 else None

def get_match_details(match_id):
    url = f"https://{REGION_MATCH}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

# --- EXECUTION ---
puuid = get_puuid(GAME_NAME, TAG_LINE)

if puuid:
    print(f"PUUID Found: {puuid}\n")
    
    # 1. Get the list of most recent matches (we only need the first one)
    list_url = f"https://{REGION_MATCH}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=5"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    match_ids = requests.get(list_url, headers=headers).json()
    
    if match_ids and isinstance(match_ids, list):
        # 2. Grab the VERY FIRST match ID (Most Recent)
        most_recent_id = match_ids[0]
        print(f"Retrieving Most Recent Match: {most_recent_id}...")
        
        match_data = get_match_details(most_recent_id)
        
        if match_data:
            # 3. Find your participant data
            for participant in match_data['info']['participants']:
                if participant['puuid'] == puuid:
                    print(f"\n--- FULL STATS FOR {GAME_NAME} ---")
                    # This prints the entire formatted JSON for your player
                    print(json.dumps(participant, indent=4)) 
        else:
            print("Error: Could not retrieve match details.")
    else:
        print("Error: No matches found in history. (Check API Key or Region)")
else:
    print("Error: Could not find Summoner PUUID.")