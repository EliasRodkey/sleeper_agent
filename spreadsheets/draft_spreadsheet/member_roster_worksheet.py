import logging
import pandas as pd

from sleeper.sleeper_user import User
from spreadsheets.spreadsheet_utils import convert_single_level_dict_to_matrix
from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class MemberRosterWorksheet(WorksheetWrapper):
   """Contains the live picks and roster for the members of the current league draft"""

   HEADERS = ["pick_no", "picked_by", "draft_slot", "full_name", "adp", "team", "fantasy_positions", "injury_status", "height", "weight", "age"]

   def __init__(self, worksheet: Worksheet):
      super().__init__(worksheet)


      logger.info(f"Initialized {self}")


   def set_user(self, user: User):
      """Sets the user attribute for the spreadsheet"""
      logger.info(f"Setting user attributes for {self}")
      self.user = user
      user_info = convert_single_level_dict_to_matrix(
         {
         "Username" : self.user.name,
         "User_ID" : self.user.id
         }
      )
      self.update_user_info(user_info)
   

   def update_user_info(self, user_info: dict):
      """Adds basic user informaiton to the top of the worksheet"""
      logger.info(f"Adding user informaiton to {self}")
      self.write_cell_range(user_info)


   def update_roster(self):
      """Updates the member roster with a new roster dataframe"""
      pass


   def update_position_count(self):
      """Updates the member roster with a new position count"""
      pass