import datetime
import logging
from gspread import Spreadsheet
import pandas as pd

from spreadsheets.sheet_manager import SheetManager
from spreadsheets.players_spreadsheet.players_data_worksheet import PlayersDataWorksheet
from spreadsheets.players_spreadsheet.update_log_worksheet import UpdateLogWorksheet

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)   



class PlayersSpreadsheet(SheetManager):
    """Google sheet containing data on all the players in the NFL"""

    UPDATE_LOGS = "update_logs"
    PLAYER_DATA = "player_data"
    
    def __init__(self, spreadsheet: Spreadsheet):
        super().__init__(spreadsheet)

        if self.is_empty():
            self.initialize_spreadsheet()
        
        else:
            self.get_sheet(self.UPDATE_LOGS, UpdateLogWorksheet)
            self.get_sheet(self.PLAYER_DATA, PlayersDataWorksheet)

        logger.info(f"{self} Initialized")
    

    def initialize_spreadsheet(self):
        """If the spreadsheet is empty, it get initialized with the correct worksheet titles and information"""
        logger.info(f"Initializing {self}...")
        log_ws = self.create_log_worksheet()
        self.create_player_data_worksheet()
        log_ws.post_log("spreadsheet initialized")
    

    def create_log_worksheet(self):
        """Creates the log post worksheet"""
        logger.info(f"Creating new post log worksheet")
        return self.create_sheet(self.UPDATE_LOGS, UpdateLogWorksheet, cols=len(UpdateLogWorksheet.HEADERS))
    

    def create_player_data_worksheet(self):
        """Creates the lof post worksheet"""
        logger.info(f"Creating new player data worksheet")
        self.get_sheet("Sheet1", PlayersDataWorksheet)
        self.rename_sheet(self.PLAYER_DATA)
    

    def update_player_data(self, update_description: str, force: bool=False):
        """Updates the player data in the player_data worksheet and posts a time log"""
        update = self.check_update_required()
        
        if update or force:
            player_ws = self._cache[self.PLAYER_DATA]
            player_ws.update_players()

            logs_ws = self._cache[self.UPDATE_LOGS]
            logs_ws.post_log(description=update_description)
        
        else:
            logger.info(f"Player data updated within 1 day, skipping update.")
    

    def check_update_required(self) -> bool:
        """Checks the update_logs sheet to see if the last player update was within the last 24 hours"""
        logs_ws = self._cache[self.UPDATE_LOGS]
        last_log = logs_ws.retrieve_last_log()

        last_log_datetime_str = last_log["datetime_stamp"]
        last_log_datetime_obj = datetime.datetime.strptime(last_log_datetime_str, "%Y-%m-%d %H:%M:%S")

        return last_log_datetime_obj.date() < datetime.datetime.now().date()


    def retrieve_player_data(self) -> pd.DataFrame:
        """Retrieves the all of the player data from the spreadsheet and returns it as a pd.Dataframe"""
        logger.info(f"Retrieving player data from {self}")
        player_data_ws = self.get_sheet(self.PLAYER_DATA, PlayersDataWorksheet)
        return player_data_ws.read_dataframe()



if __name__ == "__main__":
    from spreadsheets.gspread_client import get_spreadsheet
    from spreadsheets.spreadsheet_names import EFantasySpreadsheets

    spreadsheet = get_spreadsheet(EFantasySpreadsheets.PLAYERS)
    player_spreadsheet = PlayersSpreadsheet(spreadsheet)

    # player_spreadsheet.update_player_data(update_description="Test Sheet Update")

    # print(player_spreadsheet.retrieve_player_data())

    # player_spreadsheet.clear_spreadsheet()

    # logger.info(f"Testing SheetManager attribtue name: {player_spreadsheet.name}")
    # logger.info(f"Testing SheetManager attribtue id: {player_spreadsheet.id}")
    # logger.info(f"Testing SheetManager attribtue _cache: {player_spreadsheet._cache}")
    # logger.info(f"Testing SheetManager method get_sheet: {player_spreadsheet.get_sheet('Sheet1', PlayersDataWorksheet)}")
    # logger.info(f"Testing SheetManager method create_sheet: {player_spreadsheet.create_sheet('TEST', WorksheetWrapper)}")
    # logger.info(f"Testing SheetManager attribtue _cache: {player_spreadsheet._cache}")
    # logger.info(f"Testing SheetManager method delete_sheet: {player_spreadsheet.delete_sheet('TEST')}")
    # logger.info(f"Testing SheetManager attribtue _cache: {player_spreadsheet._cache}")
    # logger.info(f"Testing SheetManager method list_sheet_titles: {player_spreadsheet.list_sheet_titles()}")
    # logger.info(f"Testing SheetManager method clear_cache: {player_spreadsheet.clear_cache()}")
    # logger.info(f"Testing SheetManager attribtue _cache: {player_spreadsheet._cache}")