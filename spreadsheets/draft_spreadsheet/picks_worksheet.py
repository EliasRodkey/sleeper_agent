import logging

from sleeper.sleeper_league import League
from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class PicksWorksheet(WorksheetWrapper):
    """Contains the live picks for the current league draft"""
    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        logger.info(f"Initialized {self}")
    

    def set_league(self, league: League):
        """Adds the league to the worksheet and updates the worksheet with the current picks, always call before update_picks"""
        logger.info(f"Setting .league attribtue for {self} to {league}")
        self.league = league
        self.update_picks()
    

    def update_picks(self):
        """"""
        pass