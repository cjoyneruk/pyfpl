import numpy as np

def simpleSelector(squad, prediction, beta=0.6):

    formations = [[3, 4, 3], [3, 5, 2], [4, 3, 3], [4, 4, 2], [4, 5, 1], [5, 3, 2], [5, 4, 1]]

    team_inds = np.zeros(11, dtype=int)
    current_inds = np.zeros(11, dtype=int)

    # - Sort squad by position and then predicted points
    X = squad[['PLplayerID', 'position', 'pred_points+0']].sort_values(by=['position', 'pred_points+0'],
                                                                       ascending=[True, False])

    # - Add goalkeeper

    points = 0

    # - cycle through formations
    for formation in formations:

        current_inds[0] = X.index[0]
        # - get best players for that formation
        t = 1
        for pos, n_pos in enumerate(formation):
            t, s = t + n_pos, t
            current_inds[s:t] = X.loc[X['position'] == pos + 1, 'pred_points+0'].index[:n_pos].values

        # -
        if X.loc[current_inds, 'pred_points+0'].sum() > points:
            points = X.loc[current_inds, 'pred_points+0'].sum()
            team_inds = current_inds.copy()

    squad['selected'] = False
    squad.loc[team_inds, 'selected'] = True

    return squad