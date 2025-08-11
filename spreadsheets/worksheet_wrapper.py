import logging
from gspread import Worksheet
import pandas as pd
from gspread_dataframe import set_with_dataframe, get_as_dataframe


from spreadsheets.spreadsheet_utils import build_range

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class WorksheetWrapper:
    """A wrapper class for a gspread Worksheet that contains functions used across multiple worksheet classes"""
    def __init__(self, worksheet: Worksheet):
        self.ws = worksheet
        self.name = self.ws.title
        self.id = self.ws.id
    

    def retrieve_headers(self) -> list[str]:
        """Collecting the headers currently on the players data worksheet"""
        logger.info(f"Retrieving current headers on {self}")
        current_headers = self.get_list_matrix()
        return current_headers[0] if current_headers else None


    def write_cell_range(self, values: list[list], start_cell: str="A1"):
        """Write a data in a matrix format to a given cell range"""
        cell_range = build_range(start_cell, len(values), len(values[0]))
        self.ws.update(values, cell_range)

    
    def write_dataframe(self, df: pd.DataFrame, clear: bool = True, include_index: bool = False):
        """
        Writes a pandas DataFrame to the worksheet.
        Parameters:
            df (pd.DataFrame): The DataFrame to write.
            clear (bool): Whether to clear the sheet before writing.
            include_index (bool): Whether to include the DataFrame index.
        """
        if df.empty:
            print("Warning: DataFrame is empty. Skipping sheet update.")
            return

        if clear:
            self.ws.clear()
        set_with_dataframe(self.ws, df, include_index=include_index)


    def read_dataframe(self, evaluate_formulas: bool = False, header_row: int = 1) -> pd.DataFrame:
        """
        Reads the worksheet into a pandas DataFrame.
        Parameters:
            evaluate_formulas (bool): Whether to evaluate formulas or return raw values.
            header_row (int): Row number to treat as header (1-indexed).
        Returns:
            pd.DataFrame: The sheet contents as a DataFrame.
        """
        df = get_as_dataframe(self.ws, evaluate_formulas=evaluate_formulas, header=header_row - 1)
        return df


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
        return True if self.ws.get_all_values() == [[]] else False


    def clear(self):
        """Clears all cells in the current worksheet """
        logger.info(f"Clearing all values from {self}")
        self.ws.clear()
    

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, {self.id})"