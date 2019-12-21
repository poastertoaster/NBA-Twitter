import time
#Classes
from check_data import check_data
from tracker import tracker
'''
TODO:
- Set it to only look every 5 minutes when a game has started, every hour otherwise
- Get the code to check if it has mentioned every game to prevent a nap before sleeping
  - Verify that it currently does both of these things
  - The code currently naps for an hour after the last game is over, but before it has a box score put out. This could potentially roll it over after midnight, grabbing the wrong number of games
- Move the code into smaller classes
- Redo the gameStats variable to be more concise (remove the initial dict and make it a list, etc)
'''
dayOffset = 0

tracker().reset_games(dayOffset, False)

while True:
	#Check if a game has started but hasn't finished
	while check_data().check_start(dayOffset):
		#Snooze before checking if a game has finished again
		print('Snoozing ...')
		time.sleep(300)
	#Nap for an hour until a game has started
	print('Napping ...')
	time.sleep(6000)