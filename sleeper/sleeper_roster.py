import logging
import pandas as pd

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class Roster:
    """A teams roster"""

    POSITION_ORDER = ['QB', 'WR', 'RB', 'TE', 'K', 'DEF']

    def __init__(self, roster_json: dict, player_df: pd.DataFrame):
        self.json = roster_json
        self.owner_id = self.json.get("owner_id")
        self.league_id = self.json.get("league_id")
        self.df, self.position_counts = self.create_roster_df(player_df)
    

    def create_roster_df(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Takes the sleeper roster return and turns it into a dataframe of the teams roster"""
        player_ids = self.json.get("players")

        # Filter and preserve order using .loc with reindex
        roster_df = players_df.set_index('player_id').loc[player_ids].reset_index()

        # Create a categorical type to enforce custom sort order
        roster_df['position'] = pd.Categorical(roster_df['position'], categories=self.POSITION_ORDER, ordered=True)

        # Sort by position
        roster_df_sorted = roster_df.sort_values('position').reset_index(drop=True)

        # Count positions and reindex to enforce order
        position_counts = roster_df_sorted['position'].value_counts().reindex(self.POSITION_ORDER, fill_value=0)

        # Optionally convert to DataFrame
        position_counts_df = position_counts.reset_index()
        position_counts_df.columns = ['position', 'count']

        return roster_df, position_counts




    def __repr__(self):
        return f"{self.__class__.__name__}(owner_id={self.json.get("owner_id")})"