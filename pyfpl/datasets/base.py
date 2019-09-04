import pandas as pd
from .. import config
from ..retrieve import current_gw

def _current_dir():
    settings = config.get_settings()
    return settings['DATA_PATH'] + 'Current_data/'

def _historic_dir():
    settings = config.get_settings()
    return settings['DATA_PATH'] + 'Historic_data/'

def currentSeason(cols=None):

    filename = _current_dir() + 'seasonData.csv'

    return pd.read_csv(filename, usecols=cols)

def gameweekPrediction(gw=None):

    if gw is None:
        gw = current_gw()

    filename = _current_dir() + 'GW' + str(gw+1) + '_predictions.csv'

    return pd.read_csv(filename)

def seasonData(season=2018, cols=None):

    filename = _historic_dir() + str(season) + '-' + str(season-1999) + '/season_data.csv'

    return pd.read_csv(filename, usecols=cols)

def matchList(season=2018, cols=None):

    filename = _historic_dir() + str(season) + '-' + str(season-1999) + '/match_list.csv'

    return pd.read_csv(filename, usecols=cols)

def clubList(season=2018, cols=None):

    filename = _historic_dir() + str(season) + '-' + str(season-1999) + '/club_list.csv'

    return pd.read_csv(filename, usecols=cols)