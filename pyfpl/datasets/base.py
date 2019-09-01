import pandas as pd
from .. import config
from ..retrieve import current_gw

settings = config.get_config()
historic_dir = settings['data_dir'] + 'Historic_data/'
current_dir = settings['data_dir'] + 'Current_data/'

def currentSeason(cols=None):

    filename = current_dir + 'seasonData.csv'

    return pd.read_csv(filename, usecols=cols)

def gameweekPrediction(gw=None):

    if gw is None:
        gw = current_gw()


    filename = current_dir + 'GW' + str(gw+1) + '_predictions.csv'

    return pd.read_csv(filename)

# def seasondata(seasons=None, fields=None):
#
#     filename = current_dir + 'pastSeasonData.csv'
#
#     if fields is None:
#
#         df = pd.read_csv(filename)
#     else:
#         if not isinstance(fields, list):
#             raise TypeError('Please provide a list for fields')
#
#         cols = fields + ['season']
#         df = pd.read_csv(filename, usecols=cols)
#
#     if seasons is None:
#         return df
#     elif isinstance(seasons, list):
#         return df[df['season'].isin(seasons)]
#     else:
#         return df[df['season'] == seasons]
#
