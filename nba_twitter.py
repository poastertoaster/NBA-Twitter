import time
#Classes
from check_data import check_data
from tracker import tracker
'''
TODO:
- Get the code to check if it has mentioned every game to prevent a nap before sleeping
  - Verify that it currently does both of these things
  - The code currently naps for an hour after the last game is over, but before it has a box score put out. This could potentially roll it over after midnight, grabbing the wrong number of games
- Move the code into smaller classes
- Redo the gameStats variable to be more concise (remove the initial dict and make it a list, etc)
- The app is snoozing after every game posted, instead of posting multiple games it has access to, due to the fact that it is returning the true or false after every game checked, instead of at the end.
  - Making the Check Tracker function independent of the Check Game function might fix this.
'''
dayOffset = 0

#tracker().reset_games(dayOffset, False)
gamesList = tracker().reset_games(dayOffset, False)

#Try a for loop that populates a list instead of a while loop checking against a long string of other functions
# - Rewrite the check data class so that it is only working on an individual game
# - Rewrite the while loop to check if a game has started but the tracker hasn't finished all the games

while True:
	#Check if a game has started but hasn't finished
	'''while check_data().check_start(dayOffset):
		#Snooze before checking if a game has finished again
		print('Snoozing ...')
		time.sleep(300)'''
	#As long as there are games that haven't been mentioned, keep checking the games
	while 0 in gamesList:
		#Get a list of games that have started
		gameStatus = check_data().check_start_2(dayOffset)
		#If a game has started ...
		if len(gameStatus) > 0:
			for game in gameStatus:
				#Check if that game is over
				if game[1] == 'Final':
					#If it is, go through the routine to mention it on the Twitter feed
					gamesList[game[0]] = check_data().check_game_2(game[0], dayOffset)
			#If there are games that still need to be mentioned, snooze for 5 minutes before checking again
			if 0 in gamesList:
				print('Snoozing ...')
				time.sleep(300)
			#If all the games have been mentioned, break out of the loop and set up for tomorrow's games
			else:
				gamesList = tracker().reset_games(dayOffset+1, True)
				break
		else:
			break
	#Nap for an hour until a game has started
	print('Napping ...')
	time.sleep(6000)