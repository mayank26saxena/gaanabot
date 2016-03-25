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

def handle(msg):
    #Get chat_id and text from message which has been received
    username = msg['from']['first_name']
    chat_id = msg['from']['id']
    command = msg['text']

    print 'Username: ' + username
    print 'Got message: %s' % command

    bot.sendMessage(chat_id, username + ', your song is on its way..')

    #Searching YouTube with text which has been received
    query = urllib.quote(command)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib2.urlopen(url)

    #Reading response and finding top result
    html = response.read()
    soup = BeautifulSoup(html)

    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):

        #Getting Video Url from first link in search results
        VIDEO_URL = 'https://www.youtube.com' + vid['href'] 
        print 'Video URL : ' + VIDEO_URL
        
        #bot.sendMessage(chat_id, VIDEO_URL)

        #Creating Json Url for obtaining download link, length and title of song
        JSON_URL = BASE_URL + VIDEO_URL
        print 'JSON URL : ' + JSON_URL

        #bot.sendMessage(chat_id, JSON_URL)

        #Loading data from json object
        response = urllib.urlopen(JSON_URL)

        try:
            data = json.loads(response.read()) #Json object
            print data        
    
            #Getting length, download url and title of song from json object
            if 'length' not in data:
                raise ValueError("No length in given data")
                print 'No length in given data'
                break
            if 'link' not in data:
                raise ValueError("No link in given data")
                print 'No link in given data'
                break
            if 'title' not in data:
                raise ValueError("No title in given data")
                print 'No title in given data'
                break
            
            length = data['length'] 
            print 'Length : ' + length
            DOWNLOAD_URL = data['link']
            print 'DOWNLOAD_URL : ' + DOWNLOAD_URL
            title = data['title']
            print 'Title = ' + title

            bot.sendMessage(chat_id, 'Download for your song has started..')

            #Opening web browser for downloading song
            #webbrowser.open(DOWNLOAD_URL)
            downloadSong(DOWNLOAD_URL, title)
            
            #Time delay of 10 seconds for downloading of song
            #time.sleep(10)
           
            #print '10 seconds over'
            #Finding newest file in downloads directory
            #os.chdir(path)
            #files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
            #newest = files[-1]
            #print 'Newest file : ' + newest

            bot.sendMessage(chat_id, 'Download has been completed. Song is being sent to you. Please wait.')
            print 'Download is complete.'
            print 'Uploading song' 
            print 'Start time - ' + str(datetime.now())
            
            #Opening latest file in downloads folder and sending file as message
            audio = open('/home/mayank/Desktop/TelegramBot/' + title , 'rb')
            bot.sendAudio(chat_id, audio, length , '', title)
                  
            print 'Successful'
            print 'End time - ' + str(datetime.now()) 
            sendmessage(SUCCESS, title + ' was pushed successfully to ' + username + '.')

        except ValueError:
            print 'No song found'
            bot.sendMessage(chat_id, 'No song found. Please try again with a different keyword.')
            sendmessage(FAIL, ERROR)

        break

def sendmessage(title, message):
    pynotify.init("Test")
    notice = pynotify.Notification(title, message)
    notice.show()
    return

def downloadSong(url, title):
    usock = urllib2.urlopen(url)
    file_name = title
    f = open(file_name, 'wb')
    file_size = int(usock.info().getheaders("Content-Length")[0])
    print 'Downloading : %s Bytes: %s' % (file_name, file_size)

    downloaded = 0
    block_size = 8192
    while True:
        buff = usock.read(block_size)
        if not buff:
            break

        downloaded = downloaded + len(buff)
        f.write(buff)
        download_status = r"%3.2f%%" % (downloaded * 100.00 / file_size)
        download_status = download_status + (len(download_status)+1) * chr(8)
        print download_status,"done"

    f.close()

#Download path for music file
path = '/home/mayank/Desktop/TelegramBot'

#Telegram bot token ID
TOKEN = '#############################################'


#Base url for fetching json object 
BASE_URL = 'http://www.youtubeinmp3.com/fetch/?format=JSON&video='

#Keywords
SUCCESS = 'Success'
FAIL = 'Fail'
ERROR = 'Error in pushing song.'

bot = telepot.Bot(TOKEN)
bot.getMe()
bot.notifyOnMessage(handle)
print 'I am listening..'
