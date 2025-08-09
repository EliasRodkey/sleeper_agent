import logging
from gspread import Worksheet, Spreadsheet

from spreadsheets.worksheet_wrapper import WorksheetWrapper

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class SheetManager:
    def __init__(self, spreadsheet: Spreadsheet):
        self.spreadsheet = spreadsheet
        self.name = self.spreadsheet.title
        self.id = self.spreadsheet.id
        self._cache = {}


    def get_sheet(self, title: str, worksheet_class: WorksheetWrapper) -> Worksheet:
        """Retrieves a single worksheet object and returns it"""
        logger.info(f"Retrieving worksheet {title} from {self}")

        if title not in self._cache:
            ws = self.spreadsheet.worksheet(title)
            self._cache[title] = worksheet_class(ws)
        return self._cache[title]
    

    def create_sheet(self, new_title: str, worksheet_class: WorksheetWrapper, rows: int=100, cols: int=26) -> Worksheet:
        """Creates a new worksheet and adds it to the _cache"""
        logger.info(f"Creating a new Worksheet {new_title} in {self}")

        if new_title in self._cache.keys():
            logger.warning(f"Unable to create Worksheet {new_title}, already exists in {self}")
            return 

        else:
            ws = self.spreadsheet.add_worksheet(new_title, rows, cols)
            self._cache[new_title] = worksheet_class(ws)
        
        return self._cache[new_title]
    

    def delete_sheet(self, title: str):
        """Deletes a worksheet from the google spreadsheet"""
        logger.info(f"Deleting worksheet {title} from {self}")
        ws_wrapper = self._cache.pop(title)
        self.spreadsheet.del_worksheet(ws_wrapper.ws)


    def list_sheet_titles(self) -> list:
        """Returns a list of the sheet titles in the spreadsheet"""
        return [ws.title for ws in self.spreadsheet.worksheets()]


    def clear_cache(self):
        """Clears the _cache attribute of the SpreadsheetManager"""
        logger.info(f"Clearing the cache for spreadsheet {self}")
        self._cache.clear()
        
    
    def clear_spreadsheet(self):
        """Clears all of the worksheets in the SpreadsheetManager"""
        logger.info(f"Clearing the contents of the Worksheets in {self}")

        for ws in self._cache.values():
            ws.clear()

    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.id})"
