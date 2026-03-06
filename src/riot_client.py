from riotwatcher import LolWatcher, RiotWatcher, ApiError
from .config import RIOT_API_KEY, DEFAULT_REGION, DEFAULT_ROUTING

class RiotClient:
    def __init__(self):
        self.watcher = LolWatcher(RIOT_API_KEY)
        self.riot_watcher = RiotWatcher(RIOT_API_KEY)
        self.region = DEFAULT_REGION
        self.routing = DEFAULT_ROUTING

    def get_account(self, game_name, tag_line):
        try:
            return self.riot_watcher.account.by_riot_id(self.routing, game_name, tag_line)
        except ApiError as err:
            if err.response.status_code == 404:
                return None
            raise

    def get_summoner_by_puuid(self, puuid):
        try:
            return self.watcher.summoner.by_puuid(self.region, puuid)
        except ApiError as err:
            if err.response.status_code == 404:
                return None
            raise

    def get_active_game(self, puuid):
        try:
            return self.watcher.spectator.by_puuid(self.region, puuid)
        except AttributeError:
            try:
                return self.watcher.spectator.by_summoner(self.region, puuid)
            except ApiError as err:
                if err.response.status_code == 404:
                    return None
                raise
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