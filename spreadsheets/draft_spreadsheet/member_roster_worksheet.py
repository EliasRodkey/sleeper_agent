import logging

from sleeper.sleeper_league import League
from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class MemberRosterWorksheet(WorksheetWrapper):
     """Contains the live picks and roster for the members of the current league draft"""
     def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        logger.info(f"Initialized {self}")


     def set_league_and_players(self, league: League):
        """Adds the league to the worksheet and updates the worksheet with the current memeber roster, always call before update_roster"""
        logger.info(f"Setting .league attribtue for {self} to {league}")
        self.league = league
        
        self.update_roster(self.play)
    

     def update_roster(self):
         """"""
         pass