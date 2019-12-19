import datetime
from nba_api.stats.static import teams
from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.endpoints import playerprofilev2
from nba_api.stats.endpoints import boxscoreadvancedv2

class set_data():
	def __init__(self):
		self.NBATeams = teams.get_teams()

	def create_data(self, game, dayOffset):
		gameStats = {
			'home': {},
			'away': {}
		}
		#Record the information on the teams playing
		game_line = scoreboardv2.ScoreboardV2(day_offset=dayOffset, game_date=datetime.datetime.today()).line_score.get_data_frame()
		for team in self.NBATeams:
			if team['id'] == game.HOME_TEAM_ID:
				ratio = [ratio['TEAM_WINS_LOSSES'] for index, ratio in game_line.iterrows() if ratio['TEAM_ID'] == team['id']]
				gameStats['home']['team_info'] = [team['full_name'], team['id'], ratio[0]]
			elif team['id'] == game.VISITOR_TEAM_ID:
				ratio = [ratio['TEAM_WINS_LOSSES'] for index, ratio in game_line.iterrows() if ratio['TEAM_ID'] == team['id']]
				gameStats['away']['team_info'] = [team['full_name'], team['id'], ratio[0]]
		#Create a dictionary that will store the stat leaders for each team
		for key in gameStats.keys():
			gameStats[key]['boxscore'] = {
				'Player_Points': ['', 0, 0],
				'Player_Assists': ['', 0, 0],
				'Player_Rebounds': ['', 0, 0],
				'Player_+/-': ['', 0, -99]
			}
		#Store the arena the game was played in
		gameStats['home']['team_info'].append(game['ARENA_NAME'])
		return gameStats

	def set_team_points(self, game, teamStats, gameStats):
		for i, team in teamStats.iterrows():
			if team.TEAM_ID == game.HOME_TEAM_ID:
				gameStats['home']['boxscore']['team_points'] = team.PTS
			elif team.TEAM_ID == game.VISITOR_TEAM_ID:
				gameStats['away']['boxscore']['team_points'] = team.PTS
		return gameStats

	def set_player_stats(self, boxScore, gameStats):
		advancedScore = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=boxScore.iloc[0].GAME_ID).player_stats.get_data_frame()
		for key in gameStats.keys():
			scoreLine = boxScore[boxScore.TEAM_ID == gameStats[key]['team_info'][1]]
			for ind, player in scoreLine.iterrows():
				#Record the individual leader for each statistical category
				if player.PTS > gameStats[key]['boxscore']['Player_Points'][2]:
					gameStats[key]['boxscore']['Player_Points'] = [player.PLAYER_NAME, player.PLAYER_ID, int(player.PTS)]
					gameStats[key]['boxscore']['Player_Points'].append(f'{int(player.FGM)}/{int(player.FGA)} FG, {int(player.FG3M)}/{int(player.FG3A)} 3P, {int(player.FTM)}/{int(player.FTA)} FT')
				if player.AST > gameStats[key]['boxscore']['Player_Assists'][2]:
					gameStats[key]['boxscore']['Player_Assists'] = [player.PLAYER_NAME, player.PLAYER_ID, int(player.AST)]
					gameStats[key]['boxscore']['Player_Assists'].append(f'{int(player.TO)} Turnovers')
				if player.REB > gameStats[key]['boxscore']['Player_Rebounds'][2]:
					gameStats[key]['boxscore']['Player_Rebounds'] = [player.PLAYER_NAME, player.PLAYER_ID, int(player.REB)]
					gameStats[key]['boxscore']['Player_Rebounds'].append(f'{int(player.OREB)} Offensive, {int(player.DREB)} Defensive')
				if player.PLUS_MINUS > int(gameStats[key]['boxscore']['Player_+/-'][2]):
					if player.PLUS_MINUS > 0:
						gameStats[key]['boxscore']['Player_+/-'] = [player.PLAYER_NAME, player.PLAYER_ID, '+'+str(int(player.PLUS_MINUS))]
					else:
						gameStats[key]['boxscore']['Player_+/-'] = [player.PLAYER_NAME, player.PLAYER_ID, int(player.PLUS_MINUS)]
					#Set the tagline using the advanced boxscore
					advancedPlayer = advancedScore[advancedScore.PLAYER_ID == player.PLAYER_ID]
					gameStats[key]['boxscore']['Player_+/-'].append(f'{int(advancedPlayer.iloc[0].POSS)} Possessions')
		return gameStats