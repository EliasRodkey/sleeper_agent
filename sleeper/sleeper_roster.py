import logging
import pandas as pd

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class Roster:
    """A teams roster"""

    POSITION_ORDER = ['QB', 'WR', 'RB', 'TE', 'K', 'DEF']

    def __init__(self, roster_obj: dict | pd.DataFrame, player_df: pd.DataFrame):
        if isinstance(roster_obj, dict):
            self.json = roster_obj
            self.raw_df = self.create_roster_from_json(roster_obj, player_df)

        elif isinstance(roster_obj, pd.DataFrame):
            self.json = None
            self.raw_df = roster_obj

        self.df, self.position_count = self._sort_df(self.raw_df)
    

    def create_roster_from_json(self, roster_json: dict, players_df: pd.DataFrame) -> pd.DataFrame:
        """Takes the sleeper roster return and turns it into a dataframe of the teams roster"""
        player_ids = roster_json.get("players")

        # Filter and preserve order using .loc with reindex
        roster_df = players_df.set_index('player_id').loc[player_ids]

        return roster_df.reset_index()


    def _sort_df(self, roster_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Sorts the created roster dataframe by position and creates the position count dataframe.""" 
        # Create a categorical type to enforce custom sort order
        roster_df['position'] = pd.Categorical(roster_df['position'], categories=self.POSITION_ORDER, ordered=True)

        # Sort by position
        roster_df_sorted = roster_df.sort_values('position')

        # Count positions and reindex to enforce order
        position_counts = roster_df_sorted['position'].value_counts().reindex(self.POSITION_ORDER, fill_value=0)

        # Optionally convert to DataFrame
        position_counts_df = position_counts.reset_index()
        position_counts_df.columns = ["position", "count"]

        return roster_df_sorted, position_counts_df

    def __repr__(self):
        return f"{self.__class__.__name__}(owner_id={self.json.get("owner_id")})"