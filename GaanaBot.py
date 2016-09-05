import telepot
import urllib
import urllib2
from bs4 import BeautifulSoup
import webbrowser
import json
import time
import os
import pynotify
from datetime import datetime
import re
from slugify import slugify
import codecs
import wget

#Download path for music file
path = '/home/mayank/Desktop/TelegramBot/Songs/'

database_path = '/home/mayank/Desktop/TelegramBot/Database/'
userdata_file_path = database_path + 'userdata.json'
songdata_file_path = database_path + 'songdata.json'
searchdata_file_path = database_path + 'searchdata.json'

#Telegram bot token ID
TOKEN = '###############################################'

#Base url for fetching json object
BASE_URL = 'http://www.youtubeinmp3.com/fetch/?format=JSON&video='

#Keywords
SUCCESS = 'Success'
FAIL = 'Fail'
ERROR = 'Error in pushing song.'
WELCOME_MSG = 'To start using GaanaBot send the name of the song you want to download. To get lyrics send a message in the format \'Lyrics <song_name> - <artist_name>\''
ONE_MB = 1000000
SONG_SENT_MESSAGE = 'Download is complete. Song is being sent to you. Please wait. To save the song click on it and choose Save to Music option.'

BASE_LYRICS_URL = 'http://lyric-api.herokuapp.com/api/find/'
SLASH = '/'
LYRICS_ERROR_MSG = 'Lyrics not found. Message should be in the following format : Lyrics <song_name> - <artist_name>'
LYRICS_WAITING_MSG = 'Looking up lyrics for the song you requested. Please wait.'


def handle(msg):
  #Get chat_id and text from message which has been received
  print 'Message received:', msg
  username = msg['from']['first_name']
  chat_id = msg['from']['id']
  command = msg['text']


  print ('Username: ' + username)
  print ('Got message: %s' % command)

  if command == '/start':
     bot.sendMessage(chat_id, WELCOME_MSG)
     userdata = {'userid': msg['from']['id'],
                 'username': msg['from'],
     }
     savedata(userdata,userdata_file_path)
     return

  first_word = command.split(' ', 1)[0]
  print 'first word is : ' + first_word
  lower_first_word = first_word.lower()


  getlyrics = False
  if lower_first_word == 'lyrics' :
     getlyrics = True
     sendlyrics(msg)
  else:
     sendsong(msg)
     searchdata = {'userid': msg['from']['id'],
                   'username': msg['from'],
                   'searchterm': msg['text'],
                   'date' :  msg['date'],
                   'lyrics' : getlyrics
     }
     savedata(searchdata,searchdata_file_path)
  return

def sendlyrics(msg):
    username = msg['from']['first_name']
    chat_id = msg['from']['id']
    command = msg['text']

    bot.sendMessage(chat_id, LYRICS_WAITING_MSG)

    first_word = command.split(' ', 1)[0]
    s = command.split(first_word + ' ', 1)[1]
    p = s.index('-')
    song_name = s[:p]
    song_name = song_name.lower()

    if song_name[-1] == ' ' :
         song_name = song_name[0:-1].strip()
         print song_name

    artist_name = s[p+1:]
    artist_name = artist_name.lower()

    if artist_name[-1] == ' ' :
         artist_name = artist_name[0:-1]
         print artist_name

    artist_name = artist_name.replace(' ', '%20')
    song_name = song_name.replace(' ', '%20')

    print artist_name
    print song_name

    LYRICS_URL = BASE_LYRICS_URL + artist_name + SLASH + song_name
    print LYRICS_URL

    data = json.load(urllib2.urlopen(LYRICS_URL))

    if data['lyric'] == '' :
         print 'Lyrics not found.'
         bot.sendMessage(chat_id, LYRICS_ERROR_MSG)
    else :
         lyrics = data['lyric']
         print lyrics
         bot.sendMessage(chat_id, lyrics)
    return

def sendsong(msg):
  username = msg['from']['first_name']
  chat_id = msg['from']['id']
  command = msg['text']
  command = codecs.encode(command,'utf-8')
  bot.sendMessage(chat_id, username + ', your song is on its way..')

  #Searching YouTube with text which has been received

  query = urllib.quote(command)
  url = "https://www.youtube.com/results?search_query=" + query
  response = urllib2.urlopen(url)

  #Reading response and finding top result
  html = response.read()
  soup = BeautifulSoup(html, "lxml")

  for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        #Getting Video Url from first link in search results
        VIDEO_URL = 'https://www.youtube.com' + vid['href']
        print ('Video URL : ' + VIDEO_URL)

        #bot.sendMessage(chat_id, VIDEO_URL)

        #Creating Json Url for obtaining download link, length and title of song
        JSON_URL = BASE_URL + VIDEO_URL
        print ('JSON URL : ' + JSON_URL)

        #bot.sendMessage(chat_id, JSON_URL)

        #Loading data from json object
        response = urllib.urlopen(JSON_URL)

        try:
             data = json.loads(response.read()) #Json object
             print (data)

             #Getting length, download url and title of song from json object
             if 'length' not in data:
                raise ValueError("No length in given data")
                print ('No length in given data')
                break
             if 'link' not in data:
                raise ValueError("No link in given data")
                print ('No link in given data')
                break
             if 'title' not in data:
                raise ValueError("No title in given data")
                print ('No title in given data')
                break

             length = data['length']
             print ('Length : ' + str(length))
             DOWNLOAD_URL = data['link']
             print ('DOWNLOAD_URL : ' + DOWNLOAD_URL)
             title = data['title']
             print ('Title = ' + title)

             title =  slugify(title)
             upload_file = path + title.lower() + '.mp3'
             print ('upload_file name : ' + upload_file)

             if not (os.path.exists(upload_file)) :
                bot.sendMessage(chat_id, 'Download for your song has started..')
                print ('File does not exist: downloading')
                #DownloadSong method being called for downloading song
                downloadSong(DOWNLOAD_URL, upload_file)
                file_size = checkFileSize(upload_file)
                if (file_size < ONE_MB) :
                    os.remove(upload_file)
                    print ('Deleted small file.')
                    continue
                    bot.sendMessage(chat_id, SONG_SENT_MESSAGE)
                    print ('Download is complete.')
             else:
                    print ('File exists: no need to download')

             print ('Uploading song')
             print ('Start time - ' + str(datetime.now()))

             #Opening latest file in downloads folder and sending file as message
             audio = open(upload_file , 'rb')
             bot.sendAudio(chat_id, audio, length , '', title)

             print ('Successful')
             print ('End time - ' + str(datetime.now()))
             sendmessage(SUCCESS, title + ' was pushed successfully to ' + username + '.')
             songdata = {'searchterm': command,
                         'searchresult': title.lower(),
                         'date' :  msg['date']
             }
             savedata(songdata,songdata_file_path)
             break

        except ValueError:
             print ('No song found')
             bot.sendMessage(chat_id, 'No song found. Please try again with a different keyword.')
             sendmessage(FAIL, ERROR)
             break

  return

def savedata(data, filename):
  msg  = json.dumps(data)
  with open(filename, 'a') as f:
    json.dump(msg, f)
    f.write(os.linesep)

def sendmessage(title, message):
  pynotify.init("Test")
  notice = pynotify.Notification(title, message)
  notice.show()
  return

def downloadSong(url, title):
    downloaded = wget.download(url, title)
    print "Downloaded: " + downloaded

def checkFileSize(upload_file_path):
  b = os.path.getsize(upload_file_path)
  return b



bot = telepot.Bot(TOKEN)
bot.getMe()
bot.notifyOnMessage(handle)
print ('I am listening..')
