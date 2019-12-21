import tweepy

#Set Twitter information
auth = tweepy.OAuthHandler('Consumer Key', 'Consumer Secret')
auth.set_access_token('Access Token', 'Access Secret')
api = tweepy.API(auth)

class update_twitter():

	def send_update(self, statusUpdate):
		uploadedImage = api.media_upload('image.png')
		api.update_status(status=statusUpdate, media_ids=[uploadedImage.media_id])