import logging
from pprint import pprint

from spreadsheets.gspread_client import get_spreadsheet
from spreadsheets.spreadsheet_names import EFantasySpreadsheets
from spreadsheets.spreadsheet_utils import convert_single_level_dict_to_matrix, build_range
from spreadsheets.sheet_manager import SheetManager, Spreadsheet
from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet


from sleeper.sleeper_draft import Draft
from sleeper.sleeper_league import League
from sleeper.sleeper_user import User

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class LeagueSettingsWorksheet(WorksheetWrapper):
    """Worksheet that stores and displays the league settings / draft settings"""
    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        logger.info(f"Initialized {self}")
    

    def set_league(self, league: League):
        """Adds the league to the worksheet and updates the worksheet with the league settings, always call before update_settings"""
        logger.info(f"Setting .league attribtue for {self} to {league}")
        self.league = league
        self.update_settings()


    def update_settings(self):
        """Updates the league settings with the current set league. ALWAYS CALL set_league FIRST"""
        logger.info(f"Updating league settings in {self}")
        self.clear()
        self.add_league_name()
        self.add_league_settings()
        self.add_scoring_settings()
        self.add_draft_settings()


    def add_league_name(self):
        """Adds the name and ID for the league to the settings spreadsheet"""
        logger.info(f"Adding league name and ID to {self}")
        name_range = convert_single_level_dict_to_matrix(
            {
                "League_Name" : self.league.name,
                "League_ID" : self.league.id,
                "" : ""
            }
        )
        self.write_cell_range(name_range)


    def add_league_settings(self):
        """Adds the settings for the league into the worksheet minus any settings that are NA for our league"""
        logger.info(f"Adding league settings to {self}")
        revised_settings = self.remove_unused_settings(self.league.league_settings)
        settings_range = convert_single_level_dict_to_matrix(revised_settings)
        self.write_cell_range(settings_range, "A4")
    

    def add_scoring_settings(self):
        """Adds the scoring settings to the league settings worksheet"""
        logger.info(f"Adding scoring settings to {self}")
        revised_settings = self.remove_unused_settings(self.league.scoring_settings)
        settings_range = convert_single_level_dict_to_matrix(revised_settings)
        self.write_cell_range(settings_range, "D4")

    
    def add_draft_settings(self):
        """Adds the draft settings to the league settings worksheet"""
        logger.info(f"Adding draft settings to {self}")
        settings_range = convert_single_level_dict_to_matrix(self.league.draft.settings)
        self.write_cell_range(settings_range, "G4")
    

    def remove_unused_settings(self, raw_settings: dict) -> dict:
        """Removes any settings that are set to 0 (unused) from the raw settings json"""
        revised_settings = raw_settings.copy()
        for key, value in raw_settings.items():
            if value == 0:
                del revised_settings[key]     
        
        return revised_settings



class DraftBoardWorksheet(WorksheetWrapper):
    """Contains the live draftboard for the current league draft"""
    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        logger.info(f"Initialized {self}")
    

    def set_league(self, league: League):
        """Adds the league to the spreadsheet and updates the worksheet with the league settings, always call before update_draftboard"""
        logger.info(f"Setting .league attribtue for {self} to {league}")
        self.league = league
        self.update_draftboard()
    

    def update_draftboard(self):
        """"""
        pass


class PicksWorksheet(WorksheetWrapper):
    """Contains the live picks for the current league draft"""
    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        logger.info(f"Initialized {self}")
    

    def set_league(self, league: League):
        """Adds the league to the worksheet and updates the worksheet with the current picks, always call before update_picks"""
        logger.info(f"Setting .league attribtue for {self} to {league}")
        self.league = league
        self.update_draftboard()
    

    def update_picks(self):
        """"""
        pass



class MemberRosterWorksheet(WorksheetWrapper):
     """Contains the live picks and roster for the members of the current league draft"""
     def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        logger.info(f"Initialized {self}")


     def set_league(self, league: League):
        """Adds the league to the worksheet and updates the worksheet with the current memeber roster, always call before update_roster"""
        logger.info(f"Setting .league attribtue for {self} to {league}")
        self.league = league
        self.update_roster()
    

     def update_roster(self):
         """"""
         pass

    


class DraftSpreadsheet(SheetManager):
    """A representation of the draft spreadsheet"""

    LEAGUE_SETTINGS = "league_settings"
    DRAFTBOARD = "draftboard"
    PICKS = "picks"

    def __init__(self, spreadsheet: Spreadsheet, league: League):
        super().__init__(spreadsheet)

        self.league = league

        # if self.is_empty():
        self.initialize_spreadsheet()
        # else:
        #     self.get_sheet(self.LEAGUE_SETTINGS, LeagueSettingsWorksheet)

        logger.info(f"Initialized {self}")
    

    def initialize_spreadsheet(self):
        """If the spreadsheet is empty, it get initialized with the correct worksheet titles and information"""
        logger.info(f"Initializing {self}...")
        self.create_settings_worksheet()
        self.create_draftboard_worksheet()
    

    def create_settings_worksheet(self):
        """Creates the league settings worksheet inside of the draft spreadsheet"""
        logger.info(f"Creating new league settings worksheet")
        settings_ws = self.get_sheet("Sheet1", LeagueSettingsWorksheet)
        self.rename_sheet(self.LEAGUE_SETTINGS)
        settings_ws.set_league(self.league)
    

    def create_draftboard_worksheet(self):
        """Creates the draftboard worksheet inside of the draft spreadsheet"""
        pass
        



if __name__ == "__main__":
    league_id, league_info = User("thecondor").retrieve_league_info("Margaritaville")
    league = League(league_id, league_info)
    spreadsheet = get_spreadsheet(EFantasySpreadsheets.TEST)
    draft_sheet = DraftSpreadsheet(spreadsheet, league)