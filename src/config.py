import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

DEFAULT_REGION = 'sg2'
DEFAULT_ROUTING = 'sea' 
