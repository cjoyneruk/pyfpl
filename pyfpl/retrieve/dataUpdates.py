from .objectRetrieval import *
from .base import _current_dir

def update_team_history(id_, gw=None):

    cgw = current_gw()

    if gw is None:

        print('Updating gameweek {}'.format(cgw))
        filename = 'team_history/' + str(id_) + '_' + 'GW-' + str(cgw).zfill(2) + '.json'
        url = 'entry/' + str(id_) + '/event/' + str(cgw) + '/picks/'
        json_data = web_retrieve(url)
        file_save(json_data, filename)

    elif isinstance(gw, str):

        if gw != 'all':
            raise ValueError('The keyword argument {} is not recognised'.format(gw))
        else:

            for x in range(1, cgw+1):
                print('Updating gameweek {}'.format(x))
                filename = 'team_history/' + str(id_) + '_' + 'GW-' + str(x).zfill(2) + '.json'
                url = 'entry/' + str(id_) + '/event/' + str(x) + '/picks/'
                json_data = web_retrieve(url)
                file_save(json_data, filename)

    elif isinstance(gw, int):

        if gw > current_gw():

            raise ValueError('The requested gameweek is not available yet')

        else:
            print('Updating gameweek {}'.format(gw))
            filename = 'team_history/' + str(id_) + '_' + 'GW-' + str(gw).zfill(2) + '.json'
            url = 'entry/' + str(id_) + '/event/' + str(gw) + '/picks/'
            json_data = web_retrieve(url)
            file_save(json_data, filename)


def update_player_info():

    pl = player_list()
    N = pl.shape[0]

    for i, ind in enumerate(pl.index):

        name, id_ = pl.loc[ind, ['web_name', 'id']]
        print('[{:.1f}%] {} ({})'.format(100*i/N, name, id_))

        url = 'element-summary/' + str(id_) + '/'
        filename = 'players/player_' + str(id_).zfill(3) + '.json'

        jsonResponse = web_retrieve(url)

        if len(jsonResponse)==0:
            raise ValueError('{} is not returning any data, try again later'.format(url))
        file_save(jsonResponse, filename)
        time.sleep(1)

def add_new_predictions(df, gw):

    filename = _current_dir() + 'Predictions/GW' + str(gw) + '_predictions.csv'

    df.to_csv(filename, index=False)