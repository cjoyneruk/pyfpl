from pyfpl import retrieve
import pyfpl as fpl

#### Example of how to update data from the fpl API

# - Get current gameweek data
jdata = retrieve.gw_summary()

# - Update player information
retrieve.update_player_info()

# - Process the above data into a formatted csv
retrieve.updateSeasonData()

# - Get current team by logging in with user
my_team = fpl.CurrentTeam(retrieve.user_team('user'))
print(my_team)
more_info = my_team.picks
print(more_info)

# - Get league information for user
league_id = 101
league = fpl.League(retrieve.league('user', league_id))
print(league)

# - Update team histories of those in league
team_ids = league.standings['entry'].values
for id_ in team_ids:

    retrieve.update_team_history(id_=id_, gw='all')

# - Get details for team in first place from gameweek 2
team1 = team_ids[0]
other_team = fpl.HistoricTeam(retrieve.team_history(id_=team1, gw=2))
print(other_team)