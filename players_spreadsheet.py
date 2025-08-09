import logging
from gspread import Spreadsheet, Worksheet

from sleeper.sleeper_api import get_players
from spreadsheets.gspread_client import get_gspread_client
from spreadsheets.spreadsheet_names import EFantasySpreadsheets
from spreadsheets.spreadsheet_utils import convert_single_level_dict_items_to_row, convert_single_level_dict_to_matrix
from spreadsheets.sheet_manager import SheetManager
from spreadsheets.worksheet_wrapper import WorksheetWrapper

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class PlayersWorksheet(WorksheetWrapper):
    """Google sheets WorksheetWrapper subclass that contains information on current NFL players"""

    DELET_PLAYER_ATTRIBUTES = [
        "hashtag", "sport", "search_last_name", "search_first_name",
        "sportradar_id", "fantasy_data_id", "player_id", "stats_id",
        "espn_id", "rotowire_id", "rotoworld_id", "yahoo_id"
    ]

    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        self.append_row(["foo", "bar"])

        # if self.is_empty():
        #     self.update_players()

        logger.info(f"{self} Initialized")
    

    def update_players(self):
        """Uses the sleeper API to update the information on all the players in the spreadsheet"""
        logger.info(f"Updating player data on {self}")

        players_dict = get_players()
        player_range_list = []

        for player_id in players_dict.keys():
            player_info = players_dict.get(player_id)
            for attribute in self.DELETED_ATTRIBUTES:
                del player_info[attribute]

            player_row = convert_single_level_dict_items_to_row(player_id, player_info)
            player_range_list.append(player_row)
        
        headers = list(player_info.keys())
        headers.insert(0, "player_id")

        player_range_list.insert(0, headers)

        self.append_rows(player_range_list)
    

    def retrieve_player_data(self) -> dict:
        """Retrieves the player data from the players Worksheet and returns it to the sleeper format (minus the DELETED attributes)"""
        logger.info(f"Retrieving NFL player data from {self}")

        player_records = self.get_records()
        players_info_dict = {}

        for player in player_records:
            players_info_dict["player_id"] = player
        
        return players_info_dict



class PlayersSpreadsheet(SheetManager):
    """Google sheet containing data on all the players in the NFL"""
    
    def __init__(self, spreadsheet: Spreadsheet):
        super().__init__(spreadsheet)

        logger.info(f"{self} Initialized")



if __name__ == "__main__":
    client = get_gspread_client()
    player_spreadsheet = PlayersSpreadsheet(client.open(EFantasySpreadsheets.PLAYERS))

    logger.info(f"Testing SheetManager attribtue name: {player_spreadsheet.name}")
    logger.info(f"Testing SheetManager attribtue id: {player_spreadsheet.id}")
    logger.info(f"Testing SheetManager attribtue _cache: {player_spreadsheet._cache}")
    logger.info(f"Testing SheetManager method get_sheet: {player_spreadsheet.get_sheet('Sheet1', PlayersWorksheet)}")
    logger.info(f"Testing SheetManager method create_sheet: {player_spreadsheet.create_sheet('TEST', WorksheetWrapper)}")
    logger.info(f"Testing SheetManager attribtue _cache: {player_spreadsheet._cache}")
    logger.info(f"Testing SheetManager method delete_sheet: {player_spreadsheet.delete_sheet('TEST')}")
    logger.info(f"Testing SheetManager attribtue _cache: {player_spreadsheet._cache}")
    logger.info(f"Testing SheetManager method list_sheet_titles: {player_spreadsheet.list_sheet_titles()}")
    logger.info(f"Testing SheetManager method clear_cache: {player_spreadsheet.clear_cache()}")
    logger.info(f"Testing SheetManager attribtue _cache: {player_spreadsheet._cache}")