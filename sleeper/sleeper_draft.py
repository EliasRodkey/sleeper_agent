from datetime import datetime, timedelta
import logging
import pandas as pd
import time

from sleeper.ffcalc_api import get_half_ppr_adp_df, get_rookie_adp_df
import sleeper.sleeper_api as sleeper_api

from spreadsheets.spreadsheet_utils import normalize_name

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class Draft:
    """Represents a sleeper draft, holds pick information, remaining players and methods to update"""
    PRE_DRAFT = "pre_draft"
    DRAFTING = "drafting"
    PAUSED = "paused"
    COMPLETE = "complete"

    def __init__(self, league):
        self.league = league
        self.id = league.draft_id
        self.picks = []
        self.last_picks = [] 
        self._retrieve_draft_info(league.draft_id)
        self.update_picks()

        logger.info(f"{self} Initialized")

    
    def update_picks(self) -> str:
        """
        Updates the picks attribute with the most recent picks from the draft.
        Returns the draft status as a string.
        """
        logger.debug(f"Updating {self} with most recent picks from the draft")
        self.last_picks = self.picks # convert last_picks to the current picks before update
        draft_status = self.update_status()
        self.status = draft_status
        self.picks = sleeper_api.get_draft_picks(self.id)
        if self.picks != []:
            self.picks_df = self._convert_picks_json_to_df(self.picks)
        
        return self.status
        
        
    def update_status(self):
        """Retrieves the most recent draft status"""
        logger.debug(f"Retrieving draft status for {self}")
        self.status = sleeper_api.get_draft_info(self.id).get("status")
        return self.status
    

    def retrieve_draft_state(self, players_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Uses the players_df and picks_df to return the current remaining players and picked players dataframes"""
        self.update_picks()
        if self.picks != []:
            adp_df = self.merge_with_adp(players_df, is_redraft=self.league.redraft)
            enriched_picks_df = self.merge_picks_with_players(players_df)
            remaining_players_df = self.get_remaining_players(adp_df, enriched_picks_df)

            return enriched_picks_df, remaining_players_df
        
        else:
            logger.warning(f"No draft picks recorded yet: status={self.status}")
            return pd.DataFrame(), pd.DataFrame()
    

    def wait_until_draft_resumes(self):
        """Checks the status of the draft continuously until it is no longer paused"""
        logger.info(f"{self} {self.status.upper()}, waiting for status change")
        while self.update_status() == self.PAUSED:
            logger.debug(f"Latest status={self.status}")
            time.sleep(1)


    def wait_until_draft(self):
        """Wait until the draft has started then continue"""
        if self.start_time == None:
            logger.info(f"No start time set, waiting for draft to start...")
            return
        time_to_wait = self.start_time - datetime.now()
        if time_to_wait < timedelta():
            logger.warning(f"{self} past start time by {-time_to_wait}, status={self.status}")
            return
        logger.warning(f"Draft {self} is in {self.status}. Waiting {time_to_wait} for {self} to begin")
        time.sleep(time_to_wait.total_seconds())
        logger.info(f"{self} has begun, good luck!")
    

    def merge_picks_with_players(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriches draft picks with player metadata by merging on 'player_id'. 
        Returns a DataFrame indexed by 'player_id', sorted by round and pick number.
        """
        self.picks_df["player_id"] = self.picks_df["player_id"].astype(str)
        players_df["player_id"] = players_df["player_id"].astype(str)

        merged_df = self.picks_df.merge(players_df, on="player_id", how="left", suffixes=("_player", ""))

        # Optional: sort and index for roster logic
        merged_df = merged_df.sort_values(by=["round", "pick_no"])
        merged_df = merged_df.set_index("player_id")

        for col in merged_df.columns:
            if merged_df[col].isna().all():
                merged_df.drop(columns=col, inplace=True)

        return merged_df
    

    @staticmethod
    def merge_with_adp(players_df: pd.DataFrame, is_redraft: bool=True) -> pd.DataFrame:
        """Sorts the players dataframe by ADP gathered from FantasyFootballCalculator.com API"""
        logger.info(f"Sorting players dataframe by ADP")
        if is_redraft:
            adp_df = get_half_ppr_adp_df()
        
        else:
            adp_df = get_rookie_adp_df()

        adp_df = adp_df[adp_df['full_name'].notna()]
        adp_df.loc[adp_df['position_x'] == 'DEF', 'full_name'] = adp_df.loc[adp_df['position_x'] == 'DEF', 'team_x'] + ' Defense'
        adp_df['normalized_name'] = adp_df['full_name'].apply(normalize_name)

        merged_df = pd.merge(players_df, adp_df[['normalized_name', 'adp']], on='normalized_name', how='left')

        max_adp = adp_df['adp'].max()
        merged_df['adp'] = merged_df['adp'].fillna(max_adp + 1)

        return merged_df.sort_values('adp')
    

    @staticmethod
    def get_remaining_players(players_df: pd.DataFrame, picks_df: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a DataFrame of players who have not been drafted.
        Assumes 'player_id' is a column in both DataFrames.
        """
        # Normalize player_id source
        if "player_id" in picks_df.columns:
            drafted_ids = picks_df["player_id"].astype(str).str.strip()
        else:
            drafted_ids = picks_df.index.astype(str).str.strip()

        # Normalize players_df player_id
        players_df["player_id"] = players_df["player_id"].astype(str).str.strip()

        # Subtract drafted players
        remaining_df = players_df[~players_df["player_id"].isin(drafted_ids)].copy()

        return remaining_df



    def _convert_picks_json_to_df(self, picks: dict) -> pd.DataFrame:
        """Converts the picks json API return to a dataframe with other metadata"""
        picks_df = pd.DataFrame.from_dict(picks)

        picks_df.drop(columns=["is_keeper", "metadata"], inplace=True)

        # Add username column to picks_df
        picks_df['username'] = picks_df['picked_by'].map(self.league.id_username_map)
        picks_df['username'] = picks_df['username'].fillna('Bot')

        return picks_df
    

    def _retrieve_draft_info(self, draft_id: str):
        """Collects the data of teh given draft and assigns it to attributes in this class instance."""
        logger.debug(f"Retrieveing draft information for {self}")
        
        self.draft_json = sleeper_api.get_draft_info(draft_id)
        self.id = self.draft_json.get("draft_id")
        self.type = self.draft_json.get("type")
        self.status = self.draft_json.get("status")
        self.settings = self.draft_json.get("settings")
        self.order = self.draft_json.get("draft_order")
        raw_start_time = self.draft_json.get("start_time")
        if raw_start_time:
            start_time_dt = datetime.fromtimestamp(float(raw_start_time) / 1000)
            self.start_time = start_time_dt
        else:
            logger.warning(f"Start time not set, setting start time to 'None'")
            self.start_time = None
    

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
        


if __name__ == "__main__":
    draft = Draft("1254970326761082880") # Draft ID pulled from Margaritaville 
    logger.info(f"Draft attribute test id: {draft.id}")
    logger.info(f"Draft attribute test type: {draft.type}")
    logger.info(f"Draft attribute test status: {draft.status}")
    logger.info(f"Draft attribute test settings: {draft.settings}")
    logger.info(f"Draft attribute test order: {draft.order}")
    draft.update_picks()