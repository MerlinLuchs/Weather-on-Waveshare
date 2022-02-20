# See this in action here: https://www.reddit.com/r/raspberry_pi/comments/swcii5/raspberry_pi_4_and_29_epaper_showing_me_the/
#

import json 
import time
import urllib.request
import urllib.parse
from lib import epd2in9bc # Get the waveshare module for your display (epd2inbc is the black/red one, epd2in9 is the black/white one) and put them in a subfolder called "lib"
from PIL import Image,ImageDraw,ImageFont # Needed for the e-ink display.
import textwrap # This is so your text can wrap if it gets too long.
import datetime # To get time of last update.
# import locale
# locale.setlocale(locale.LC_ALL, 'de_DE.utf8') # Used this to set Germany as a region.

meteocons = ImageFont.truetype('meteocons.ttf', 32) # Get here: https://www.alessioatzeni.com/meteocons/ and put .ttf file in the same directory
meteoconssmall = ImageFont.truetype('meteocons.ttf', 20) # This is the same for a smaller text size, in case you want smaller symbols.
glyphter = ImageFont.truetype('glyphter.ttf', 20) # This is for humidity icon. Font is here: https://freebiesbug.com/psd-freebies/80-stroke-icons-psd-ai-webfont/
font22 = ImageFont.truetype('Font.ttc', 22) # Various font sizes to choose from.
font20 = ImageFont.truetype('Font.ttc', 20)
font18 = ImageFont.truetype('Font.ttc', 18)
font16 = ImageFont.truetype('Font.ttc', 16)
font14 = ImageFont.truetype('Font.ttc', 14)
width = 296 # width and height of my particular 2.9 inch display.
height = 128

APIKEY = "xxxxxxxxxxxxxxxxx" # Get a free api key from the Open Weather Map: https://openweathermap.org/api
LOCATION = "Berlin,DE" # Choose your city.
WETTER_API_URL = "http://api.openweathermap.org/data/2.5/weather" # This is the weather API. They have other APIs like the "One Call" one that has other info like forecast or moonrise. Pick your poison.

epd = epd2in9bc.EPD() # Adjust according to your display.
epd.init()
image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
ryimage = Image.new('1', (epd.height, epd.width), 255) # This is to clear the red image - not needed for black/white displays.
draw = ImageDraw.Draw(image)

def ausgabe(y):
	epd.init()
	draw.rectangle((0, 0, epd.height, epd.width), fill = 255)
	today = datetime.datetime.today()
	drawblack = ImageDraw.Draw(image)
	drawred = ImageDraw.Draw(ryimage)
	
	message = "\' " #Meteocon symbol for the thermometer
	drawred.text((2,5), message, font = meteoconssmall, fill = 0) # It's red. Adjust this for black/white displays.
	message = "   " + str(y["main"]["temp"]) + "ºC" # Getting the data from the API.
	drawblack.text((3,2), message, font = font22, fill = 0)
	message = str(y["weather"][0]["description"])
	drawblack.text((23,25), message, font = font20, fill = 0) # Getting description from API (e.g. "partly cloudy")
	
	#Wind speed
	message = "F"  # Meteocon symbol for wind
	drawblack.text((80,57), message, font = meteoconssmall, fill = 0)
	wind_ms = (y["wind"]["speed"])
	wind_kmh = wind_ms * 3.6 # This calculates the metres/second into kilometers/hour
	formatted_wind_kmh = "{:.2f}".format(wind_kmh) # This reduces the output to two numbers behind the comma
	message = str(y["wind"]["speed"]) + " m/s = "  + str(formatted_wind_kmh) + " km/h"
	drawblack.text((102,57), message, font = font16, fill = 0)

	message = "W" #glyphter font: This is the humidity drop.
	drawblack.text((6,55), message, font = glyphter, fill = 0)
	message = ": " + str(y["main"]["humidity"]) + "%" 
	drawblack.text((22,55), message, font = font18, fill = 0)
		
	message = "B " # Sunrise icon
	drawblack.text((5,95), message, font = meteocons, fill = 0)
	message = "   " + time.strftime('%H:%M', time.localtime(y["sys"]["sunrise"]))
	drawblack.text((20,95), message, font = font18, fill = 0)
	message = "Sunrise"
	drawblack.text((35,110), message, font = font14, fill = 0)

	message = "A " # Sunset icon
	drawred.text((85,95), message, font = meteocons, fill = 0)
	message = "   " + time.strftime('%H:%M', time.localtime(y["sys"]["sunset"]))
	drawblack.text((100,95), message, font = font18, fill = 0)
	message = "Sunset"
	drawblack.text((115,110), message, font = font14, fill = 0)

#	DATE AND TIME
	drawblack.text((175, 95), 'Last update:', font = font16, fill = 0) #
	drawblack.text((175, 110), '{:%a, %d.%m. (%H:%M)}'.format(today), font = font14, fill = 0)
	drawblack.line((165, 95, 165, 128), fill = 0, width = 2)

	epd.display(epd.getbuffer(image), epd.getbuffer(ryimage))
	epd.sleep()

# Set up where we'll be fetching data from
params = {"q": LOCATION, "appid": APIKEY, "units":"metric" } # options are standard, metric, imperial
data_source = WETTER_API_URL + "?" + urllib.parse.urlencode(params) +"&lang=en" # change "&lang=en" to "&lang=de" for German, etc.
weather_refresh = None

wait = 0

while True:
	if wait == 0:
		response = urllib.request.urlopen(data_source) 
		if response.getcode() == 200: 
			value = response.read() 
			y = json.loads(value)
			ausgabe(y)
		else: 
			print("Unable to retrieve data at {}".format(url))
		time.sleep(1781) # Every 30 minutes. There was a shift, though, maybe the display refresh time, so I adjusted it a bit.

