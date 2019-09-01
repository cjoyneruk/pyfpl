import numpy as np

def teamCheck(team):

    if team.purchase_value() > 100:
        return False

    club_count = squad[['PLclubID', 'PLplayerID']].groupby('PLclubID').count().reset_index()
    if club_count['PLplayerID'].max() > 3:
        return False
    else:
        return True


def team_selection(squad):

    formations = [[3, 4, 3], [3, 5, 2], [4, 3, 3], [4, 4, 2], [4, 5, 1], [5, 3, 2], [5, 4, 1]]

    team_inds = np.zeros(11, dtype=int)
    current_inds = np.zeros(11, dtype=int)

    # - Sort squad by position and then predicted points
    X = squad[['PLplayerID','position', 'pred_points+0']].sort_values(by=['position', 'pred_points+0'], ascending=[True, False])

    # - Add goalkeeper

    points = 0

    # - cycle through formations
    for formation in formations:

        current_inds[0] = X.index[0]
        # - get best players for that formation
        t = 1
        for pos, n_pos in enumerate(formation):
            t, s = t+n_pos, t
            current_inds[s:t] = X.loc[X['position']==pos+1, 'pred_points+0'].index[:n_pos].values

        # -
        if X.loc[current_inds, 'pred_points+0'].sum()>points:
            points = X.loc[current_inds, 'pred_points+0'].sum()
            team_inds = current_inds.copy()

    squad['selected'] = False
    squad.loc[team_inds,'selected'] = True

    return squad


def squad_return(squad, team_selection=False):

    # - Goal keeper return
    squad = squad.rename(columns={'pred_points': 'pred_points+0'})
    pcols = ['pred_points+0', 'pred_points+1', 'pred_points+2', 'pred_points+3', 'pred_points+4', 'pred_points+5']
    k = np.arange(0,6)

    #GLK_points = squad.loc[squad['position']==0, pcols].values*(0.9**k)
    #GLK_points = GLK_points.max(axis=0).sum()

    formations = [[3, 4, 3], [3, 5, 2], [4, 3, 3], [4, 4, 2], [4, 5, 1], [5, 3, 2], [5, 4, 1]]

    team_inds = np.zeros((11, 6), dtype=int)
    current_inds = np.zeros(11, dtype=int)
    for k, col_name in enumerate(pcols):

        X = squad[['PLplayerID','position', col_name]].sort_values(by=['position', col_name], ascending=[True, False])

        current_inds[0] = X.index[0]
        points = 0
        for formation in formations:
            t = 1
            for pos, n_pos in enumerate(formation):

                t, s = t+n_pos, t
                #print(team_inds[s:t,i].shape)
                current_inds[s:t] = X.loc[X['position']==pos+1, col_name].index[:n_pos].values
                #print(n_pos)
                #print(X.loc[X['position'] == pos+1, col_name].index[:n_pos].values.shape)

            if X.loc[current_inds, col_name].sum()>points:
                points = X.loc[current_inds, col_name].sum()
                team_inds[:,k] = current_inds

    tot_return = 0
    for k, col_name in enumerate(pcols):
        tot_return += squad.loc[team_inds[:,k],col_name].sum()

    return tot_return