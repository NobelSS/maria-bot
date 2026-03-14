import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

DEFAULT_REGION = 'sg2'
ACCOUNT_ROUTING = 'asia'  # Account-V1 uses the continental routing (asia)
MATCH_ROUTING = 'sea'     # Match-V5 uses the SEA routing cluster
