from datetime import datetime
import logging
import time

from sleeper.sleeper_draft import Draft
from sleeper.sleeper_league import League
from sleeper.sleeper_user import User

from spreadsheets.draft_spreadsheet.draft_spreadsheet import DraftSpreadsheet
from spreadsheets.players_spreadsheet.players_spreadsheet import PlayersSpreadsheet
from spreadsheets.gspread_client import get_spreadsheet
from spreadsheets.spreadsheet_names import EFantasySpreadsheets

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def get_players_df():
    """Retrieves a dataframe of the NFL player data from the PlayersSpreadsheet"""
    spreadsheet = get_spreadsheet(EFantasySpreadsheets.PLAYERS)
    players_spreadsheet = PlayersSpreadsheet(spreadsheet)
    return players_spreadsheet.retrieve_player_data()


def update_draft_spreadsheet(draft_spreadsheet: DraftSpreadsheet) -> bool:
    """Directs the behavior of the draft spreadsheet based on the draft status, returns True if the sheet was successfully updated"""
    logger.info(f"Updating the draft spreadsheet depending on the current status of the draft.")

    draft_spreadsheet.draft.update_picks()
    status = draft_spreadsheet.draft.status

    match status:
        case Draft.DRAFTING:
            update_status = draft_spreadsheet.update_draftboard()

        case Draft.COMPLETE:
            update_status = draft_spreadsheet.update_draftboard()
            
        case Draft.PRE_DRAFT:
            draft_spreadsheet.draft.wait_until_draft()
            update_status = False

        case Draft.PAUSED:
            draft_spreadsheet.draft.wait_until_draft_resumes()
            update_status = False

        case _:
            logger.error(f"Unrecognized draft status {draft_spreadsheet.draft.status}")
            update_status = False
    
    return update_status


if __name__ == "__main__":

    players_df = get_players_df()

    league_id, league_info = User("thecondor").retrieve_league_info("AGENT TEST LEAGUE")
    # league_id, league_info = User("thecondor").retrieve_league_info("Margaritaville")
    # league_id, league_info = User("thecondor").retrieve_league_info("The Gentleman's League")
    league = League(league_id, league_json=league_info, redraft=True)
    spreadsheet = get_spreadsheet(EFantasySpreadsheets.TEST)
    draft_spreadsheet = DraftSpreadsheet(spreadsheet, league, players_df)

    while draft_spreadsheet.draft.status != Draft.COMPLETE:
        update_status = update_draft_spreadsheet(draft_spreadsheet)
        
