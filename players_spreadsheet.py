import datetime
import logging
from gspread import Spreadsheet, Worksheet
from pprint import pprint

from sleeper.sleeper_api import get_players
from spreadsheets.gspread_client import get_spreadsheet
from spreadsheets.spreadsheet_names import EFantasySpreadsheets
from spreadsheets.spreadsheet_utils import convert_single_level_dict_items_to_row, sanitize_matrix
from spreadsheets.sheet_manager import SheetManager
from spreadsheets.worksheet_wrapper import WorksheetWrapper

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class PlayersDataWorksheet(WorksheetWrapper):
    """Google sheets WorksheetWrapper subclass that contains information on current NFL players"""
    ALL_PlAYER_ATTRIBUTES = [
        "hashtag", "depth_chart_position", "status", "sport",
        "fantasy_positions", "number", "search_last_name",
        "injury_start_date", "weight", "position",
        "practice_participation", "sportradar_id", "team",
        "last_name", "college", "fantasy_data_id", "injury_status",
        "player_id", "height", "search_full_name", "age", "stats_id",
        "birth_country", "espn_id", "search_rank", "first_name",
        "depth_chart_order", "years_exp", "rotowire_id", "rotoworld_id",
        "search_first_name", "yahoo_id"
    ]
    DELETED_ATTRIBUTES = [
        "hashtag", "sport", "search_last_name", "search_first_name",
        "sportradar_id", "fantasy_data_id", "player_id", "stats_id",
        "espn_id", "rotowire_id", "rotoworld_id", "yahoo_id"
    ]

    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        self.append_row(["foo", "bar"])

        if self.is_empty() or self.requires_update():
            self.update_worksheet()

        logger.info(f"{self} Initialized")


    def update_worksheet(self):
        """Updates the current worksheet by clearing it, adding headers, then adding players"""
        logger.info(f"Refreshing {self} with updated values")
        self.clear()
        self.add_headers()
        self.update_players()


    def update_players(self):
        """Uses the sleeper API to update the information on all the players in the spreadsheet"""
        logger.info(f"Updating player data on {self}")

        players_dict = get_players()
        player_matrix = []

        for player_id in players_dict.keys():
            player_info = players_dict.get(player_id)
            pprint(player_info)
            
            for attribute in self.DELETED_ATTRIBUTES:
                try:
                    del player_info[attribute]
                except KeyError as e:
                    logger.warning(f"Player {player_info['first_name']} {player_info['last_name']} has to attribute: {attribute}, skipping deletion")
            
            player_row = convert_single_level_dict_items_to_row(player_id, player_info)

            if not player_info.keys() == self.headers:
                for i, attribute in enumerate(self.headers):
                    if attribute not in player_info.keys():
                        player_row.insert(i, "N/A")
            
            player_matrix.append(player_row)


        sanitized_player_matrix = sanitize_matrix(player_matrix)
        pprint(sanitized_player_matrix)
        self.append_rows(sanitized_player_matrix)
    

    def retrieve_player_data(self) -> dict:
        """Retrieves the player data from the players Worksheet and returns it to the sleeper format (minus the DELETED attributes)"""
        logger.info(f"Retrieving NFL player data from {self}")

        player_records = self.get_records()
        players_info_dict = {}

        for player in player_records:
            players_info_dict["player_id"] = player
        
        return players_info_dict


    def retrieve_headers(self) -> list[str]:
        """Collecting the headers currently on the players data worksheet"""
        logger.info(f"Retrieving current headers on {self}")
        return self.get_list_matrix()[0]


    def add_headers(self):
        """Adds the data headers to the players data worksheet"""
        logger.info(f"Adding headers {self.headers} to {self}")
        self.append_row(self.headers)


    @property
    def headers(self):
        headers = []
        for header in self.ALL_PlAYER_ATTRIBUTES:
            if header not in self.DELETED_ATTRIBUTES:
                headers.append(header)
        headers.insert(0, "player_id")
        return headers
    

    def requires_update(self):
        """Checks to see if the headers in the current worksheet match the headers in the PlayersDataWorksheet wrapper"""
        logger.info(f"Checking if update needed for {self} headers")
        return not self.retrieve_headers() == self.headers



class UpdateLogWorksheet(WorksheetWrapper):
    """Google sheet WorksheetWrapper subclass that represents a store of the upload log"""

    HEADERS = ["datetime_stamp", "upload_description"]

    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        if self.is_empty():
            self.append_row(self.HEADERS)

        logger.info(f"{self} Initialized")
    

    def post_log(self, description: str):
        """Posts the date that an upload occured showing how up to date the data is"""
        logger.info(f"Posting log for player upload to {self}")
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")

        self.append_row([formatted_date, description])


    def retrieve_logs(self):
        """Retrieves the post log data"""
        logger.info(f"Retrieving the post logs for {self}")
        return self.get_records()


    def retrieve_last_log(self):
        """Retrieves the last postes log"""
        logger.info("Retrieveing the last posted log for {self}")
        return self.get_records()[-1]



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

    

    @property
    def update_log_ws(self):
        return self._cache("update_logs")



if __name__ == "__main__":
    spreadsheet = get_spreadsheet(EFantasySpreadsheets.PLAYERS)
    player_spreadsheet = PlayersSpreadsheet(spreadsheet)

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