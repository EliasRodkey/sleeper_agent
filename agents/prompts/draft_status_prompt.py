import logging
import pandas as pd

from agents.prompts.prompt_builder import PromptBuilder

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class DraftStatusPrompt(PromptBuilder):
    def __init__(self, current_roster: pd.DataFrame, 
                 position_count: pd.DataFrame, 
                 draft_picks: pd.DataFrame, 
                 remaining_players: pd.DataFrame):
        super().__init__()
        self.current_roster = current_roster
        self.position_count = position_count
        self.draft_picks = draft_picks
        self.remaining_players = remaining_players
    

    def summarize_current_roster(self) -> str:
        """Takes the current roster provided and creates a summary to add to the prompt"""
        logger.info(f"Condensing current roster into prompt component")
        return self.current_roster.groupby('position', observed=True)['full_name'].apply(list).to_dict()
    

    def get_top_available_by_adp(self, position=None, n=10):
        """
        Returns top available players filtered by position and tier, sorted byra_tier_ranking.

        Parameters:
        - df: DataFrame with columns ['name', 'position', 'tier', 'intra_tier_ranking', ...]
        - position: str or list of positions to filter (e.g., 'WR' or ['WR', 'RB'])
        - tier_max: int, max tier to include (e.g., Tier 3 and better)
        - n: int, number of players to return

        Returns:
        - DataFrame of top available players
        """
        df_filtered = self.remaining_players.copy()

        if position:
            if isinstance(position, str):
                df_filtered = df_filtered[df_filtered['position'] == position]
            elif isinstance(position, list):
                df_filtered = df_filtered[df_filtered['position'].isin(position)]

        df_filtered = df_filtered[df_filtered['adp'] != df_filtered['adp'].max()]
        df_sorted = df_filtered.sort_values(by='adp', ascending=True)

        return df_sorted.head(n)
    

    def get_top_available_by_tier(self, position=None, tier_max=3, n=10):
        """
        Returns top available players filtered by position and tier, sorted by intra_tier_ranking.

        Parameters:
        - df: DataFrame with columns ['name', 'position', 'tier', 'intra_tier_ranking', ...]
        - position: str or list of positions to filter (e.g., 'WR' or ['WR', 'RB'])
        - tier_max: int, max tier to include (e.g., Tier 3 and better)
        - n: int, number of players to return

        Returns:
        - DataFrame of top available players
        """
        df_filtered = self.remaining_players.copy()

        if position:
            if isinstance(position, str):
                df_filtered = df_filtered[df_filtered['position'] == position]
            elif isinstance(position, list):
                df_filtered = df_filtered[df_filtered['position'].isin(position)]

        df_filtered = df_filtered[df_filtered['tier'] <= tier_max]
        df_sorted = df_filtered.sort_values(by=['tier', 'intra_tier_ranking'], ascending=[True, True])

        return df_sorted.head(n)


    def summarize_recent_picks(self, n=10):
        """Summarizes the most recent picks made in the draft"""
        recent = self.draft_picks.tail(n)
        return recent['position'].value_counts().to_dict()
    

    def detect_scarcity(self, positions, tier_cutoff=6):
        """
        Returns the number of remaining players at the given positions and tier or better.
        
        Parameters:
        - positions: list of positions (e.g., ['WR', 'RB'])
        - tier_cutoff: int, max tier to include
        
        Returns:
        - int: count of remaining players matching criteria
        """
        df = self.remaining_players
        filtered = df[df['position'].isin(positions) & (df['tier'] <= tier_cutoff)]
        return len(filtered)