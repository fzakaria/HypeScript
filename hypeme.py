"""
This python script automates downloading files from HypeMachine.com
Copyright (C) 2011  Farid Marwan Zakaria

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys
import urllib2
import re
import time
import sqlite3
import os
from collections import deque

AREA_TO_SCRAPE = 'popular'
NUMBER_OF_PAGES = 3
DB_FILE = 'songs.db'
DEBUG = True
FOLDER = 'C:/Development/HypeScript/Test'

class HypeSong:
	def __init__(self, id , key, title, artist):
		self.id = id
		self.key = key
		self.title = title
		self.artist = artist
		self.url = 'http://hypem.com/serve/play/' + id + '/' + key + ".mp3"
		

	def __str__(self):
		return "("+self.key+", "+self.title+", "+self.artist+")"


class HypeScraper:
	
	def __init__(self):
		self.url = 'http://hypem.com/'+AREA_TO_SCRAPE+'/'
		self.songs = deque()
		self.conn = sqlite3.connect(DB_FILE)
		self.cursor = self.conn.cursor()
		
	def start(self):
		for i in range(1, NUMBER_OF_PAGES + 1):
			complete_url = self.url + "/" + str(i) + '?ax=1&ts='+ str(time.time())
			request = urllib2.Request(complete_url)
			response = urllib2.urlopen(request)
			#save our cookie
			self.current_cookie = response.headers.get('Set-Cookie')
			#grab the HTML
			html_data = response.read()
		
			if DEBUG:
				html_file = open("hypeHTML.html", "w")
				html_file.write(html_data)
				html_file.close()
				
			self.parse_html(html_data)
			
			self.download_songs()
				
	
	def download_songs(self):
	
		while len( self.songs ) > 0:
			current_song = self.songs.popleft()
			
			print "Attempting to download ", current_song
			
			if self.song_exists( current_song ):
				print "\tSong existed!"
				continue	
			
			#download song
			print "\tDownloading song..."
			if (self.download_song(current_song) ):
				print "\tInserted song into db"
				self.insert_song(current_song)
			
		
			
	def download_song(self, song):
		os.chdir(FOLDER)
		request = urllib2.Request(song.url)
		request.add_header('cookie', self.current_cookie)
		try:
     			response = urllib2.urlopen(request)
		except urllib2.HTTPError  as e:
      			print "Error downloading song: ", song
			print(e.code)
			return False
		#grab the data
		song_data = response.read()
		try:
			mp3_song = open(song.title+".mp3", "wb")
			mp3_song.write(song_data)
			mp3_song.close()
		except Exception as e:
			print "Error downloading song: ", song
			return False
		time.sleep(1) #sleep so we aren't booted
		return True
	
	def insert_song(self, song):
		t = (None, song.id)
		self.cursor.execute("insert into songs values (?, ?)", t)
		self.conn.commit()
		
	def song_exists(self, song):
		t = (song.id, )
		self.cursor.execute("select * from songs where key=?", t)
		if len(self.cursor.fetchall()) > 0:
			return True
		return False
		
	def parse_html(self, html_contents):
		idMatches = re.findall("[ \t]id:\'(\w*)(?=\')", html_contents)
		keyMatches = re.findall("(?<=\tkey: \')\w*(?=\')", html_contents)
		songMatches= re.findall("(?<=\tsong:\').*(?=\')", html_contents)
		artistMatches= re.findall("(?<=\tartist:\').*(?=\')", html_contents)
		
		for i in range( len(idMatches) ):
			id = idMatches[i]
			key = keyMatches[i]
			title = songMatches[i]
			artist = artistMatches[i]		
			song = HypeSong(id, key, title, artist)
			self.songs.append(song)

		if DEBUG:
			print "Found " , len(self.songs) , " songs."
			
			

def main():
	scraper = HypeScraper()
	scraper.start()
	scraper.conn.close()
		
		
		
		
if __name__ == "__main__":
    main()
		