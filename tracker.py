import time
import datetime
from nba_api.stats.endpoints import scoreboardv2

class tracker():

	def check_games(self):
		#Open the tracking file
		file = open("todays_games.txt", "r")
		#Filter the data in the file to create an iterable list
		gamesString = str(file.read().strip())
		games_list = gamesString.split(",")
		file.close()
		return games_list

	def reset_games(self, offset, sleeping):
		gamesList = []
		#Check how many games are on
		for i in range(len(scoreboardv2.ScoreboardV2(day_offset=offset, game_date=datetime.datetime.today()).game_header.get_data_frame())):
			gamesList.append(0)
		#If all the games have finished, don't check again for eight hours
		if sleeping:
			print('Sleeping for the night ...')
			time.sleep(28800)
		return gamesList