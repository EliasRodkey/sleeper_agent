import logging
from pprint import pprint
import pandas as pd

from spreadsheets.gspread_client import get_spreadsheet
from spreadsheets.spreadsheet_names import EFantasySpreadsheets
from spreadsheets.sheet_manager import SheetManager, Spreadsheet
from spreadsheets.draft_spreadsheet.league_settings_worksheet import LeagueSettingsWorksheet
from spreadsheets.draft_spreadsheet.draftboard_worksheet import DraftboardWorksheet
from spreadsheets.draft_spreadsheet.picks_worksheet import PicksWorksheet
from spreadsheets.draft_spreadsheet.member_roster_worksheet import MemberRosterWorksheet

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

        self.players_df = players_df
        self.league = league

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
        draftboard_ws.set_league_and_players(self.league, self.players_df)
    

    def update_draftboard(self, picks: dict):
        """Updates the draftboard with a new pick, removing it from the draftboard worksheet and moving it to the picks worksheet and respective rosters"""
        if not self.picks:
            pass # Initialize
        elif self.picks == picks:
            pass # do nothing
        else:
            pass # update


        



if __name__ == "__main__":
    from spreadsheets.players_spreadsheet.players_spreadsheet import PlayersSpreadsheet
    spreadsheet = get_spreadsheet(EFantasySpreadsheets.PLAYERS)
    players_spreadsheet = PlayersSpreadsheet(spreadsheet)
    players_df = players_spreadsheet.retrieve_player_data()

    league_id, league_info = User("thecondor").retrieve_league_info("Margaritaville")
    league = League(league_id, league_info)
    spreadsheet = get_spreadsheet(EFantasySpreadsheets.TEST)
    draft_sheet = DraftSpreadsheet(spreadsheet, league, players_df)