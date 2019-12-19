import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class image():
	def __init__(self):
		self.colors = {
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

	def create_image(self, gameStats):
		#Set the fonts
		score_font = ImageFont.truetype('Roboto-Black.TTF', 36)
		record_font = ImageFont.truetype('Roboto-Black.TTF', 12)
		#Generate the image
		createdImage = Image.new('RGB', (640, 360), color='white')
		drawing = ImageDraw.Draw(createdImage)
		#Create the colored backgrounds
		drawing.rectangle([0,0,320,360],fill=self.colors[gameStats['home']['team_info'][0]])
		drawing.rectangle([320,0,640,360],fill=self.colors[gameStats['away']['team_info'][0]])
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
				createdImage = image().draw_row(gameStats, createdImage, offset, key.replace('Player_', ''))
				offset += 75
		#Draw the Arena name
		arw, arh = drawing.textsize(f"{gameStats['home']['team_info'][3]}", font=record_font)
		drawing.rectangle([0, 345, 640, 360], fill='white')
		drawing.text((320-(arw/2), 358-arh), gameStats['home']['team_info'][3], fill=self.colors[gameStats['home']['team_info'][0]], font=record_font)
		#Save the image
		createdImage.save('image.png')
		
	def draw_row(self, gameStats, createdImage, yOffset, statType):
		#Set the fonts
		stat_font = ImageFont.truetype('Roboto-Black.TTF', 16)
		tag_font = ImageFont.truetype('Roboto-Medium.TTF', 12)

		drawing = ImageDraw.Draw(createdImage)
		#Home
		#Get Headshot
		headshot = image().get_headshot(gameStats['home']['team_info'][1], gameStats['home']['boxscore']['Player_'+statType][1])
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
		headshot = image().get_headshot(gameStats['away']['team_info'][1], gameStats['away']['boxscore']['Player_'+statType][1])
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

	def get_headshot(self, team_id, player_id):
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
		#Open the saved headshot and resize it
		headshot = Image.open('headshot.png').convert("RGBA")
		headshot.thumbnail((82, 60), resample=Image.BILINEAR)
		#Hand the headshot data back
		return headshot