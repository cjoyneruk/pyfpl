from .. import config
import requests
import json
import datetime

settings = config.get_settings()
current_dir = settings['DATA_PATH'] + 'Current_data/'
base_url = 'https://fantasy.premierleague.com/api/'

def file_retrieve(filename):

    with open(filename, 'r') as json_file:
        json_conf = json_file.read()

    return json.loads(json_conf)


def web_retrieve(url, email=None, pswd=None):

    print('Retrieving from {}'.format(url))
    jsonResponse = None

    try:
        if email is None:
            response = requests.get(url)
            jsonResponse = response.json()
        else:
            login_url = 'https://users.premierleague.com/accounts/login/'
            payload = {'password': pswd,
                       'login': email,
                       'redirect_uri': 'https://fantasy.premierleague.com/a/login',
                       'app': 'plfpl-web'}

            session = requests.session()
            session.post(login_url, data=payload)

            response = session.get(url)
            jsonResponse = response.json()

    except Exception as e:

        print('{}: Connection problems - please try again'.format(e))

    return jsonResponse


def file_save(json_data, filename):

    with open(filename, 'w') as out_file:
        json.dump(json_data, out_file)


def json_retrieve(filename, url):

    jsonResponse = None

    try:

        with open(filename, 'r') as json_file:
            json_conf = json_file.read()

        jsonResponse = json.loads(json_conf)

    except FileNotFoundError:

        print('Retrieving from {}'.format(url))

        try:

            response = requests.get(url)
            jsonResponse = response.json()

            with open(filename, 'w') as out_file:
                json.dump(jsonResponse, out_file)

        except Exception as e:

            print('{}: Connection problems - please try again'.format(e))

    return jsonResponse


def json_daily_retrieve(filename, url, email=None, pswd=None):

    today = datetime.date.today()

    try:

        json_wrap = file_retrieve(filename)

        # - If current date is newer than datestamp then update file
        datestamp = json_wrap['datestamp']
        recorded_date = datetime.date(datestamp[0], datestamp[1], datestamp[2])

        if recorded_date < today:
            print('{} out of date, updating...'.format(filename))
            json_data = web_retrieve(url, email=email, pswd=pswd)
            json_wrap = {'datestamp': [today.year, today.month, today.day],
                         'data': json_data}

            file_save(json_wrap, filename)

            return json_data

        else:

            return json_wrap['data']

    except FileNotFoundError:

        print('{} not found, updating...'.format(filename))
        # - if file not there then get from web and save
        json_data = web_retrieve(url, email=email, pswd=pswd)
        json_wrap = {'datestamp': [today.year, today.month, today.day],
                     'data': json_data}

        file_save(json_wrap, filename)

        return json_data
