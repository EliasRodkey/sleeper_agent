import logging
import pandas as pd
import re

from spreadsheets.sheet_manager import SheetManager, Spreadsheet
from spreadsheets.draft_spreadsheet.league_settings_worksheet import LeagueSettingsWorksheet
from spreadsheets.draft_spreadsheet.draftboard_worksheet import DraftboardWorksheet
from spreadsheets.draft_spreadsheet.picks_worksheet import PicksWorksheet
from spreadsheets.draft_spreadsheet.member_roster_worksheet import MemberRosterWorksheet

from sleeper.ffcalc_api import get_half_ppr_adp_df, get_rookie_adp_df
from sleeper.sleeper_api import get_draft_picks
from sleeper.sleeper_league import League
from sleeper.sleeper_user import User

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
    


class DraftSpreadsheet(SheetManager):
    """A representation of the draft spreadsheet"""

    LEAGUE_SETTINGS = "league_settings"
    DRAFTBOARD = "draftboard"
    PICKS = "picks"

    def __init__(self, spreadsheet: Spreadsheet, league: League, players_df: pd.DataFrame):
        super().__init__(spreadsheet)

        self.league = league
        self.players_df = self.sort_by_adp(players_df)

        # if self.is_empty():
        self.initialize_spreadsheet()
        # else:
        #     self.get_sheet(self.LEAGUE_SETTINGS, LeagueSettingsWorksheet)

        logger.info(f"Initialized {self}")
    

    def initialize_spreadsheet(self):
        """If the spreadsheet is empty, it get initialized with the correct worksheet titles and information"""
        logger.info(f"Initializing {self}...")
        # self.create_settings_worksheet()
        self.create_draftboard_worksheet()
    

    def create_settings_worksheet(self):
        """Creates the league settings worksheet inside of the draft spreadsheet"""
        logger.info(f"Creating new league settings worksheet")
        settings_ws = self.get_sheet("Sheet1", LeagueSettingsWorksheet)
        self.rename_sheet(self.LEAGUE_SETTINGS)
        settings_ws.set_league(self.league)
    

    def create_draftboard_worksheet(self):
        """Creates the draftboard worksheet inside of the draft spreadsheet"""
        logger.info(f"Creating new draftboard worksheet")
        draftboard_ws = self.create_sheet(self.DRAFTBOARD, DraftboardWorksheet)
        draftboard_ws.update_draftboard(self.players_df)
    

    def update_draftboard(self, picks: dict):
        """Updates the draftboard with a new pick, removing it from the draftboard worksheet and moving it to the picks worksheet and respective rosters"""
        if not self.picks:
            pass # Initialize
        elif self.picks == picks:
            pass # do nothing
        else:
            pass # update
    

    def sort_by_adp(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sorts the players dataframe by ADP gathered from FantasyFootballCalculator.com API"""
        logger.info(f"Sorting players dataframe by ADP")
        if self.league.redraft:
            adp_df = get_half_ppr_adp_df()
        
        else:
            adp_df = get_rookie_adp_df()

        adp_df = adp_df[adp_df['full_name'].notna()]
        adp_df.loc[adp_df['position_x'] == 'DEF', 'full_name'] = adp_df.loc[adp_df['position_x'] == 'DEF', 'team_x'] + ' Defense'
        df['normalized_name'] = df['full_name'].apply(self.normalize_name)
        adp_df['normalized_name'] = adp_df['full_name'].apply(self.normalize_name)

        merged_df = pd.merge(df, adp_df[['normalized_name', 'adp']], on='normalized_name', how='left')

        max_adp = adp_df['adp'].max()
        merged_df['adp'] = merged_df['adp'].fillna(max_adp + 1)

        return merged_df.sort_values('adp')


    def normalize_name(self, name: str):
        """Normalized the names of plaeyrs to match accross datasets"""
        if not isinstance(name, str):
            name = ""
        name = name.lower().strip()
        # Remove common suffixes
        name = re.sub(r'\b(jr\.?|sr\.?|ii|iii|iv|v)\b', '', name)
        # Remove punctuation and extra whitespace
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip()