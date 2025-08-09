import logging

import sleeper_api as sleeper

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)



class Draft():
    """Represents a sleeper draft, holds pick information, remaining players and methods to update"""
    def __init__(self, draft_id: str):
        self.id = draft_id
        self.picks = []
        self._retrieve_draft_info(draft_id)

    
    def update_picks(self):
        """Updates the picks attribute with the most recent picks from the draft."""
        if self.status != "drafting":
            logger.warning(f"Unable to update picks for {self}, status={self.status}")

        else:
            logger.info(f"Updating {self} with most recent picks from the draft")
            self.picks = sleeper.get_draft_picks(self.id)


    
    def _retrieve_draft_info(self, draft_id: str):
        """Collects the data of teh given draft and assigns it to attributes in this class instance."""
        logger.info(f"Retrieveing draft information for {self}")
        
        self.draft_json = sleeper.get_draft_info(draft_id)
        self.id = self.draft_json.get("draft_id")
        self.type = self.draft_json.get("type")
        self.status = self.draft_json.get("status")
        self.settings = self.draft_json.get("settings")
        self.order = self.draft_json.get("draft_order")
    

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