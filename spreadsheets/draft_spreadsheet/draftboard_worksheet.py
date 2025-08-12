import logging
import pandas as pd

from sleeper.sleeper_league import League
from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class DraftboardWorksheet(WorksheetWrapper):
    """Contains the live draftboard for the current league draft"""
    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        logger.info(f"Initialized {self}")
    

    def update_draftboard(self, draftboard_df: pd.DataFrame):
        """Updates the current draft board with a new DataFrame without the most recent picks"""
        logger.info(f"Updating {self} with most recent pick")
        self.clear()
        self.write_dataframe(draftboard_df)