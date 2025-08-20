import logging
import pandas as pd
import re

from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class DraftTiersWorksheet(WorksheetWrapper):
    """Contains the live picks for the current league draft"""

    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        logger.info(f"Initialized {self}")
    

    def retrieve_tiers(self) -> pd.DataFrame:
        """Retrieves the player tier data from the worksheet as a dataframe"""
        logger.info(f"Retrieving player tier data")
        return self.read_dataframe()
    

    def add_player_ids(self, player_df: pd.DataFrame):
        """Retrieves the tiers and adds an index column with the sleeper player ids"""
        logger.info(f"Adding player ids to {self}")
        tiers_df = self.retrieve_tiers()
        tiers_df["normalized_name"] = tiers_df["full_name"].apply(self._normalize_name)

        merged_df = pd.merge(tiers_df, player_df[["player_id", "normalized_name"]], on="normalized_name", how="left")

        merged_df.set_index("player_id")
        self.clear()
        self.write_dataframe(merged_df)

    
    def _normalize_name(self, name: str):
        """Normalized the names of players to match accross datasets"""
        if not isinstance(name, str):
            name = ""
        name = name.lower().strip()
        # Remove common suffixes
        name = re.sub(r'\b(jr\.?|sr\.?|ii|iii|iv|v)\b', '', name)
        # Remove punctuation and extra whitespace
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip()