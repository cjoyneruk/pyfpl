from .objectRetrieval import *
from .dataUpdates import *
import pyfpl as fpl
from datetime import date
import numpy as np
from .base import _current_dir


def __applymatchnumbering(matchlist):

    matchlist = matchlist.sort_values(by=['clubid', 'match_order'])
    matchlist['match_no'] = np.arange(0, 760) % 38 + 1

    return matchlist

def __allPlayerHistory(id_list):

    id_ = id_list[0]

    df = fpl.Player(player(id_)).history

    for id_ in id_list[1:]:

        df = pd.concat((df,fpl.Player(player(id_)).history))

    cols = ['element', 'fixture', 'assists', 'bonus', 'bps', 'clean_sheets', 'creativity',
            'goals_conceded', 'goals_scored', 'influence', 'minutes', 'own_goals',
            'penalties_missed', 'penalties_saved', 'red_cards', 'saves', 'threat',
            'total_points', 'value', 'yellow_cards']

    return df[cols].rename(columns={'fixture': 'matchid', 'element': 'id'})

def __applyELO(fixs, all_fix):

    beta = 0.02 # - learning parameter
    c = 0.3 # - home advantage

    # - Get initial ELO data
    filename = _current_dir() + 'ELO_init.csv'
    ELO_init = pd.read_csv(filename).set_index('clubid')

    # - Order club matches by index
    match_inds = all_fix.sort_values(by=['clubid', 'match_order']).copy()
    match_inds = match_inds.reset_index()
    match_inds = match_inds[['index', 'was_home']].copy()
    match_inds['was_home'] = match_inds['was_home'].replace({False: 0, True: 1})
    match_inds = match_inds.values.reshape((20, 38, 2))

    # - Add rating columns
    fixs['R_h'] = 0
    fixs['R_a'] = 0

    for ind in fixs[fixs['GW']==1].index:
        id_h, id_a = fixs.loc[ind, ['id_h', 'id_a']]
        fixs.loc[ind, ['R_h', 'R_a']] = ELO_init.loc[id_h, 'Initial_ELO'], ELO_init.loc[id_a, 'Initial_ELO']

    ind = 0
    mp = np.zeros(20, dtype=int)
    location = {1: 'R_h', 0: 'R_a'}
    while fixs.loc[ind, 'finished']:
        id_h, R_h, HG, id_a, R_a, AG = fixs.loc[ind, ['id_h', 'R_h', 'team_h_score', 'id_a', 'R_a', 'team_a_score']]

        Delta = HG - AG - (R_h - R_a + c)

        mp[id_h - 1] += 1
        mp[id_a - 1] += 1

        if mp[id_h-1]<38:
            next_ind, loc = match_inds[id_h-1, mp[id_h-1], :]
            fixs.loc[next_ind, location[loc]] = R_h + beta*Delta

        if mp[id_a-1]<38:
            next_ind, loc = match_inds[id_a-1, mp[id_a-1], :]
            fixs.loc[next_ind, location[loc]] = R_a - beta*Delta

        ind += 1

    return fixs[['matchid', 'id_h', 'id_a', 'R_h', 'R_a']]

def updateSeasonData():

    print('Processing fixtures...')
    fixlist = fpl.FixtureList(fixtures())

    home_fix = fixlist.fixtures[['matchid', 'id_h', 'GW', 'match_order']].rename(columns={'id_h': 'clubid'})
    home_fix['was_home'] = True
    away_fix = fixlist.fixtures[['matchid', 'id_a', 'GW', 'match_order']].rename(columns={'id_a': 'clubid'})
    away_fix['was_home'] = False

    # - Do not reset index yet, as this will facilitate applying ELO ratings
    all_fix = pd.concat((home_fix, away_fix), axis=0, sort=False)

    print('Calculating ELO ratings...')
    ELO_ratings = __applyELO(fixlist.fixtures, all_fix)
    home_ELO = ELO_ratings[['matchid', 'id_h', 'id_a', 'R_h', 'R_a']].rename(columns={'id_h': 'clubid',
                                                                                      'id_a': 'Opp_id',
                                                                              'R_h': 'ELO',
                                                                              'R_a': 'Opp_ELO'})

    away_ELO = ELO_ratings[['matchid', 'id_a', 'id_h', 'R_a', 'R_h']].rename(columns={'id_a': 'clubid',
                                                                              'id_h': 'Opp_id',
                                                                              'R_h': 'Opp_ELO',
                                                                              'R_a': 'ELO'})

    all_fix = all_fix.reset_index(drop=True)
    all_fix = __applymatchnumbering(all_fix)

    all_fix = all_fix.merge(pd.concat((home_ELO, away_ELO), axis=0, sort=False), on=['matchid', 'clubid'], how='left')

    print('Processing player histories...')
    # - Get current player_list
    playerlist = player_list()
    playerlist = playerlist[['id', 'web_name', 'team', 'element_type']]
    playerlist = playerlist.rename(columns={'web_name': 'name', 'team': 'clubid', 'element_type': 'position'})

    seasondata = pd.merge(all_fix, playerlist, on='clubid', how='left')

    id_list = playerlist['id'].to_list()
    playersummary = __allPlayerHistory(id_list)

    seasondata = seasondata.merge(playersummary, on=['id','matchid'], how='left')

    print('Saving...')
    filename = _current_dir() + 'seasonData.csv'
    seasondata.to_csv(filename, index=False)

    print('Complete.')
