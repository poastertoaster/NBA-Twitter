import time
import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from nba_api.stats.static import teams
from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.endpoints import playerprofilev2
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import boxscoreadvancedv2

'''
TODO:
- Set it to only look every 5 minutes when a game has started, every hour otherwise
- Get the code to check if it has mentioned every game to prevent a nap before sleeping
  - Verify that it currently does both of these things
  - The code currently naps for an hour after the last game is over, but before it has a box score put out. This could potentially roll it over after midnight, grabbing the wrong number of games
- Divide the code into classes
- Remove the tracking file by storing the games for today in a list generated from the number of games. I don't see the point anymore.
'''

NBATeams = teams.get_teams()
dayOffset = 0
colors = {
	'Atlanta Hawks': '#e03a3e',
	'Boston Celtics': '#007A33',
	'Brooklyn Nets': '#000000',
	'Charlotte Hornets': '#00788C',
	'Chicago Bulls': '#CE1141',
	'Cleveland Cavaliers': '#6F263D',
	'Dallas Mavericks': '#002B5e',
	'Denver Nuggets': '#0E2240',
	'Detroit Pistons': '#C8102E',
	'Golden State Warriors': '#006BB6',
	'Houston Rockets': '#CE1141',
	'Indiana Pacers': '#FDBB30',
	'Los Angeles Clippers': '#c8102E',
	'Los Angeles Lakers': '#FDB927',
	'Memphis Grizzlies': '#5D76A9',
	'Miami Heat': '#98002E',
	'Milwaukee Bucks': '#00471B',
	'Minnesota Timberwolves': '#236192',
	'New Orleans Pelicans': '#0C2340',
	'New York Knicks': '#006BB6',
	'Oklahoma City Thunder': '#007ac1',
	'Orlando Magic': '#0077c0',
	'Philadelphia 76ers': '#006bb6',
	'Phoenix Suns': '#1d1160',
	'Portland Trail Blazers': '#E03A3E',
	'Sacramento Kings': '#5a2d81',
	'San Antonio Spurs': '#000000',
	'Toronto Raptors': '#ce1141',
	'Utah Jazz': '#002B5C',
	'Washington Wizards': '#e31837'
}

def check_game(game_index, games_list):
	todaysGames = scoreboardv2.ScoreboardV2(day_offset=dayOffset, game_date=datetime.datetime.today()).game_header.get_data_frame()
	#Go through all of the games for today
	game = todaysGames.iloc[game_index]
	gameStats = create_data(game)
	#If the game is over ...
	if game.GAME_STATUS_TEXT == 'Final':
		#Grab the game stat line
		teamStats = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game.GAME_ID).team_stats.get_data_frame()
		#Check for the team's collective stats
		gameStats = set_team_points(game, teamStats, gameStats)
		#Check that the box score has a final total
		if gameStats['home']['boxscore']['team_points'] != None:
			#Grab the boxscore
			boxScore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game.GAME_ID).player_stats.get_data_frame()
			#Set this game to complete in the tracking file
			write_games(game_index, games_list)
			#Set the category leaders
			gameStats = set_player_stats(boxScore, gameStats)
			#Create the image summary
			create_image(gameStats)
			#Print the tagline for the game.
			if gameStats['home']['boxscore']['team_points'] > gameStats['away']['boxscore']['team_points']:
				status = f"The {gameStats['home']['team_info'][0]} defeat the {gameStats['away']['team_info'][0]} {gameStats['home']['boxscore']['team_points']}-{gameStats['away']['boxscore']['team_points']} off of {gameStats['home']['boxscore']['Player_Points'][2]} points from {gameStats['home']['boxscore']['Player_Points'][0]}."
			else:
				status = f"The {gameStats['away']['team_info'][0]} defeat the {gameStats['home']['team_info'][0]} {gameStats['away']['boxscore']['team_points']}-{gameStats['home']['boxscore']['team_points']} off of {gameStats['away']['boxscore']['Player_Points'][2]} points from {gameStats['away']['boxscore']['Player_Points'][0]}."
			print(status)
		#When the last game has been checked, set up for tomorrow
		games_list = list(map(lambda game: game.replace('\n', ''), games_list))
		if '0' not in games_list:
			reset_games(1, True)
			return True
		else:
			return False

def check_tracker():
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
				return check_game(index, games_list)

def check_start():
	#Check the games for today
	todaysGames = scoreboardv2.ScoreboardV2(day_offset=dayOffset, game_date=datetime.datetime.today()).game_header.get_data_frame()
	#If a game has started keep going. If not, go back to napping.
	gamesStarted = [[index, game['GAME_STATUS_TEXT']] for index, game in todaysGames.iterrows() if 'ET' not in game['GAME_STATUS_TEXT']]
	if len(gamesStarted) > 0:
		gamesFinished = [finished[0] for finished in gamesStarted if finished[1] == 'Final']
		#If a game has finished run the rest of the script
		if len(gamesFinished) > 0:
			return check_tracker()
			'''#If there are games that haven't finished, continue waiting to check them
			if len(gamesFinished) != len(todaysGames):
				return True
			#If all the games have finished, break the loop and go to sleep
			else:
				return False'''
		#If a game hasn't finished, snooze until it's over
		else:
			return False

def write_games(index, games_list):
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

def reset_games(offset, sleeping):
	total = []
	#Check how many games are on tomorrow
	for i in range(len(scoreboardv2.ScoreboardV2(day_offset=offset, game_date=datetime.datetime.today()).game_header.get_data_frame())):
		if i == len(scoreboardv2.ScoreboardV2(day_offset=offset, game_date=datetime.datetime.today()).game_header.get_data_frame())-1:
			total.append('0')
		else:
			total.append('0\n')
	file = open('todays_games.txt', 'w')
	file.writelines(total)
	file.close()
	if sleeping:
		#If all the games have finished, don't check again for eight hours
		print('Sleeping for the night ...')
		time.sleep(28800)

def create_data(game):
	gameStats = {
		'home': {},
		'away': {}
	}
	#Record the information on the teams playing
	game_line = scoreboardv2.ScoreboardV2(day_offset=dayOffset, game_date=datetime.datetime.today()).line_score.get_data_frame()
	for team in NBATeams:
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

def set_team_points(game, teamStats, gameStats):
	for i, team in teamStats.iterrows():
		if team.TEAM_ID == game.HOME_TEAM_ID:
			gameStats['home']['boxscore']['team_points'] = team.PTS
		elif team.TEAM_ID == game.VISITOR_TEAM_ID:
			gameStats['away']['boxscore']['team_points'] = team.PTS
	return gameStats

def set_player_stats(boxScore, gameStats):
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

def create_image(gameStats):
	#Set the fonts
	score_font = ImageFont.truetype('Roboto-Black.TTF', 36)
	record_font = ImageFont.truetype('Roboto-Black.TTF', 12)

	createdImage = Image.new('RGB', (640, 360), color='white')
	drawing = ImageDraw.Draw(createdImage)
	#Create the colored backgrounds
	drawing.rectangle([0,0,320,360],fill=colors[gameStats['home']['team_info'][0]])
	drawing.rectangle([320,0,640,360],fill=colors[gameStats['away']['team_info'][0]])
	drawing.line([320, 0, 320, 360], fill='white', width=1)
	#Draw the team's scoring
	sHw, sHh = drawing.textsize(str(gameStats['home']['boxscore']['team_points']), font=score_font)
	drawing.text((315-sHw, 5), str(gameStats['home']['boxscore']['team_points']), font=score_font, fill='white')
	drawing.text((325, 5), str(gameStats['away']['boxscore']['team_points']), font=score_font, fill='white')
	#Draw the team's record
	rHw, rHh = drawing.textsize(f"({gameStats['home']['team_info'][2]})", font=record_font)
	rAw, rAh = drawing.textsize(f"({gameStats['away']['team_info'][2]})", font=record_font)
	drawing.text((214-(rHw/2), 26-(rHh/2)), f"({gameStats['home']['team_info'][2]})", font=record_font)
	drawing.text((426-(rAw/2), 26-(rAh/2)), f"({gameStats['away']['team_info'][2]})", font=record_font)
	#Draw the team's logo
	homeLogo = Image.open('team_logos/'+gameStats['home']['team_info'][0].replace(' ','_')+ '.png')
	homeLogo.thumbnail((40, 40), resample=Image.BILINEAR)
	createdImage.paste(homeLogo, box=(140,5), mask=homeLogo)
	awayLogo = Image.open('team_logos/'+gameStats['away']['team_info'][0].replace(' ','_')+ '.png')
	awayLogo.thumbnail((40, 40), resample=Image.BILINEAR)
	createdImage.paste(awayLogo, box=(460,5), mask=awayLogo)
	#Draw the Rows
	offset = 60
	for key in gameStats['home']['boxscore']:
		if key != 'team_points':
			createdImage = draw_row(gameStats, createdImage, offset, key.replace('Player_', ''))
			offset += 75
	#Draw the Arena name
	arw, arh = drawing.textsize(f"{gameStats['home']['team_info'][3]}", font=record_font)
	drawing.rectangle([0, 345, 640, 360], fill='white')
	drawing.text((320-(arw/2), 358-arh), gameStats['home']['team_info'][3], fill=colors[gameStats['home']['team_info'][0]], font=record_font)
	createdImage.save('image.png')
	
def draw_row(gameStats, createdImage, yOffset, statType):
	stat_font = ImageFont.truetype('Roboto-Black.TTF', 16)
	tag_font = ImageFont.truetype('Roboto-Medium.TTF', 12)

	drawing = ImageDraw.Draw(createdImage)
	#Home
	#Get Headshot
	headshot = get_headshot(gameStats['home']['team_info'][1], gameStats['home']['boxscore']['Player_'+statType][1])
	createdImage.paste(headshot, box=(5,yOffset), mask=headshot)
	#Draw Text
	drawing.text((80, yOffset-10), statType, font=stat_font, fill='white')
	hPNw, hPNh = drawing.textsize(str(gameStats['home']['boxscore']['Player_'+statType][0]+' -'), font=stat_font)
	hPTw, hPTh = drawing.textsize(str(gameStats['home']['boxscore']['Player_'+statType][2]), font=stat_font)
	hTw, hTh = drawing.textsize(gameStats['home']['boxscore']['Player_'+statType][3], font=tag_font)
	drawing.text((315-hPTw, yOffset+55-hPTh), str(gameStats['home']['boxscore']['Player_'+statType][2]), font=stat_font, fill='white')
	drawing.text((310-hPTw-hPNw, yOffset+55-hPTh), str(gameStats['home']['boxscore']['Player_'+statType][0]+' -'), font=stat_font, fill='white')
	drawing.text((315-hTw, yOffset+52-hPTh-hTh), str(gameStats['home']['boxscore']['Player_'+statType][3]), font=tag_font, fill='white')
	#Away
	#Get Headshot
	headshot = get_headshot(gameStats['away']['team_info'][1], gameStats['away']['boxscore']['Player_'+statType][1])
	createdImage.paste(headshot, box=(553,yOffset), mask=headshot)
	#Draw Text
	sPw, sPh = drawing.textsize(statType, font=stat_font)
	drawing.text((560-sPw, yOffset-10), statType, font=stat_font, fill='white')
	aPNw, aPNh = drawing.textsize('- '+str(gameStats['away']['boxscore']['Player_'+statType][0]), font=stat_font)
	aPTw, aPTh = drawing.textsize(str(gameStats['away']['boxscore']['Player_'+statType][2]), font=stat_font)
	aTw, aTh = drawing.textsize(gameStats['away']['boxscore']['Player_'+statType][3], font=tag_font)
	drawing.text((325, yOffset+55-aPTh), str(gameStats['away']['boxscore']['Player_'+statType][2]), font=stat_font, fill='white')
	drawing.text((330+aPTw, yOffset+55-aPTh), '- '+str(gameStats['away']['boxscore']['Player_'+statType][0]), font=stat_font, fill='white')
	drawing.text((325, yOffset+52-aPTh-aTh), str(gameStats['away']['boxscore']['Player_'+statType][3]), font=tag_font, fill='white')
	#Draw bottom line
	drawing.line([5, yOffset+60, 635, yOffset+60], fill='white', width=1)
	return createdImage

def get_headshot(team_id, player_id):
	#Get the player's headshot for their team
	headshot = requests.get(f'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/{team_id}/2019/260x190/{player_id}.png')
	if headshot.status_code == 403:
		#If they don't have a team headshot, get their latest headshot
		headshot = requests.get(f'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png')
		#If none of the headshots are available, get the default fallback
		if headshot.status_code == 403:
			headshot = requests.get('https://stats.nba.com/media/img/league/nba-headshot-fallback.png')
	imageData = Image.open(BytesIO(headshot.content))
	imageData.save('headshot.png')
	headshot = Image.open('headshot.png').convert("RGBA")
	headshot.thumbnail((82, 60), resample=Image.BILINEAR)
	return headshot

reset_games(dayOffset, False)

while True:
	#Check if a game has started but hasn't finished
	while check_start():
		print('Snoozing ...')
		time.sleep(300)
	#Repeat the process every 5 minutes
	print('Napping ...')
	time.sleep(6000)