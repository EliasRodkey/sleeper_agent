import logging
import requests

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


BASE_URL = "https://fantasyfootballcalculator.com/api/v1/adp"


def get_ppr_adp():
    """Retrieve ADP data for full PPR draft"""
    logger.debug(f"Retrieveing full PPR ADP data")

    url = f"{BASE_URL}/ppr"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_standard_adp():
    """Retrieve ADP data for standard draft"""
    logger.debug(f"Retrieveing standard ADP data")

    url = f"{BASE_URL}/standard"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_rookie_adp():
    """Retrieve ADP data for rookie draft"""
    logger.debug(f"Retrieveing full rookie data")

    url = f"{BASE_URL}/rookie"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

