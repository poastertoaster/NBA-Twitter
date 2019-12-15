import datetime
from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.endpoints import boxscoreadvancedv2

PHXSuns = '0021900349'
#1626164

wlratio = scoreboardv2.ScoreboardV2(day_offset=-1, game_date=datetime.datetime.today()).line_score.get_data_frame()
for index, game in wlratio.iterrows():
	print(game['TEAM_ID'], game['TEAM_WINS_LOSSES'])