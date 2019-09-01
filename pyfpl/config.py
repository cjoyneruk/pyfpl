import os
import json

path = os.environ['PATH'].split(':')[0]
filename = path + '/pyfpl_config.json'

def _do_nothing(*args):
    pass


def _data_fnc_no(settings):
    print('Please enter new path')
    new_path = input()
    settings['DATA_PATH'] = new_path


def _del_user(settings, user):
    settings['USER_LIST'].remove(user)
    string = user + '_DETAILS'
    del settings[string]
    print("User '{}' deleted".format(user))


def _edit_user(settings, user):
    userdetails = user + '_DETAILS'
    print('')
    print('Enter new email address ({})'.format(settings[userdetails]['EMAIL']))
    email = input()
    settings[userdetails]['EMAIL'] = email

    print('')
    print('Enter new password ({})'.format(settings[userdetails]['PWD']))
    password = input()
    settings[userdetails]['PWD'] = password

    print('')
    print('Enter new team id ({})'.format(settings[userdetails]['TEAMID']))
    cont = True
    while cont:
        teamid = input()
        try:
            settings[userdetails]['TEAMID'] = int(teamid)
            cont = False
        except ValueError:
            print('You must enter an integer for the team id:')

def _add_user(settings):

    print('Name for user:')
    user = input()
    if user in settings['USER_LIST']:
        print("User '{}' already in user list, please enter another name".format(user))
    else:
        settings['USER_LIST'].append(user)
        userdetails = user + '_DETAILS'

        settings[userdetails] = {}

        print("Enter email for '{}'".format(user))
        email = input()
        settings[userdetails]['EMAIL'] = email

        print("Enter password for '{}'".format(user))
        pswd = input()
        settings[userdetails]['PWD'] = pswd

        print("Enter team ID for '{}'".format(user))
        cont = True
        while cont:
            teamid = input()
            try:
                settings[userdetails]['TEAMID'] = int(teamid)
                cont = False
            except ValueError:
                print('You must enter an integer for the team id:')


def _keep_user_no(settings, user):
    print("Are you sure you want to remove user '{}'? y/n".format(user))
    _check_fnc(settings, user, y_fnc=_del_user)


def _check_fnc(*args, y_fnc=_do_nothing, n_fnc=_do_nothing):
    y_ans = ['Y', 'y', 'Yes', 'yes', 'YES']
    n_ans = ['N', 'n', 'No', 'no', 'NO']

    while True:
        a = input()
        if a in y_ans:
            y_fnc(*args)
            return True
        elif a in n_ans:
            n_fnc(*args)
            return False
        else:
            print("Please enter either 'y' or 'n'")


def get_settings():

    try:
        with open(filename, 'r') as config_file:
            json_conf = config_file.read()

        return json.loads(json_conf)

    except FileNotFoundError:

        print('Please run setup')


def update_settings():

    try:
        with open(filename, 'r') as config_file:
            json_conf = config_file.read()

        settings = json.loads(json_conf)

        # - Either keep or change current data directory
        print("Keep the current data directory as \n '{}'? y/n".format(settings['DATA_PATH']))
        _check_fnc(settings, n_fnc=_data_fnc_no)

        # - Display user list
        print('')
        print('Current users:')
        for user in settings['USER_LIST']:
            print(user)

        # - Keep/remove and/or edit users
        print('')
        user_list = settings['USER_LIST'].copy()
        for user in user_list:
            print("Keep user '{}'? y/n".format(user))
            _check_fnc(settings, user, n_fnc=_keep_user_no)

            if user in settings['USER_LIST']:
                print("Would you like to edit settings for '{}'? y/n".format(user))
                _check_fnc(settings, user, y_fnc=_edit_user)

        # - Add other users
        response_1 = True
        while response_1:
            print('')
            print('Would you like to add another user? y/n')
            response_1 = _check_fnc(settings, y_fnc=_add_user)

        with open(filename, 'w') as config_file:
            json.dump(settings, config_file)

    except FileNotFoundError:
        print('Please run setup')


def setup():

    settings = {}

    print('Enter path for data storage')
    settings['DATA_PATH'] = input()

    settings['USER_LIST'] = []

    # - Add initial user
    print('')
    print('Would you like to add a user? y/n')
    response_0 = _check_fnc(settings, y_fnc=_add_user)

    # - Add more users
    if response_0:

        response_1 = True
        while response_1:
            print('')
            print('Would you like to add another user? y/n')
            response_1 = _check_fnc(settings, y_fnc=_add_user)

    with open(filename, 'w') as config_file:
        json.dump(settings, config_file)