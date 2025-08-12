import logging
import pandas as pd
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
        return response.json().get("players")
    else:
        response.raise_for_status()


def get_standard_adp():
    """Retrieve ADP data for standard draft"""
    logger.debug(f"Retrieveing standard ADP data")

    url = f"{BASE_URL}/standard"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("players")
    else:
        response.raise_for_status()


def get_rookie_adp():
    """Retrieve ADP data for rookie draft"""
    logger.debug(f"Retrieveing full rookie data")

    url = f"{BASE_URL}/rookie"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("players")
    else:
        response.raise_for_status()


def get_half_ppr_adp_df(ppr_weight: float=0.6, standard_weight: float=0.4) -> pd.DataFrame:
    """Returns a pandas dataframe with the weighted ADP between standard and full PPR"""
    if ppr_weight + standard_weight != 1:
        logger.error(f"Invalid weights for ADP calcualtion: ppr_weight={ppr_weight}, standard_weight={standard_weight}")
        raise ValueError(f"Invalid weights for ADP calcualtion: ppr_weight={ppr_weight}, standard_weight={standard_weight}")

    ppr_df = pd.DataFrame.from_dict(get_ppr_adp()).rename(columns={"adp" : "ppr_adp"})
    standard_df = pd.DataFrame.from_dict(get_standard_adp()).rename(columns={"adp" : "standard_adp"})
    merged_df = pd.merge(standard_df, ppr_df, on='player_id', how='inner')
    merged_df['adp'] = 0.4 * merged_df['standard_adp'] + 0.6 * merged_df['ppr_adp']
    merged_df.rename(columns={"name_x" : "full_name"}, inplace=True)

    assert merged_df['standard_adp'].notnull().all()
    assert merged_df['ppr_adp'].notnull().all()

    return merged_df


def get_rookie_adp_df() -> pd.DataFrame:
    """Returns a pandas dataframe with the ADP for rookie drafts"""
    return pd.DataFrame.from_dict(get_rookie_adp()).rename(columns={"name_x" : "full_name"})