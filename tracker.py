import time
import datetime
from nba_api.stats.endpoints import scoreboardv2

class tracker():

	def write_games(self, index, games_list):
		#Open the tracking file
		file = open('todays_games.txt', 'w')
		#Set the current game to finished
		games_list[index] = 1
		#Set it in the format for the text document
		for i, game in enumerate(games_list):
			if '\n' not in str(game):
				games_list[i] = f'{game}\n'
		#Write it to the file and close it
		file.writelines(games_list)
		file.close()

	def reset_games(self, offset, sleeping):
		total = []
		#Check how many games are on
		for i in range(len(scoreboardv2.ScoreboardV2(day_offset=offset, game_date=datetime.datetime.today()).game_header.get_data_frame())):
			if i == len(scoreboardv2.ScoreboardV2(day_offset=offset, game_date=datetime.datetime.today()).game_header.get_data_frame())-1:
				total.append('0')
			else:
				total.append('0\n')
		file = open('todays_games.txt', 'w')
		file.writelines(total)
		file.close()
		#If all the games have finished, don't check again for eight hours
		if sleeping:
			print('Sleeping for the night ...')
			time.sleep(28800)