import logging

from sleeper.sleeper_league import League
from spreadsheets.spreadsheet_utils import convert_single_level_dict_to_matrix
from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet


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