from pandas.io.json import json_normalize
from pyfpl import retrieve
import datetime
import numpy as np

class Player:

    def __init__(self, json):

        for k, data in json.items():
            setattr(self, k, json_normalize(data))


class Team:

    def __crossref_picks(self):

        current_pl = retrieve.player_list()
        club_list = retrieve.club_summary()
        club_list = club_list.rename(columns={'id': 'team'})

        self.picks = self.picks.merge(current_pl[['id', 'web_name', 'team', 'now_cost',
                                                  'total_points', 'element_type']], on='id', how='left')
        self.picks = self.picks.merge(club_list[['team', 'name']], on='team', how='left')

        self.picks = self.picks.drop(columns='position')
        self.picks = self.picks.rename(columns={'web_name': 'player',
                                                'now_cost': 'value',
                                                'team': 'clubid',
                                                'name': 'club',
                                                'element_type': 'position'})

    def purchase_value(self):
        return self.picks['purchase_value'].sum()

    def current_value(self):
        return self.picks['value'].sum()

    def __repr__(self):

        cols = ['id', 'player', 'position', 'club', 'value', 'total_points']
        display = self.picks[cols].copy().set_index('id')
        display['position'] = display['position'].replace(dict(zip([1, 2, 3, 4], ['GLK', 'DEF', 'MID', 'FWD'])))

        return display.__repr__()


class HistoricTeam(Team):

    def __init__(self, json):

        self.active_chip = json['active_chip']
        self.automatic_subs = json['automatic_subs']
        self.entry_history = json_normalize(json['entry_history'])
        self.picks = json_normalize(json['picks'])

        if 'active_chip' not in json.keys():
            raise TypeError('Please retrieve using pyfpl.retrieve.team_history')

        self.picks = self.picks.rename(columns={'element': 'id'})

        gw = self.entry_history['event'].max()
        old_pl = retrieve.player_list(gw=(gw-1))
        self.picks = self.picks.merge(old_pl[['id', 'now_cost']], on='id', how='left')
        self.picks = self.picks.rename(columns={'now_cost': 'purchase_value'})

        self._Team__crossref_picks()


class CurrentTeam(Team):

    def __init__(self, json):

        for k, data in json.items():
            setattr(self, k, json_normalize(data))

        if 'chips' not in json.keys():
            raise TypeError('Please retrieve using pyfpl.retrieve.user_team')

        self.picks = self.picks.rename(columns={'element': 'id', 'purchase_price': 'purchase_value'})

        self._Team__crossref_picks()

    @property
    def essential(self):
        return self.picks[['id', 'position', 'clubid', 'selling_price']]

class League:

    def __init__(self, json):

        self.name = json['league']['name']
        self.id_ = json['league']['id']
        self.standings = json_normalize(json['standings']['results'])

    def __repr__(self):

        df = self.standings.sort_values(by='rank')
        df = df.set_index('rank')

        string = self.name + '\n'
        string += df[['player_name', 'entry_name', 'event_total', 'total']].__repr__()

        return string

class FixtureList:

    def __init__(self, json):

        self.fixtures = json_normalize(json)
        self.fixtures = self.fixtures.drop(columns=['stats', 'team_a_difficulty', 'team_h_difficulty'])
        self.fixtures = self.fixtures.rename(columns={'id': 'matchid', 'event': 'GW'})
        self.__crossref()
        self.__matchorder()

    def __crossref(self):

        club_list = retrieve.club_summary()
        club_list = club_list.rename(columns={'id': 'team'})
        self.fixtures = self.fixtures.rename(columns={'team_h': 'id_h', 'team_a': 'id_a'})

        self.fixtures = self.fixtures.merge(club_list[['team', 'name']], left_on='id_h', right_on='team', how='left')
        self.fixtures = self.fixtures.drop(columns='team')
        self.fixtures = self.fixtures.rename(columns={'name': 'club_h'})
        self.fixtures = self.fixtures.merge(club_list[['team', 'name']], left_on='id_a', right_on='team', how='left')
        self.fixtures = self.fixtures.drop(columns='team')
        self.fixtures = self.fixtures.rename(columns={'name': 'club_a'})

    def __matchorder(self):

        X = self.fixtures['kickoff_time'].str.split('T').copy()

        self.fixtures['Date'] = ''
        self.fixtures['Time'] = ''

        for ind in X.index:
            self.fixtures.loc[ind, ['Date', 'Time']] = X.loc[ind]

        Y = self.fixtures['Date'].str.split('-')
        Z = self.fixtures['Time'].str.split(':')

        for ind in Y.index:
            r = Y.loc[ind]
            s = Z.loc[ind]
            self.fixtures.loc[ind, 'kickoff_time'] = datetime.datetime(int(r[0]), int(r[1]), int(r[2]), int(s[0]), int(s[1]))

        self.fixtures = self.fixtures.drop(columns=['Date', 'Time'])
        self.fixtures = self.fixtures.sort_values(by=['kickoff_time', 'code'])
        self.fixtures['match_order'] = np.arange(0, 380, dtype=int)

    def __repr__(self):
        cols = ['club_h', 'club_a', 'team_h_score', 'team_a_score', 'finished']
        return self.fixtures[cols].__repr__()
