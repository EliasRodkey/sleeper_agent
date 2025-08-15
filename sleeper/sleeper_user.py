import logging
import pandas as pd

import sleeper.sleeper_api as sleeper_api
from sleeper.sleeper_roster import Roster

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class User:
    """Represents a user of the sleeper platform, Retrieves the user ID and using the sleeper API."""
    _instances = {}  # Class-level registry of username → User instance
    _iterator = 1 

    def __new__(cls, username: str):
        if username in cls._instances:
            username = f"{str(username)}_duplicate_user_{cls._iterator}"
            cls._iterator += 1
        instance = super().__new__(cls)
        cls._instances[username] = instance
        return instance
    
    def __init__(self, username: str):
        self.info = sleeper_api.get_user_info(username)
        self.name = self.info.get("username")
        self.id = self.info.get("user_id")
        
        logger.info(f"Initialized {self}")
    

    def retrieve_league_info(self, league_name: str) -> tuple[str, dict] | None:
        """Collects all of the informaiton for the leagues the user is in and sorts it into an accessible format."""
        logger.info(f"Retrieveing all of the league data for {self}")

        leagues_json = sleeper_api.get_user_leagues(self.id)

        self.league_names = [league["name"] for league in leagues_json]

        if league_name in self.league_names:
            league_idx = self.league_names.index(league_name)
            self.league = leagues_json[league_idx]
            self.league_id = self.league.get("league_id")
            return self.league_id, self.league
        
        logger.error(f"No leagues found called {league_name} for user {self.name}, available leagues: {self.league_names}")

    
    def set_roster(self, roster_json: dict, player_df: pd.DataFrame):
        """Sets the roster attribute for the user"""
        logger.info(f"Updating current roster information for {self}")
        self.season_stats = roster_json.pop("settings")
        self.roster = Roster(roster_json, player_df)


    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.id})"


    @classmethod
    def get_all_users(cls):
        return list(cls._instances.values())



if __name__ == "__main__":
    me = User("thecondor")
    logger.info(f"User attribute test repr: {me}")
    logger.info(f"User attribute test info: {me.info}")
    logger.info(f"User attribute test name: {me.name}")
    logger.info(f"User attribute test id: {me.id}")
    leaggue_id, league_json = me.retrieve_league_info('Margaritaville')
    # logger.info(f"User method test retrieve_league_info: {me.league_id, me.league}")