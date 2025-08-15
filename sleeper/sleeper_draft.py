from datetime import datetime, timedelta
import logging
import time

import sleeper.sleeper_api as sleeper_api

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class Draft:
    """Represents a sleeper draft, holds pick information, remaining players and methods to update"""
    PRE_DRAFT = "pre_draft"
    DRAFTING = "drafting"
    PAUSED = "paused"
    COMPLETE = "complete"

    def __init__(self, draft_id: str):
        self.id = draft_id
        self.picks = []
        self.last_picks = [] 
        self._retrieve_draft_info(draft_id)
        self.update_picks()

        logger.info(f"{self} Initialized")

    
    def update_picks(self) -> str:
        """
        Updates the picks attribute with the most recent picks from the draft.
        Returns the draft status as a string.
        """
        logger.info(f"Updating {self} with most recent picks from the draft")
        self.last_picks = self.picks # convert last_picks to the current picks before update
        draft_status = self.update_status()
        self.status = draft_status
        self.picks = sleeper_api.get_draft_picks(self.id)
        
        return self.status
        
        
    def update_status(self):
        """Retrieves the most recent draft status"""
        logger.debug(f"Retrieving draft status for {self}")
        self.status = sleeper_api.get_draft_info(self.id).get("status")
        return self.status


    def _retrieve_draft_info(self, draft_id: str):
        """Collects the data of teh given draft and assigns it to attributes in this class instance."""
        logger.info(f"Retrieveing draft information for {self}")
        
        self.draft_json = sleeper_api.get_draft_info(draft_id)
        self.id = self.draft_json.get("draft_id")
        self.type = self.draft_json.get("type")
        self.status = self.draft_json.get("status")
        self.settings = self.draft_json.get("settings")
        self.order = self.draft_json.get("draft_order")
        raw_start_time =self.draft_json.get("start_time")
        if raw_start_time:
            start_time_dt = datetime.fromtimestamp(float(raw_start_time) / 1000)
            self.start_time =start_time_dt
        else:
            self.start_time = datetime.now()
    

    def wait_until_draft_resumes(self):
        """Checks the status of the draft continuously until it is no longer paused"""
        logger.info(f"{self} {self.status.upper()}, waiting for status change")
        while self.update_status() == self.PAUSED:
            logger.debug(f"Latest status={self.status}")
            time.sleep(1)


    def wait_until_draft(self):
        """Wait until the draft has started then continue"""
        time_to_wait = self.start_time - datetime.now()
        if time_to_wait < timedelta():
            logger.warning(f"{self} past start time by {-time_to_wait}, status={self.status}")
            return
        logger.warning(f"Draft {self} is in {self.status}. Waiting {time_to_wait} for {self} to begin")
        time.sleep(time_to_wait.total_seconds())
        logger.info(f"{self} has begun, good luck!")
    

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
        


if __name__ == "__main__":
    draft = Draft("1254970326761082880") # Draft ID pulled from Margaritaville 
    logger.info(f"Draft attribute test id: {draft.id}")
    logger.info(f"Draft attribute test type: {draft.type}")
    logger.info(f"Draft attribute test status: {draft.status}")
    logger.info(f"Draft attribute test settings: {draft.settings}")
    logger.info(f"Draft attribute test order: {draft.order}")
    draft.update_picks()