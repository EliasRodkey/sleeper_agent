import logging

from spreadsheets.gspread_client import SpreadsheetAPI, Spreadsheet
from spreadsheets.spreadsheet_names import EFantasyDraftSpreadsheets, ELeagueNames

from sleeper.sleeper_draft import SleeperDraft

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class DraftSpreadsheet(SleeperDraft):
    """A representation of the draft spreadsheet"""
    def __init__(self, username: str, league_name: str, spreadsheet: Spreadsheet):
        super().__init__(username, league_name)
        self.league_id = self.league_info['league_id']
        
        self.spreadsheet = spreadsheet
        self.clear_spreadsheet(self.spreadsheet)

        self.settings_worksheet = self.add_league_settings()
        self.draft_board_worksheet = str

        logger.info(f"Initialized {self}")


    def add_league_settings(self):
        """
        Renames the default sheet1 to league_settings.
        Adds the settings from the given league_name to
        """
        logger.info(f"Adding league settings for {self.league_name} to {self.spreadsheet_name} 'league_settings'.")
        settings_worksheet = self.spreadsheet.sheet1
        settings_worksheet.update_title('league_settings')

        league_settings = self._compile_league_info()

        # self.spreadsheet.update()

    
    def _compile_league_info(self):
        pass
    

    def __repr__(self):
        return f"DraftSpreadsheet({self.user}, {self.league_name}, {self.spreadsheet_name})"
        



if __name__ == "__main__":
    draft = DraftSpreadsheet("TheCondor", ELeagueNames.MARGARITAVILLE, EFantasyDraftSpreadsheets.TEST)

    draft.add_league_settings()