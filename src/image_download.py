#!/usr/bin/python

from PIL import Image
import io
import random
import urllib
import json
from jpglitch import Jpeg
from alchemyapi_python.alchemyapi import AlchemyAPI

def download(url):
	response = urllib.urlopen(url)
	img_bytes = response.read()
	return img_bytes

def bytesToImage(bytes):
	return Image.open(io.BytesIO(bytes))

def glitch(bytes):
	jpeg = Jpeg(bytearray(bytes), random.randint(0,99), random.randint(0,99), random.randint(0,20))
	return jpeg.new_bytes

def main():
	url = 'https://unsplash.it/640/640/?random';
	bytes = download(url)
	glitched = glitch(bytes)
	original_image = bytesToImage(bytes)
	glitched_image = bytesToImage(glitched)

	original_image.show()
	glitched_image.show()

	original_image.save('Original.jpg')
	glitched_image.save('Glitched.jpg')

	alchemyapi = AlchemyAPI()
	
	options = {'forceShowAll': 1}
	response = alchemyapi.imageTagging('image', 'Original.jpg', options)

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

	return

if __name__ == '__main__':
	main()