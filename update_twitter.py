import tweepy

#Set Twitter information
auth = tweepy.OAuthHandler('uUX7QohSIfgzJS1qLKj52VQxm', 'KnSKRR4qfzigpPRNBiGpMFHsKBdfQCul8KGS9H2WPuUpmyTRPb')
auth.set_access_token('1208449656193052672-02mOgavTOUalvUvi1EafYU9SP0wpSF', 'XNn5tfkg1zRcAKWRnE6aSildCZqwYMTNyrAVdEZ5vi77A')
api = tweepy.API(auth)

class update_twitter():

	def send_update(self, statusUpdate):
		uploadedImage = api.media_upload('image.png')
		api.update_status(status=statusUpdate, media_ids=[uploadedImage.media_id])