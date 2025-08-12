import logging

import sleeper.sleeper_api as sleeper_api

from sleeper.sleeper_user import User
from sleeper.sleeper_draft import Draft

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class League():
    """Represents a sleeper league, contains scoring and roster information"""
    def __init__(self, league_id: str, league_json: dict=None):
        self._retrieve_league_info(league_id, league_json)
        self._retrieve_users()
        self._add_draft()

        logger.info(f"Initialized {self}")
    

    def update_rosters(self):
        """Retrieves new roster data and updates the rosters of the users in the league"""
        pass


    def _retrieve_league_info(self, league_id:str, league_json: dict | None):
        """Collects the data for a given league and stores the data in this instance"""
        logger.info(f"Retrieveing league information for league ID {league_id}")

        if not league_json:
            league_json = sleeper_api.get_league_info(league_id)
        
        # Set league attributes
        self.league_json = league_json
        self.id = league_json.get("league_id")
        self.name = league_json.get("name")
        self.draft_id = league_json.get("draft_id")
        self.roster_positions = league_json.get("roster_position")
        self.scoring_settings = league_json.get("scoring_settings")
        self.league_settings = league_json.get("settings")
        self.status = league_json.get("status")
    

    def _retrieve_users(self):
        """Iterates through the users in the league and maps their usernames to their User object"""
        logger.info(f"Retrieving the available rosters for the {self}")

        self.users = {}
        self.rosters_json = sleeper_api.get_league_rosters(self.id)

        for roster in self.rosters_json:
            user_id = roster.get("owner_id")
            user = User(user_id)
            user.set_roster(roster)
            self.users[user.name] = user
    

    def _add_draft(self):
        """Adds a draft object to the league."""
        logger.info(f"Adding draft ID {self.draft_id} to {self}")

        self.draft = Draft(self.draft_id)
    

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.id}, {self.status})"



if __name__ == "__main__":
    me = User("TheCondor")
    league_id, league_json = me.retrieve_league_info("Margaritaville")
    redraft_league = League(league_id, league_json=league_json)

    logger.info(f"League attribute test id: {redraft_league.id}")
    logger.info(f"League attribute test name: {redraft_league.name}")
    logger.info(f"League attribute test draft_id: {redraft_league.draft_id}")
    logger.info(f"League attribute test roster_positions: {redraft_league.roster_positions}")
    logger.info(f"League attribute test scoring_settings: {redraft_league.scoring_settings}")
    logger.info(f"League attribute test league_settings: {redraft_league.league_settings}")
    logger.info(f"League attribute test status: {redraft_league.status}")

    logger.info(f"League attribute test Users: {redraft_league.users}")

    logger.info(f"League attribute test draft: {redraft_league.draft}")