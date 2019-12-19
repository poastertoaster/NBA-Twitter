import datetime
from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.endpoints import boxscoretraditionalv2
#Classes
from image import image
from set_data import set_data
from tracker import tracker

class check_data():

	def check_game(self, game_index, games_list, dayOffset):
		todaysGames = scoreboardv2.ScoreboardV2(day_offset=dayOffset, game_date=datetime.datetime.today()).game_header.get_data_frame()
		#Go through all of the games for today
		game = todaysGames.iloc[game_index]
		gameStats = set_data().create_data(game, dayOffset)
		#If the game is over ...
		if game.GAME_STATUS_TEXT == 'Final':
			#Grab the game stat line
			teamStats = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game.GAME_ID).team_stats.get_data_frame()
			#Check for the team's collective stats
			gameStats = set_data().set_team_points(game, teamStats, gameStats)
			#Check that the box score has a final total
			if gameStats['home']['boxscore']['team_points'] != None:
				#Grab the boxscore
				boxScore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game.GAME_ID).player_stats.get_data_frame()
				#Set this game to complete in the tracking file
				tracker().write_games(game_index, games_list)
				#Set the category leaders
				gameStats = set_data().set_player_stats(boxScore, gameStats)
				#Create the image summary
				image().create_image(gameStats)
				#Print the tagline for the game.
				if gameStats['home']['boxscore']['team_points'] > gameStats['away']['boxscore']['team_points']:
					status = f"The {gameStats['home']['team_info'][0]} defeat the {gameStats['away']['team_info'][0]} {gameStats['home']['boxscore']['team_points']}-{gameStats['away']['boxscore']['team_points']} off of {gameStats['home']['boxscore']['Player_Points'][2]} points from {gameStats['home']['boxscore']['Player_Points'][0]}."
				else:
					status = f"The {gameStats['away']['team_info'][0]} defeat the {gameStats['home']['team_info'][0]} {gameStats['away']['boxscore']['team_points']}-{gameStats['home']['boxscore']['team_points']} off of {gameStats['away']['boxscore']['Player_Points'][2]} points from {gameStats['away']['boxscore']['Player_Points'][0]}."
				print(status)
			#When the last game has been checked, set up for tomorrow
			games_list = list(map(lambda game: game.replace('\n', ''), games_list))
			if '0' not in games_list:
				tracker().reset_games(1, True)
				#Break the snooze loop
				return False
			else:
				#Continue the snooze loop if there are more games to check
				return True

	def check_tracker(self, dayOffset):
		games_list = []
		#Open the tracking file
		with open("todays_games.txt") as file:
			#Filter the data in the file to create an iterable list
			for cnt, line in enumerate(file):
				games_list.append(line)
			file.close()
			#Go through the data in the list and check games that haven't finished
			for index, game in enumerate(games_list):
				if int(game) == 0:
					check_data().check_game(index, games_list, dayOffset)

	def check_start(self, dayOffset):
		#Check the games for today
		todaysGames = scoreboardv2.ScoreboardV2(day_offset=dayOffset, game_date=datetime.datetime.today()).game_header.get_data_frame()
		#If a game has started keep going. If not, go back to napping.
		gamesStarted = [[index, game['GAME_STATUS_TEXT']] for index, game in todaysGames.iterrows() if 'ET' not in game['GAME_STATUS_TEXT']]
		if len(gamesStarted) > 0:
			gamesFinished = [finished[0] for finished in gamesStarted if finished[1] == 'Final']
			#If a game has finished run the rest of the script
			if len(gamesFinished) > 0:
				return check_data().check_tracker(dayOffset)
				'''#If there are games that haven't finished, continue waiting to check them
				if len(gamesFinished) != len(todaysGames):
					return True
				#If all the games have finished, break the loop and go to sleep
				else:
					return False'''
			#If a game hasn't finished, snooze until it's over
			else:
				return False