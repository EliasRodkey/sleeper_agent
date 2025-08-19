import logging

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


if __name__ == "__main__":

    players_df = get_players_df()
    my_user = User("thecondor")

    league_id, league_info = my_user.retrieve_league_info("AGENT TEST LEAGUE")
    # league_id, league_info = User("thecondor").retrieve_league_info("Margaritaville")
    # league_id, league_info = User("thecondor").retrieve_league_info("The Gentleman's League")
    league = League(league_id, league_json=league_info, redraft=True)
    spreadsheet = get_spreadsheet(EFantasySpreadsheets.TEST)
    draft_spreadsheet = DraftSpreadsheet(my_user, spreadsheet, league, players_df)

    # In case the draft is already complete, call once before looping.
    draft_spreadsheet.update_draftboard_spreadsheet()

    while draft_spreadsheet.draft.status != Draft.COMPLETE:
        update_status = draft_spreadsheet.update_draftboard_spreadsheet()

        if update_status:
            logger.info(f"{draft_spreadsheet} updated with new data.")