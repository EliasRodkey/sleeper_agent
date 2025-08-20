import logging
import pandas as pd

from sleeper.sleeper_league import League
from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class DraftboardWorksheet(WorksheetWrapper):
    """Contains the live draftboard for the current league draft"""

    HEADERS = ["adp", "full_name", "team", "fantasy_positions", "injury_status", "height", "weight", "age"]

    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        logger.info(f"Initialized {self}")
    

    def update_draftboard(self, draftboard_df: pd.DataFrame):
        """Updates the current draft board with a new DataFrame without the most recent picks"""
        logger.info(f"Updating {self} with most recent pick")
        self.clear()
        try:
            self.write_dataframe(draftboard_df[self.HEADERS])
        
        except Exception as e:
            logger.warning(f"Failed to post draftboard_df to {self}, attempting to remove 'adp': {e}")
            modified_headers = self.HEADERS.copy()
            modified_headers.remove("adp")
            self.write_dataframe(draftboard_df[modified_headers])
            