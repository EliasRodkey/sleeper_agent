import logging
import pandas as pd

from spreadsheets.sheet_manager import SheetManager, Spreadsheet
from spreadsheets.draft_spreadsheet.league_settings_worksheet import LeagueSettingsWorksheet
from spreadsheets.draft_spreadsheet.draftboard_worksheet import DraftboardWorksheet
from spreadsheets.draft_spreadsheet.picks_worksheet import PicksWorksheet
from spreadsheets.draft_spreadsheet.member_roster_worksheet import MemberRosterWorksheet

from sleeper.sleeper_league import League
from sleeper.sleeper_user import User

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
    


class DraftSpreadsheet(SheetManager):
    """A representation of the draft spreadsheet"""

    LEAGUE_SETTINGS = "league_settings"
    DRAFTBOARD = "draftboard"
    PICKS = "picks"
    MY_ROSTER = "my_roster"

    def __init__(self, my_user: User, spreadsheet: Spreadsheet, league: League, players_df: pd.DataFrame):
        super().__init__(spreadsheet)

        self.league = league
        self.draft = self.league.draft
        self.players_df = players_df
        self.my_user = my_user
        
        if not self.is_empty():
            self.clear_spreadsheet()
        self.initialize_spreadsheet()

        logger.info(f"Initialized {self}")
    

    def initialize_spreadsheet(self):
        """If the spreadsheet is empty, it get initialized with the correct worksheet titles and information"""
        logger.info(f"Initializing {self}...")
        self.create_settings_worksheet()
        self.create_draftboard_worksheet()
        self.create_picks_worksheet()
        self.create_user_worksheet(self.my_user)

        # for user_id, user in self.league.users.items():
        #     username = self.league.id_username_map[user_id]
        #     self.create_user_worksheet(username, user)
    

    def create_settings_worksheet(self):
        """Creates the league settings worksheet inside of the draftboard spreadsheet"""
        logger.info(f"Creating new league settings worksheet")
        settings_ws = self.get_sheet("Sheet1", LeagueSettingsWorksheet)
        self.rename_sheet(self.LEAGUE_SETTINGS)
        settings_ws.set_league(self.league)
    

    def create_draftboard_worksheet(self):
        """Creates the draftboard worksheet inside of the draftboard spreadsheet"""
        logger.info(f"Creating new draftboard worksheet")
        draftboard_ws = self.create_sheet(self.DRAFTBOARD, DraftboardWorksheet)
        draftboard_ws.update_draftboard(self.players_df)
    

    def create_picks_worksheet(self):
        """Creates the picks worksheet inside of the draftboard spreadhseet"""
        logger.info(f"Creating new picks worksheet")
        self.create_sheet(self.PICKS, PicksWorksheet)
    

    def create_user_worksheet(self, user: User):
        """Creates a user worksheet inside of the draftboard spreadsheet"""
        logger.info(f"Creating new user worksheet for {user.name}")

        bot_user = 0
        if user.name == self.my_user.name:
            user_ws = self.create_sheet(f"my_roster", MemberRosterWorksheet)

        elif user.name == "none":
            bot_user += 1
            user_ws = self.create_sheet(f"bot_{bot_user}", MemberRosterWorksheet)
            
        else:
            user_ws = self.create_sheet(f"{user.name}_roster", MemberRosterWorksheet)
        
        user_ws.set_user(user)


    def update_draftboard_spreadsheet(self) -> bool:
        """
        Updates the draftboard with a new pick, removing it from the draftboard worksheet and moving it to the picks worksheet and respective rosters.
        Returns boolean if the draft spreadsheet was successfully updates or not.
        """
        logger.debug(f"Updating the draft spreadsheet depending on the current status of the draft.")

        self.draft.update_picks()
        status = self.draft.status
        logger.debug(f"Current draft status: {status}")

        match status:
            case self.draft.DRAFTING:
                if (self.draft.picks == self.draft.last_picks):
                    update_status = False
                
                else:
                    update_status = self.update_worksheets()

            case self.draft.COMPLETE:
                update_status = self.update_worksheets()
                
            case self.draft.PRE_DRAFT:
                self.draft.wait_until_draft()
                update_status = False

            case self.draft.PAUSED:
                self.draft.wait_until_draft_resumes()
                update_status = False

            case _:
                logger.error(f"Unrecognized draft status {self.draft.status}")
                update_status = False
        
        return update_status
    

    def update_worksheets(self):
        """Updates the draftboard, picks, and my_roster worksheets with the latest picks"""
        # Turn the picks API return into a df and merge with player data
        picks_df, remaining_players_df = self.draft.retrieve_draft_state(self.players_df)

        # Update the picks WS with new picks
        picks_ws = self.get_sheet(self.PICKS, PicksWorksheet)
        picks_ws.update_picks(picks_df)

        # Update the user roster with new picks
        self.my_user.set_roster(picks_df, self.players_df)
        my_team_ws = self.get_sheet(self.MY_ROSTER, MemberRosterWorksheet)
        my_team_ws.update_position_count()
        my_team_ws.update_roster()
        
        # Subtract the picked players from the players df to get the remaining players and repost to draftboard
        draftboard_ws = self.get_sheet(self.DRAFTBOARD, DraftboardWorksheet)
        draftboard_ws.update_draftboard(remaining_players_df)

        return True