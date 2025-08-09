import logging
from string import ascii_uppercase as alphabet
from gspread.utils import rowcol_to_a1, a1_to_rowcol


logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_single_level_dict_to_matrix(dictionnary: dict) -> list[list]:
    """
    Takes a dictionary with only one level (each key has a discreet value not another dict or list) and 
    formats it into a list of lists list[key, value]
    """
    logger.debug(f"Converting dictionary to layered list.")

    layered_list = []
    for key, value in dictionnary.items():
        list.append([key, value])
    
    return layered_list


def convert_single_level_dict_items_to_row(unique_id: int, dictionnary: dict) -> list:
    """
    Takes a dictionary with only one level (each key has a discreet value not another dict or list) and 
    formats into a list where the list has a unique identifier at the beginning and the items of the dict as values after that
    """
    logger.debug(f"Converting dictionary to item row list.")

    row_list = [item for item in dictionnary.items()]
    row_list.insert(0, unique_id)

    return row_list


def build_range(start_cell: str, num_rows: int, num_cols: int):
    """Creates a range string using a starting cell and the size of data"""
    logger.debug(f"Building cell range string from start cell {start_cell}, rows: {num_rows}, cols: {num_cols}")

    start_row, start_col = a1_to_rowcol(start_cell)
    end_row = start_row + num_rows - 1
    end_col = start_col + num_cols - 1
    end_cell = rowcol_to_a1(end_row, end_col)

    return f"{start_cell}:{end_cell}"


def sanitize_matrix(matrix: list[list], default_val: str="N/A"):
    """Replaces all null values with default value in a matrix"""
    return [
        [cell if cell is not None else default_val for cell in row]
        for row in matrix
    ]
