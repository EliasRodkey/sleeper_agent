import logging
import datetime

from spreadsheets.worksheet_wrapper import WorksheetWrapper, Worksheet

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



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