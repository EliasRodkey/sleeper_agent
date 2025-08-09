import logging
from gspread import Worksheet

from spreadsheets.spreadsheet_utils import build_range

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class WorksheetWrapper:
    """A wrapper class for a gspread Worksheet that contains functions used across multiple worksheet classes"""
    def __init__(self, worksheet: Worksheet):
        self.ws = worksheet
        self.name = self.ws.title
        self.id = self.ws.id


    def write_cell_range(self, values: list[list], start_cell: str):
        """Write a data in a matrix format to a given cell range"""
        cell_range = build_range(start_cell, len(values), len(values[0]))
        self.ws.update(values, cell_range)
        print('heyoooo')


    def get_list_matrix(self) -> list[list]:
        """Returns a 2d matrix of all the cells containing values on the worksheet"""
        return self.ws.get_all_values()
    

    def get_records(self) -> list[dict]:
        """Returns a list of dictionaries of the rows with the headers as keys"""
        return self.ws.get_all_records()


    def append_row(self, row: list):
        """Add a row to the spreadsheet"""
        self.ws.append_row(row)
    

    def append_rows(self, rows: list[list]):
        """Adds multiple rows to the spreadsheet"""
        self.ws.append_rows(rows)
    

    def is_empty(self) -> bool:
        """Checks to see if the Worksheet is empty (No cells with values)"""
        return not self.ws.get_all_values()


    def clear(self):
        """Clears all cells in the current worksheet """
        logger.info(f"Clearing all values from {self}")
        self.ws.clear()
    

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.id})"