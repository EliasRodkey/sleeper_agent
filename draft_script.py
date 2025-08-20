import logging
import pandas as pd

from agents.prompts.draft_status_prompt import DraftStatusPrompt

from sleeper.sleeper_draft import Draft
from sleeper.sleeper_league import League
from sleeper.sleeper_user import User

from spreadsheets.draft_tiers_worksheet import DraftTiersWorksheet
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


def merge_players_df_and_tier_df(players_df):
    """Merges the tier df into the players df"""
    spreadsheet = get_spreadsheet(EFantasySpreadsheets.TIERS_2025)
    tiers_worksheet = DraftTiersWorksheet(spreadsheet.worksheet('Sheet1'))
    positional_tiers = tiers_worksheet.retrieve_tiers()

    return pd.merge(players_df, positional_tiers[["player_id", "tier", "intra_tier_ranking"]], how="left", on=["player_id"])


if __name__ == "__main__":
    # players_df = get_players_df()
    # my_user = User("thecondor")

    # league_id, league_info = my_user.retrieve_league_info("AGENT TEST LEAGUE")
    # # league_id, league_info = User("thecondor").retrieve_league_info("Margaritaville")
    # # league_id, league_info = User("thecondor").retrieve_league_info("The Gentleman's League")
    # league = League(league_id, league_json=league_info, redraft=True)
    # spreadsheet = get_spreadsheet(EFantasySpreadsheets.TEST)
    # draft_spreadsheet = DraftSpreadsheet(my_user, spreadsheet, league, players_df)

    # # In case the draft is already complete, call once before looping.
    # draft_spreadsheet.update_draftboard_spreadsheet()

    # while draft_spreadsheet.draft.status != Draft.COMPLETE:
    #     update_status = draft_spreadsheet.update_draftboard_spreadsheet()

    #     if update_status:
    #         logger.info(f"{draft_spreadsheet} updated with new data.")

    players_df = get_players_df()
    tier_merged_df = merge_players_df_and_tier_df(players_df)

    my_user = User("thecondor")

    league_id, league_info = my_user.retrieve_league_info("AGENT TEST LEAGUE")
    # # league_id, league_info = User("thecondor").retrieve_league_info("Margaritaville")
    # # league_id, league_info = User("thecondor").retrieve_league_info("The Gentleman's League")
    league = League(league_id, league_json=league_info, redraft=True)

    picks_df, remaining_players_df = league.draft.retrieve_draft_state(tier_merged_df)

    my_user.set_roster(picks_df, tier_merged_df)
    roster_df = my_user.roster.df
    position_counts_df = my_user.roster.position_count

    
    update_prompt = DraftStatusPrompt(
        roster_df, position_counts_df, picks_df, remaining_players_df
    )

    # logger.info(f"Test DraftUpdatePrompt attr current_roster: {update_prompt.current_roster}")
    # logger.info(f"Test DraftUpdatePrompt attr position_count {update_prompt.position_count}")
    # logger.info(f"Test DraftUpdatePrompt attr draft_picks: {update_prompt.draft_picks}")
    logger.info(f"Test DraftUpdatePrompt attr remaining_players: {update_prompt.remaining_players}")

    # logger.info(f"Test DraftUpdatePrompt method summarize_current_roster: {update_prompt.summarize_current_roster()}")
    logger.info(f"Test DraftUpdatePrompt method get_top_available_by_tier: {update_prompt.get_top_available_by_tier(tier_max=5)}")
    logger.info(f"Test DraftUpdatePrompt method get_top_available_by_adp: {update_prompt.get_top_available_by_adp()}")
    # logger.info(f"Test DraftUpdatePrompt method summarize_recent_picks: {update_prompt.summarize_recent_picks()}")
    logger.info(f"Test DraftUpdatePrompt method detect_scarcity: {update_prompt.detect_scarcity(['WR'], tier_cutoff=4)}")
    logger.info(f"Test DraftUpdatePrompt method detect_scarcity: {update_prompt.detect_scarcity(['RB'], tier_cutoff=6)}")


