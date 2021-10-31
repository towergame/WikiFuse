from whapi import random_article, return_details, get_images
import random
from twitter import *
import base64
import json
import requests
import time
from datetime import datetime, timedelta
from discord_webhook import DiscordWebhook

with open('auth.json') as json_file:
    data = json.load(json_file) # load the json config file
	# JSON format:
'''
	{
		"token": "the oauth key",
		"token_secret": "the oauth key secret",
		"api_key": "the consumer api key",
		"api_key_secret": "the consumer api key secret",
		"webhook": "discord webhook url to log to"
	} 
'''


# Logs something to the standard output and a specified discord webhook
# Formatted as: LOGTYPE: string
def log(logtype, string):
	webhook = DiscordWebhook(url=data["webhook"], rate_limit_retry=True, content= "**" + logtype + "**" + ": ```" + string + "```")
	response = webhook.execute()
	print(logtype + ": " + string)

# Twitter API
t = Twitter(
    auth=OAuth(data["token"], data["token_secret"], data["api_key"], data["api_key_secret"]))

def do_stuff(): # the main function
	info = return_details(random_article()) # get a random article
	# print(info["title"])	

	def get_random_image(): # gets a random image
		image_theft = random_article() # gets article
		image_info = return_details(image_theft) # its details (link)
		image_list = get_images(image_theft) # and the images in it
		filtered_list = []
		for im in image_list:
			if "-Step-" in im: # Filters out any images not related to the article itself
				filtered_list.append(im)
		if len(filtered_list) == 0: 
			return get_random_image() # just recursively re-runs the function if the article is useless
		image = filtered_list[random.randrange(0, len(filtered_list), 1)] # gets a random step pic from the article
		# print(image_info["url"])
		# print(image_list)
		# print(image)
		return [image, image_info]

	image_stuff = get_random_image()
	image = image_stuff[0]
	image_info = image_stuff[1]
	# print(image_info)
	# imagedata = Image.open(requests.get(image, stream=True).raw)
	base64_image = base64.b64encode(requests.get(image).content)
	params = {"media[]": base64_image, "status": info["title"], "_base64": True}
	response = t.statuses.update_with_media(**params)
	t.statuses.update(status = "@" + response["user"]["screen_name"] + "\n Title: " + info["url"] + "\nImage: " + image_info["url"], in_reply_to_status_id = response["id_str"], auto_populate_reply_metadata = True)


log("INFO", "Bot is online.")
while 1:
	dt = datetime.now() + timedelta(hours=1)
	dt = dt.replace(minute=0,second=0)
	while datetime.now() < dt:
		time.sleep(1)
	try:
		do_stuff()
		log("INFO", "Successfully sent the message for " + str(dt.hour) + ":00!")
	except Exception as e:
		log("ERR", str(e))
		pass