#!/usr/bin/python

from PIL import Image
import io
import random
import urllib
import json
import datetime
import logging
from jpglitch import Jpeg
from alchemyapi_python.alchemyapi import AlchemyAPI
from instagram import InstagramSession

logger = logging.getLogger('vitium')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('vitium.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


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
	    logger.info('## Response Object ##')
	    logger.info(json.dumps(response, indent=4))

	    logger.info('')
	    logger.info('## Keywords ##')
	    for keyword in response['imageKeywords']:
	        logger.info('{key} : {score}'.format(key=keyword['text'], score=keyword['score']))
	    logger.info('')
	else:
	    logger.error('Error in image tagging call: ', response['statusInfo'])

def getKeywords(response):
	keywords = []
	if response['status'] == 'OK':
	    for keyword in response['imageKeywords']:
	        keywords.append(keyword)
	else:
	    logger.error('Error in image tagging call: ', response['statusInfo'])

	return keywords

def post(file_path, comment, config):
	insta = InstagramSession()
	if insta.login(config['username'], config['password']):
		media_id = insta.upload_photo(file_path)
		if media_id is not None:
			logger.info("Uploaded image");
			insta.configure_photo(media_id, comment)
		else:
			logger.error('Media id is None!')

def main(config):
	while True:
		now = datetime.datetime.now()
		logger.info('Running at {now}'.format(now=now))
		if len(config['download_urls']) > 0:
			url = random.choice(config['download_urls'])
			logger.info('Downloading from \'{URL}\''.format(URL=url))
			bytes = download(url)
		else:
			logger.error('ERROR: No \'download_urls\' in config')
			return

		original_name = now.strftime(config['save_format_string'])

		glitched = glitch(bytes, config['glitch'])
		original_image = bytesToImage(bytes)
		glitched_image = bytesToImage(glitched)

		# original_image.show()
		# glitched_image.show()

		alchemyapi = AlchemyAPI(config['alchemyapi_key'])
		
		options = {'forceShowAll': 1}
		logger.info('Requesting tags for original image')
		orig_response = alchemyapi.imageTaggingRaw(bytes, options)
		logger.info('Requesting tags for glitched image')
		glitch_response = alchemyapi.imageTaggingRaw(glitched, options)
		keywords = getKeywords(orig_response)
		logger.info('Recieved original {orig} glitch {glitch}'.format(orig=len(keywords), glitch=len(getKeywords(glitch_response))))
		if (len(keywords) and len(getKeywords(glitch_response))):
			break;


		
	original_image.save(config['save_directory'] + '/' + original_name)
	glitched_image.save(config['save_directory'] + '/' + config['prefix'] + original_name)

	logger.info('---Original---')
	printResponse(orig_response)
	logger.info('---Glitched---')
	printResponse(glitch_response)

	comment = ''
	for keyword in keywords:
		if keyword['score'] > 0.4:
			comment += ' #' + keyword['text'].replace(" ", "")

	if not len(comment):
		logger.info('No comment so far adding first')
		comment += ' #' + keyword['text'][0].replace(" ", "")
	
	comment += ' #glitchart #digitalart'

	logger.info('Comment is \'{comment}\''.format(comment=comment))

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


