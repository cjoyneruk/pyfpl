from pyfpl import datasets
from pyfpl import retrieve
import pyfpl as fpl
import numpy as np
import pandas as pd


def teamCheck(teaminfo):

    club_count = teaminfo[['clubid', 'id']].groupby('clubid').count().reset_index()
    if club_count['id'].max() > 3:
        return False
    else:
        return True

def teamSelector(teamlist, n_weeks):

    col_headings = ['GW+{}'.format(i) for i in range(0, n_weeks)]

    formations = [[3, 4, 3], [3, 5, 2], [4, 3, 3], [4, 4, 2], [4, 5, 1], [5, 3, 2], [5, 4, 1]]

    # - Find all players for next n_weeks
    team_inds = np.zeros(11, dtype=int)
    current_inds = np.zeros(11, dtype=int)

    teamselection = pd.DataFrame(np.zeros((15, len(col_headings)+2)), columns=['id', 'name'] + col_headings)
    teamselection[['id', 'name']] = teamlist[['id', 'name']]
    teamselection[col_headings] = False

    for col_name in col_headings:

        X = teamlist[['id', 'position', col_name]].sort_values(by=['position', col_name], ascending=[True, False])

        current_inds[0] = X.index[0]

        points = 0
        for formation in formations:
            t = 1
            for pos, n_pos in enumerate(formation):

                t, s = t+n_pos, t
                current_inds[s:t] = X.loc[X['position']==pos+2, col_name].index[:n_pos].values

            if X.loc[current_inds, col_name].sum() > points:
                points = X.loc[current_inds, col_name].sum()
                team_inds = current_inds.copy()

        teamselection.loc[team_inds, col_name] = True

    return teamselection

def teamReturn(teamlist, n_weeks, weighting=0.8):

    col_headings = ['GW+{}'.format(i) for i in range(0, n_weeks)]

    formations = [[3, 4, 3], [3, 5, 2], [4, 3, 3], [4, 4, 2], [4, 5, 1], [5, 3, 2], [5, 4, 1]]

    # - Find all players for next n_weeks
    current_inds = np.zeros(11, dtype=int)

    tot_points = 0
    for k, col_name in enumerate(col_headings):

        X = teamlist[['id', 'position', col_name]].sort_values(by=['position', col_name], ascending=[True, False])

        current_inds[0] = X.index[0]

        points = 0
        for formation in formations:
            t = 1
            for pos, n_pos in enumerate(formation):

                t, s = t+n_pos, t
                current_inds[s:t] = X.loc[X['position']==pos+2, col_name].index[:n_pos].values

            if X.loc[current_inds, col_name].sum() > points:
                points = X.loc[current_inds, col_name].sum()

        tot_points += (weighting**k)*points

    return tot_points


def Transfer(pred, team):

    if not isinstance(team, fpl.CurrentTeam):
        raise TypeError('Please supply a pyfpl.CurrentTeam object')

    balance = team.transfers.loc[0, 'bank']

    teamlist = team.essential
    teamlist = teamlist.merge(pred)

    # - remove current players from pred
    inds = pred[pred['id'].isin(teamlist['id'])].index
    pred = pred.drop(inds)

    W = teamlist.loc
    print(pred.shape)

    return teamlist, inds


myteam = fpl.CurrentTeam(retrieve.user_team('user1'))

cgw = 3
n_weeks = 6

balance = myteam.transfers.loc[0, 'bank']

plist = retrieve.player_list(gw=cgw-1)

player = fpl.Player(retrieve.player(123))

df = datasets.gameweekPrediction()


df = df[df['GW']<(cgw+n_weeks)]
predictions = df.pivot(index='id', columns='GW', values='predicted_points_scored').reset_index()


cols_needed = ['id', 'team', 'element_type', 'now_cost', 'web_name']
predictions = predictions.merge(plist[cols_needed], on='id', how='left')
predictions = predictions.rename(columns={'team': 'clubid',
                                          'element_type': 'position',
                                          'now_cost': 'value',
                                          'web_name': 'name'})

r = np.arange(cgw, cgw+n_weeks, dtype=int)
GW_cols = ['GW+{}'.format(i) for i in range(0,n_weeks)]
predictions = predictions.rename(columns=dict(zip(r,GW_cols)))

teaminfo = team_chris.essential
teaminfo = teaminfo.merge(predictions[['id', 'name']+ GW_cols], on='id', how='left')
teaminfo = teaminfo.rename(columns={'selling_price': 'value'})
teaminfo = teaminfo.sort_values(by='position').reset_index(drop=True)
predictions = predictions[teaminfo.columns]

drop_inds = predictions[predictions['position'].isna()].index
predictions = predictions.drop(drop_inds)
predictions[['clubid', 'position', 'value']] = predictions[['clubid', 'position', 'value']].astype(int)

team_ids = teaminfo['id'].values
inds = predictions[predictions['id'].isin(team_ids)].index
predictions = predictions.drop(inds)

predictions['tot_return'] = predictions[GW_cols].sum(axis=1)
drop_inds = predictions[predictions['tot_return']<3].index
predictions = predictions.drop(drop_inds)
predictions = predictions.reset_index(drop=True)

max_prices = np.array([teaminfo.loc[teaminfo['position']==i,'value'].max() for i in range(1,5)]) + balance

# - eliminate those players too expensive
for i, price in enumerate(max_prices):

    records = (predictions['position']==(i+1)) & (predictions['value']>price)
    inds = predictions[records].index
    if len(inds)>0:
        predictions = predictions.drop(inds)

position_locs = [[0,1], [2,3,4,5,6], [7,8,9,10,11], [12,13,14]]

current_return = teamReturn(teaminfo, n_weeks=6, weighting=0.5)
teamselection = teamSelector(teaminfo, n_weeks=6)

#j = 10
#predictions = predictions[predictions['position']==3]
N = predictions.shape[0]

transfers = pd.DataFrame([], columns=['player_out', 'player_in', 'player_cost', 'transfer_cost', 'points_gain'])

# for t, ind in enumerate(predictions.index):
#
#     # - swap players and check price is ok
#     pos, val = predictions.loc[ind, ['position','value']]
#
#     # - Check value
#     if val <= teaminfo.loc[j, 'value'] + balance:
#
#         # - swap in player and check
#         teaminfo.loc[j], temp = predictions.loc[ind], teaminfo.loc[j].copy()
#
#         # - Check for clubs
#         if teamCheck(teaminfo):
#             tot_points = teamReturn(teaminfo, n_weeks=6, weighting=0.5)
#             if tot_points>current_return:
#                 print('{} -> {} [{:.1f}]'.format(temp['name'], teaminfo.loc[j,'name'], tot_points))
#
#                 transfers.loc[transfers.shape[0]] = [teaminfo.loc[j,'id'], teaminfo.loc[j,'name'], teaminfo.loc[j,'value'], tot_points]
#
#         teaminfo.loc[j] = temp
#
#     print('{:.1f}% - complete'.format(100*(t+1)/N))
#
# transfers.to_csv('possible_transfers.csv', index=False)

predictions = predictions.reset_index(drop=True)

for ind in predictions.index:

    # - swap players and check price is ok
    pos, val_in = predictions.loc[ind, ['position','value']]

    for j in position_locs[pos-1]:

        val_out = teaminfo.loc[j, 'value']
        # - Check value
        if val_in <= val_out + balance:

            # - swap in player and check
            teaminfo.loc[j], temp = predictions.loc[ind], teaminfo.loc[j].copy()

            if teamCheck(teaminfo):

                alt_return = teamReturn(teaminfo, n_weeks=6, weighting=0.5)
                if alt_return>current_return+2:
                    transfers.loc[transfers.shape[0]] = [temp['name'], teaminfo.loc[j, 'name'],
                                                         val_in, val_in-val_out, alt_return-current_return]
                    print('{} -> {} [{:.1f}]'.format(temp['name'], teaminfo.loc[j,'name'], alt_return-current_return))
            teaminfo.loc[j] = temp

    print('{:.1f}% - complete'.format(100*ind/N))

transfers.to_csv('chris_transfers.csv',index=False)
teaminfo.to_csv('chris_teaminfo.csv', index=False)
teamselection.to_csv('chris_selection.csv', index=False)


#tot_return = teamReturn(teaminfo, 6, 0.6)

