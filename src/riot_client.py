from riotwatcher import LolWatcher, ApiError
from .config import RIOT_API_KEY, DEFAULT_REGION, DEFAULT_ROUTING

class RiotClient:
    def __init__(self):
        self.watcher = LolWatcher(RIOT_API_KEY)
        self.region = DEFAULT_REGION
        self.routing = DEFAULT_ROUTING

    def get_account(self, game_name, tag_line):
        try:
            return self.watcher.account.by_riot_id(self.routing, game_name, tag_line)
        except ApiError as err:
            if err.response.status_code == 404:
                return None
            raise

    def get_summoner_by_puuid(self, puuid):
        return self.watcher.summoner.by_puuid(self.region, puuid)

    def get_active_game(self, puuid):
        try:
            summoner = self.get_summoner_by_puuid(puuid)
            return self.watcher.spectator.by_summoner(self.region, summoner['id'])
        except ApiError as err:
            if err.response.status_code == 404:
                return None
            raise

    def get_match_history(self, puuid, count=5):
        return self.watcher.match.matchlist_by_puuid(self.routing, puuid, count=count)

    def get_match_details(self, match_id):
        return self.watcher.match.by_id(self.routing, match_id)

    def get_league_entries(self, summoner_id):
        return self.watcher.league.by_summoner(self.region, summoner_id)
