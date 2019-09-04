from pyfpl import datasets
import numpy as np

cols = ['element', 'clubid', 'matchid', 'GW', 'was_sub',
       'in_squad', 'minutes',  'web_name', 'value',
       'status', 'position', 'chance_of_playing_this_round', 'chance_of_playing_next_round']


sd = datasets.pastSeason(season=2018, cols=cols)

df = sd[sd['status']=='i']

