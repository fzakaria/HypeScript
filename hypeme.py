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

import unicodedata
from time import time
import urllib2
import urllib
from bs4 import BeautifulSoup
import json
import string
import os

# AREA_TO_SCRAPE
# This is the general area that you'd like to parse and scrape.
# Ex. 'popular', 'latest', '<username>' or 'track/<id>'

AREA_TO_SCRAPE = 'popular'
NUMBER_OF_PAGES = 3

# DO NOT MODIFY THESE UNLES YOU KNOW WHAT YOU ARE DOING
DEBUG = False
HYPEM_URL = 'https://hypem.com/{}'.format(AREA_TO_SCRAPE)


validFilenameChars = '-_.() %s%s' % (string.ascii_letters, string.digits)


def removeDisallowedFilenameChars(filename):
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII',
                                                                     'ignore')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)


class HypeScraper:

    def __init__(self):
        pass

    def start(self):
        print '--------STARTING DOWNLOAD--------'
        print '\tURL : {} '.format(HYPEM_URL)
        print '\tPAGES: {}'.format(NUMBER_OF_PAGES)

        for i in range(1, NUMBER_OF_PAGES + 1):

            print 'PARSING PAGE: {}'.format(i)

            page_url = HYPEM_URL + '/{}'.format(i)
            html, cookie = self.get_html_file(page_url)

            if DEBUG:
                html_file = open('hypeHTML.html', 'w')
                html_file.write(html)
                html_file.close()

            tracks = self.parse_html(html)

            print '\tPARSED {} SONGS'.format(len(tracks))

            self.download_songs(tracks, cookie)

    def get_html_file(self, url):
        data = {'ax': 1, 'ts': time()}
        data_encoded = urllib.urlencode(data)
        complete_url = url + '?{}'.format(data_encoded)
        request = urllib2.Request(complete_url)
        response = urllib2.urlopen(request)
        # save our cookie
        cookie = response.headers.get('Set-Cookie')
        # grab the HTML
        html = response.read()
        response.close()
        return html, cookie

    def parse_html(self, html):
        track_list = []
        soup = BeautifulSoup(html)
        html_tracks = soup.find(id='displayList-data')
        if html_tracks is None:
            return track_list
        try:
            track_list = json.loads(html_tracks.text)
            if DEBUG:
                print json.dumps(track_list, sort_keys=True, indent=4,
                                 separators=(',', ': '))
            return track_list[u'tracks']
        except ValueError:
            print 'Hypemachine contained invalid JSON.'
            return track_list

    # tracks have id, title, artist, key
    def download_songs(self, tracks, cookie):

        print '\tDOWNLOADING SONGS...'
        for track in tracks:

            key = track[u'key']
            id = track[u'id']
            artist = removeDisallowedFilenameChars(track[u'artist'])
            title = removeDisallowedFilenameChars(track[u'song'])
            type = track[u'type']

            print '\tFETCHING SONG....'

            print u'\t{} by {}'.format(title, artist)

            if type is False:
                print '\tSKIPPING SONG SINCE NO LONGER AVAILABLE...'
                continue

            try:
                serve_url = 'http://hypem.com/serve/source/{}/{}'.format(id,
                                                                         key)
                request = urllib2.Request(serve_url, '', {'Content-Type':
                                                          'application/json'})
                request.add_header('cookie', cookie)
                response = urllib2.urlopen(request)
                song_data_json = response.read()
                response.close()
                song_data = json.loads(song_data_json)
                url = song_data[u'url']

                download_response = urllib2.urlopen(url)
                filename = '{} - {}.mp3'.format(artist, title)
                if os.path.exists(filename):
                    print('File already exists , skipping')
                else:
                    mp3_song_file = open(filename, 'wb')
                    mp3_song_file.write(download_response.read())
                    mp3_song_file.close()
            except urllib2.HTTPError, e:
                print ('HTTPError = ' + str(e.code) +
                       ' trying hypem download url.')
            except urllib2.URLError, e:
                print ('URLError = ' + str(e.reason) +
                       ' trying hypem download url.')
            except Exception, e:
                print 'generic exception: ' + str(e)


def main():
    scraper = HypeScraper()
    scraper.start()

if __name__ == '__main__':
        main()
