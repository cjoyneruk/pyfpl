import pandas as pd
from pandas.io.json import json_normalize
from .base import *
import time
from .base import _current_dir


def current_gw():

    gw_deadlines = pd.read_csv(_current_dir() + 'gameweek_deadlines.csv')
    current_time = time.time()
    return gw_deadlines.loc[gw_deadlines['deadline_time_epoch']<current_time, 'GW'].values.max()


def next_deadline(gw=None):

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    months = ['January', 'February', 'March', 'April', 'May',
              'June', 'July', 'August', 'September', 'October',
              'November', 'December']

    gw_deadlines = pd.read_csv(_current_dir() + 'gameweek_deadlines.csv')
    if gw is None:
        gw = current_gw()

    t = datetime.datetime.fromtimestamp(gw_deadlines.loc[gw, 'deadline_time_epoch'])

    date_string = days[t.weekday()] + ' ' + str(t.day)
    if t.day == 1:
        date_string += 'st '
    elif t.day == 2:
        date_string += 'nd '
    elif t.day == 3:
        date_string += 'rd '
    else:
        date_string += 'th '

    date_string += months[t.month-1] + ' - ' + str(t.hour) + ':' + str(t.minute).zfill(2)

    return date_string


def team_history(id_, gw=None):

    if gw is None:
        gw = current_gw()
    elif gw > current_gw():
        raise ValueError('The requested gameweek is not available yet')

    filename = 'team_history/' + str(id_) + '_' + 'GW-' + str(gw).zfill(2) + '.json'

    try:

        return file_retrieve(filename)

    except FileNotFoundError as e:

        print('{}: Problem retrieving file'.format(e))
        print("Consider running 'update_team_history'")

        return None


def gw_summary(gw=None):

    if gw is None:
        gw = current_gw()
    elif gw > current_gw():
        raise ValueError('The requested gameweek is not available yet')

    filename = 'gameweek_summary/summary_GW-' + str(gw).zfill(2) + '.json'
    url = 'bootstrap-static/'

    if gw < current_gw():

        # - return file
        json_wrap = file_retrieve(filename)

        return json_wrap['data']

    elif gw == current_gw():

        return json_daily_retrieve(filename, url)


def club_summary(gw=None):

    if gw is None:
        gw = current_gw()

    data = gw_summary(gw)

    return json_normalize(data['teams'])


def player_list(gw=None):

    if gw is None:
        gw = current_gw()

    data = gw_summary(gw)

    return json_normalize(data['elements'])


def fixtures():

    filename = 'fixtures.json'
    url = 'fixtures'

    return json_daily_retrieve(filename, url)



def player(id_):

    filename = 'players/player_' + str(id_).zfill(3) + '.json'

    return file_retrieve(filename)


def user_team(name):

    settings = config.get_settings()
    user = name + '_DETAILS'
    details = settings[user]

    filename = 'user_teams/' + name + '_' + str(details['TEAMID']) + '.json'
    url = 'my-team/' + str(details['TEAMID']) + '/'

    return json_daily_retrieve(filename, url, email=details['EMAIL'], pwd=details['PWD'])


def league(name, league_id):

    settings = config.get_settings()

    user = name + '_DETAILS'
    details = settings[user]

    filename = 'league_standings/' + str(league_id) + '.json'
    url = 'leagues-classic/' + str(league_id) + '/standings/'

    return json_daily_retrieve(filename, url, email=details['EMAIL'], pwd=details['PWD'])