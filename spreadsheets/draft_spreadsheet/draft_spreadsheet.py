import logging
import pandas as pd
import re
import time

from spreadsheets.sheet_manager import SheetManager, Spreadsheet
from spreadsheets.draft_spreadsheet.league_settings_worksheet import LeagueSettingsWorksheet
from spreadsheets.draft_spreadsheet.draftboard_worksheet import DraftboardWorksheet
from spreadsheets.draft_spreadsheet.picks_worksheet import PicksWorksheet
from spreadsheets.draft_spreadsheet.member_roster_worksheet import MemberRosterWorksheet

from sleeper.ffcalc_api import get_half_ppr_adp_df, get_rookie_adp_df
from sleeper.sleeper_league import League
from sleeper.sleeper_user import User

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
    


class DraftSpreadsheet(SheetManager):
    """A representation of the draft spreadsheet"""

    LEAGUE_SETTINGS = "league_settings"
    DRAFTBOARD = "draftboard"
    PICKS = "picks"
    MY_TEAM = "thecondor"

    def __init__(self, spreadsheet: Spreadsheet, league: League, players_df: pd.DataFrame):
        super().__init__(spreadsheet)

        self.league = league
        self.draft = self.league.draft
        self.players_df = self._sort_by_adp(players_df)
        self.my_user = self.league.users[self.league.username_id_map[self.MY_TEAM]]
        
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
        if user.name == self.MY_TEAM:
            user_ws = self.create_sheet(f"my_roster", MemberRosterWorksheet)

        elif user.name == "none":
            bot_user += 1
            user_ws = self.create_sheet(f"bot_{bot_user}", MemberRosterWorksheet)
            
        else:
            user_ws = self.create_sheet(f"{user.name}_roster", MemberRosterWorksheet)
        
        user_ws.set_user(user)


    def update_draftboard(self) -> bool:
        """
        Updates the draftboard with a new pick, removing it from the draftboard worksheet and moving it to the picks worksheet and respective rosters.
        Returns boolean if the draft spreadsheet was successfully updates or not.
        """
        logger.info(f"Updating {self} with new draftboard, picks, and rosters")

        if (self.draft.picks == {}) or (self.draft.picks == self.draft.last_picks):
            logger.info(f"{self} not updated, no new picks with last refresh")
            time.sleep(1)
            
            return False

        else:
            self.last_picks_json = self.draft.picks
            picks_df = self._convert_picks_json_to_df(self.draft.picks)

            # TODO: It looks like rosters won't get updated until after the draft. have to build the rosters using the pciks df :(
            self.league.update_rosters(self.players_df)
            try:
                print(self.my_user.roster.json)
                print(self.my_user.roster.df)
                print(self.my_user.roster.position_count)
            except:
                pass
        
            return True
        

    def _convert_picks_json_to_df(self, picks: dict) -> pd.DataFrame:
        """Converts the picks json API return to a dataframe with other metadata"""
        picks_df = pd.DataFrame.from_dict(picks)

        picks_df.drop(columns=["is_keeper", "metadata"], inplace=True)

        # Merge player info into picks_df
        picks_df = picks_df.merge(self.players_df, on='player_id', how='left')

        # Add username column to picks_df
        picks_df['username'] = picks_df['picked_by'].map(self.league.id_username_map)
        picks_df['username'] = picks_df['username'].fillna('Bot')

        return picks_df


    def _sort_by_adp(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sorts the players dataframe by ADP gathered from FantasyFootballCalculator.com API"""
        logger.info(f"Sorting players dataframe by ADP")
        if self.league.redraft:
            adp_df = get_half_ppr_adp_df()
        
        else:
            adp_df = get_rookie_adp_df()

        adp_df = adp_df[adp_df['full_name'].notna()]
        adp_df.loc[adp_df['position_x'] == 'DEF', 'full_name'] = adp_df.loc[adp_df['position_x'] == 'DEF', 'team_x'] + ' Defense'
        df['normalized_name'] = df['full_name'].apply(self._normalize_name)
        adp_df['normalized_name'] = adp_df['full_name'].apply(self._normalize_name)

        merged_df = pd.merge(df, adp_df[['normalized_name', 'adp']], on='normalized_name', how='left')

        max_adp = adp_df['adp'].max()
        merged_df['adp'] = merged_df['adp'].fillna(max_adp + 1)

        return merged_df.sort_values('adp')


    def _normalize_name(self, name: str):
        """Normalized the names of plaeyrs to match accross datasets"""
        if not isinstance(name, str):
            name = ""
        name = name.lower().strip()
        # Remove common suffixes
        name = re.sub(r'\b(jr\.?|sr\.?|ii|iii|iv|v)\b', '', name)
        # Remove punctuation and extra whitespace
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name.strip()