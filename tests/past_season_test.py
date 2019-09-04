from pyfpl import datasets
import numpy as np

cols = ['element', 'clubid', 'matchid', 'GW', 'was_sub',
       'in_squad', 'minutes',  'web_name', 'value', 'match_no',
       'status', 'position', 'chance_of_playing_this_round', 'chance_of_playing_next_round']

sd = datasets.seasonData(season=2018, cols=cols)

# - Construct baseline: If started previous game and available then predict start, otherwise not

# - Create started column
sd['start'] = (True^sd['was_sub'])&sd['in_squad']

# - Create started previous game column
alt_df = sd[['element', 'match_no', 'start']]
alt_df = alt_df.rename(columns={'start': 'start_prev'})
alt_df['match_no'] += 1

sd = sd.merge(alt_df, on=['element', 'match_no'], how='left')

sd = sd.drop(sd[sd['match_no']==1].index)
sd = sd.reset_index(drop=True)

X = sd[['start_prev', 'status']]
y = sd['start']

y_pred = X['start_prev']&(X['status']=='a')

n = y.shape[0]
n_c = sum(y==y_pred)
n_i = n - n_c

print(n_c/n)