#!/usr/bin/python

from PIL import Image
import io
import random
import urllib
import json
import datetime
from jpglitch import Jpeg
from alchemyapi_python.alchemyapi import AlchemyAPI
from instagram import InstagramSession

def download(url):
	response = urllib.urlopen(url)
	img_bytes = response.read()
	return img_bytes

def bytesToImage(bytes):
	return Image.open(io.BytesIO(bytes))

def imageToBytes(image):
	output = io.BytesIO()
	image.save(output, 'JPEG')    
	return output.getvalue()

def glitch(bytes, config):
	for rot in xrange(config['num_rotations']):
		jpeg = Jpeg(bytearray(bytes), random.randint(config['min_amount'], config['max_amount']), 
									  random.randint(config['min_seed'], config['max_seed']), 
									  random.randint(1,config['max_iterations']))

		im = bytesToImage(jpeg.new_bytes)
		bytes = imageToBytes(im.rotate(90)) 

	# rotate back
	for rot in xrange(config['num_rotations']):
		im = bytesToImage(bytes)
		bytes = imageToBytes(im.rotate(-90)) 

	return bytes

def printResponse(response):
	if response['status'] == 'OK':
	    print('## Response Object ##')
	    print(json.dumps(response, indent=4))

	    print('')
	    print('## Keywords ##')
	    for keyword in response['imageKeywords']:
	        print(keyword['text'], ' : ', keyword['score'])
	    print('')
	else:
	    print('Error in image tagging call: ', response['statusInfo'])

def getKeywords(response):
	keywords = []
	if response['status'] == 'OK':
	    for keyword in response['imageKeywords']:
	        keywords.append(keyword)
	else:
	    print('Error in image tagging call: ', response['statusInfo'])

	return keywords

def post(file_path, comment, config):
	insta = InstagramSession()
	if insta.login(config['username'], config['password']):
		media_id = insta.upload_photo(file_path)
		print media_id
		if media_id is not None:
			insta.configure_photo(media_id, comment)
		else:
			print 'Media id is None!'

def main(config):
	while True:
		now = datetime.datetime.now()
		if len(config['download_urls']) > 0:
			url = random.choice(config['download_urls'])
			bytes = download(url)
		else:
			print('ERROR: No \'download_urls\' in config');
			return

		original_name = now.strftime(config['save_format_string'])

		glitched = glitch(bytes, config['glitch'])
		original_image = bytesToImage(bytes)
		glitched_image = bytesToImage(glitched)

		original_image.show()
		glitched_image.show()

		alchemyapi = AlchemyAPI(config['alchemyapi_key'])
		
		options = {'forceShowAll': 1}
		orig_response = alchemyapi.imageTaggingRaw(bytes, options)
		glitch_response = alchemyapi.imageTaggingRaw(glitched, options)
		keywords = getKeywords(orig_response)
		if (len(keywords) and len(getKeywords(glitch_response))):
			break;


		
	original_image.save(config['save_directory'] + '/' + original_name)
	glitched_image.save(config['save_directory'] + '/' + config['prefix'] + original_name)

	print('---Original---')
	printResponse(orig_response)
	print('---Glitched---')
	printResponse(glitch_response)

	comment = ''
	for keyword in keywords:
		if keyword['score'] > 0.4:
			comment += ' #' + keyword['text']

	if not len(comment):
		print('No comment so far adding first')
		comment += ' #' + keyword['text'][0]
	
	comment += ' #glitchart'

	print comment

	if config['confirmation']:
		x = raw_input('Upload: y/n? ')

		if x == 'y':
			post(config['save_directory'] + '/' + config['prefix'] + original_name,
				 comment, config['instagram'])
	else:
		post(config['save_directory'] + '/' + config['prefix'] + original_name,
				 comment, config['instagram'])

	return

if __name__ == '__main__':
	with open('../config.json', 'r') as file:
		main(json.load(file))


