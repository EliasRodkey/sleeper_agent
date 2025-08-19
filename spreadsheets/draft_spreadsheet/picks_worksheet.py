import logging
import pandas as pd

from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class PicksWorksheet(WorksheetWrapper):
    """Contains the live picks for the current league draft"""

    HEADERS = ["pick_no", "full_name", "adp", "fantasy_positions", "injury_status", "team", "username", "draft_slot", "height", "weight", "age"]

    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        logger.info(f"Initialized {self}")
    

    def update_picks(self, picks_df: pd.DataFrame):
        """updates the pick board with the latest picks from the draft"""
        logger.info(f"Updating {self} with the latest picks from the draft")
        try:
            self.write_dataframe(picks_df[self.HEADERS])
        
        except Exception as e:
            logger.warning(f"Update failed for {self}, exception: {e}")


