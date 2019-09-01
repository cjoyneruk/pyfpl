from .. import config
import requests
import json
import datetime

_base_url = 'https://fantasy.premierleague.com/api/'

def _current_dir():
    settings = config.get_settings()
    return settings['DATA_PATH'] + 'Current_data/'

def file_retrieve(filename):

    with open(_current_dir() + filename, 'r') as json_file:
        json_conf = json_file.read()

    return json.loads(json_conf)


def web_retrieve(url, email=None, pwd=None):

    print('Retrieving from {}'.format(_base_url + url))
    jsonResponse = None

    try:
        if email is None:
            response = requests.get(_base_url + url)
            jsonResponse = response.json()
        else:
            login_url = 'https://users.premierleague.com/accounts/login/'
            payload = {'password': pwd,
                       'login': email,
                       'redirect_uri': 'https://fantasy.premierleague.com/a/login',
                       'app': 'plfpl-web'}

            session = requests.session()
            session.post(login_url, data=payload)

            response = session.get(_base_url + url)
            jsonResponse = response.json()

    except Exception as e:

        print('{}: Connection problems - please try again'.format(e))

    return jsonResponse


def file_save(json_data, filename):

    with open(_current_dir() + filename, 'w') as out_file:
        json.dump(json_data, out_file)


def json_retrieve(filename, url):

    jsonResponse = None

    try:

        with open(_current_dir() + filename, 'r') as json_file:
            json_conf = json_file.read()

        jsonResponse = json.loads(json_conf)

    except FileNotFoundError:

        print('Retrieving from {}'.format(_base_url + url))

        try:

            response = requests.get(_base_url + url)
            jsonResponse = response.json()

            with open(_current_dir() + filename, 'w') as out_file:
                json.dump(jsonResponse, out_file)

        except Exception as e:

            print('{}: Connection problems - please try again'.format(e))

    return jsonResponse


def json_daily_retrieve(filename, url, email=None, pwd=None):

    today = datetime.date.today()

    try:

        json_wrap = file_retrieve(filename)

        # - If current date is newer than datestamp then update file
        datestamp = json_wrap['datestamp']
        recorded_date = datetime.date(datestamp[0], datestamp[1], datestamp[2])

        if recorded_date < today:
            print('{} out of date, updating...'.format(_current_dir() + filename))
            json_data = web_retrieve(url, email=email, pwd=pwd)
            json_wrap = {'datestamp': [today.year, today.month, today.day],
                         'data': json_data}

            file_save(json_wrap, filename)

            return json_data

        else:

            return json_wrap['data']

    except FileNotFoundError:

        print('{} not found, updating...'.format(filename))
        # - if file not there then get from web and save
        json_data = web_retrieve(url, email=email, pwd=pwd)
        json_wrap = {'datestamp': [today.year, today.month, today.day],
                     'data': json_data}

        file_save(json_wrap, filename)

        return json_data
