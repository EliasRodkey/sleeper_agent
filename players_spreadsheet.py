import datetime
import logging
from gspread import Spreadsheet, Worksheet
import pandas as pd

from sleeper.sleeper_api import get_players
from spreadsheets.gspread_client import get_spreadsheet
from spreadsheets.spreadsheet_names import EFantasySpreadsheets
from spreadsheets.sheet_manager import SheetManager
from spreadsheets.worksheet_wrapper import WorksheetWrapper

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

        # Fill nulls
        for col in players_df.columns:
            players_df[col] = players_df[col].astype(str).fillna(default_val)


        return players_df    



class UpdateLogWorksheet(WorksheetWrapper):
    """Google sheet WorksheetWrapper subclass that represents a store of the upload log"""

    HEADERS = ["datetime_stamp", "upload_description"]

    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet)

        if self.is_empty() or not self.retrieve_headers():
            self.write_cell_range([self.HEADERS])

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
    

    def update_player_data(self, update_description: str):
        """Updates the player data in the player_data worksheet and posts a time log"""
        update = self.check_update_required()

        if update:
            player_ws = self.get_sheet(self.PLAYER_DATA)
            player_ws.update_players()

            logs_ws = self.get_sheet(self.UPDATE_LOGS)
            logs_ws.post_log(description=update_description)
        
        else:
            logger.info(f"Player data updated within 1 day, skipping update.")
    

    def check_update_required(self) -> bool:
        """Checks the update_logs sheet to see if the last player update was within the last 24 hours"""
        logs_ws = self.get_sheet(self.UPDATE_LOGS)
        last_log = logs_ws.retrieve_last_log()

        last_log_datetime_str = last_log["datetime_stamp"]
        last_log_datetime_obj = datetime.datetime.strptime(last_log_datetime_str, "%Y-%m-%d %H:%M:%S")

        return last_log_datetime_obj.date() < datetime.datetime.now().date()


    def retrieve_player_data(self) -> pd.DataFrame:
        """Retrieves the all of the player data from the spreadsheet and returns it as a pd.Dataframe"""
        logger.info(f"Retrieving player data from {self}")
        player_data_ws = self.get_sheet(self.PLAYER_DATA)
        return player_data_ws.read_dataframe()



if __name__ == "__main__":
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