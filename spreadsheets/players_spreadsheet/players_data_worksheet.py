import logging
import pandas as pd

from sleeper.sleeper_api import get_players
from spreadsheets.spreadsheet_utils import normalize_name
from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class PlayersDataWorksheet(WorksheetWrapper):
    """Google sheets WorksheetWrapper subclass that contains information on current NFL players"""
    
    DELETED_ATTRIBUTUES = ["metadata", "competitions", "player_id", "injury_notes", "sport"]

    FANTASY_PLAYER_POSITIONS = ["WR", "RB", "QB", "TE", "K", "DEF"]

    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        if self.is_empty():
            logger.error(f"Worksheet not empty! we have a problem {self.is_empty()}")
            self.update_players()

        logger.info(f"{self} Initialized")


    def update_players(self, default_val: str="N/A"):
        """Uses the sleeper API to update the information on all the players in the spreadsheet"""
        logger.info(f"Updating player data on {self}")

        players_df = pd.DataFrame.from_dict(get_players())
        clean_players_df = self.clean_df(players_df, default_val=default_val)

        # clean_players_df.to_excel("players_df_output.xlsx", index=False)
        self.write_dataframe(clean_players_df, clear=True, include_index=True)


    def clean_df(self, players_df: pd.DataFrame, default_val: str="N/A") -> pd.DataFrame:
        """Cleans the raw player dataframe by removing extra columns and replacing null / unnacceptable value types"""
        logger.info(f"Cleaning player info Dataframe for worksheet upload")

        players_df = players_df.T
        players_df.set_index("player_id", inplace=True)

        players_df.dropna(axis=1, how="all", inplace=True)
        players_df.drop(columns=self.DELETED_ATTRIBUTUES, errors="ignore", inplace=True)

        # Remove players with no offensive fantasy position
        players_df = players_df[
            players_df["fantasy_positions"].apply(
                lambda x: isinstance(x, list) and any(pos in x for pos in self.FANTASY_PLAYER_POSITIONS)
            )
        ]

        # Convert fnatasy_positions to string
        players_df["fantasy_positions"] = players_df["fantasy_positions"].apply(lambda x: ", ".join(x) if isinstance(x, list) else default_val)

        # Remove duplicate and inactive players
        players_df = players_df[
            ~players_df["full_name"].isin(["Duplicate Player", "TreVeyon Henderson DUPLICATE"])
        ]
        players_df = players_df[~((players_df["active"] == False))]

        # Add defense abbreviation to full_name column
        players_df.loc[players_df['position'] == 'DEF', 'full_name'] = players_df.loc[players_df['position'] == 'DEF', 'team'] + ' Defense'

        players_df['normalized_name'] = players_df['full_name'].apply(normalize_name)

        # Fill nulls
        for col in players_df.columns:
            players_df[col] = players_df[col].astype(str).fillna(default_val)

        return players_df