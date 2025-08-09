import logging
import requests

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


BASE_URL = "https://api.sleeper.app/v1"



def get_user_info(username: str):
    """Retrieve user information by user ID or Username."""
    logger.debug(f"Retrieveing user information from user {username} from sleeper API")

    url = f"{BASE_URL}/user/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_user_leagues(user_id: str, sport: str = "nfl", year: int = 2025):
    """Retrieve leagues associated with a user by user ID or Username."""
    logger.debug(f"Retrieveing user leagues for user ID {user_id} (sport={sport}, year={year}) from sleeper API")

    url = f"{BASE_URL}/user/{user_id}/leagues/{sport}/{year}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_league_info(league_id: str):
    """Collects the settings of a given league"""
    logger.debug(f"Retrieveing information on league ID {league_id} from sleeper API")
    
    url = f"{BASE_URL}/league/{league_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_league_rosters(league_id: str):
    """Collects the rosters of a given league"""
    logger.debug(f"Retrieveing rosters for league ID {league_id} from sleeper API")
    
    url = f"{BASE_URL}/league/{league_id}/rosters"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_draft_info(draft_id: str):
    """Collects the rosters of a given draft ID"""
    logger.debug(f"Retrieveing draft information for draft ID {draft_id} from sleeper API")
    
    url = f"{BASE_URL}/draft/{draft_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_draft_picks(draft_id: str):
    """Collects all the draft picks of a given draft ID"""
    logger.debug(f"Retrieveing draft picks for draft ID {draft_id} from sleeper API")
    
    url = f"{BASE_URL}/draft/{draft_id}/picks"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_players():
    """
    Collects information on all players in the NFL.
    USE AT MOST ONCE PER DAY.
    """
    logger.info(f"Retrieveing data on all players in the nfl")
    
    url = f"{BASE_URL}/players/nfl"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
        

if __name__ == "__main__":
    import pprint

    pprint.pprint(get_user_leagues("TheCondor"))