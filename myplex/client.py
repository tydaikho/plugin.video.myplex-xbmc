'''
    @document   : client.py
    @package    : MyPlex client for XBMC add-on
    @author     : Rick Crook
    @copyright  : 2012, Rick Crook 
    @thanks     : to Zsolt Torok for his example SoundCloud client
    @version    : 0.01

    @license    : Gnu General Public License - see LICENSE.TXT
    @description: myPlex client library
'''
'''
This file is part of "MyPlex-XBMC add-on"

    "MyPlex-XBMC add-on" is free software: you can redistribute
    it and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the License,
    or (at your option) any later version.

    "MyPlex-XBMC add-on" is distributed in the hope that it will
    be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with "MyPlex-XBMC add-on".
    If not, see <http://www.gnu.org/licenses/>.
'''

import urllib
import urllib2
import httplib2
import urlparse
import xml.dom.minidom

#define global constants
_PLEX_SERVERS_URL = 'https://my.plexapp.com/pms/servers.xml'
_PLEX_SECTIONS_URL = 'https://my.plexapp.com/pms/system/library/sections'
_PLEX_SIGNIN_URL = 'https://my.plexapp.com/users/sign_in.xml'
# https://my.plexapp.com/pms/playlists?X-Plex-Token=<Hash> 
# https://my.plexapp.com/pms/playlists/queue?X-Plex-Token=<Hash> 
# https://my.plexapp.com/pms/playlists/queue/unwatched?X-Plex-Token=<Hash> 
# https://my.plexapp.com/pms/playlists/queue/watched?X-Plex-Token=<Hash>

_X_PLEX_PLATFORM = 'XBMC'
_X_PLEX_PLATFORM_VERSION = 'Unknown'
_X_PLEX_PROVIDES = 'player'
_X_PLEX_PRODUCT = 'plugin.video.myplex-xbmc'
_X_PLEX_VERSION = '0.0.1'
_X_PLEX_DEVICE = 'Unknown'
_X_PLEX_CLIENT_IDENTIFIER = 'Unknown'

VIDEO_TITLE = 'title'
VIDEO_STREAM_URL = 'stream_url'
_TITLE = 'pmstitle'
_URL ='pmsurl'
_SERVER = 'pmsserver'
_TOKEN = 'pmstoken'
_HOST = 'pmshost'

class MyPlexClient(object):
  # MyPlex client to handle all communication with the MyPlex REST API.

  def __init__(self, username='', password='', token=''):
    #Constructor
    # set token if supplied else try and login
    self.username = username
    self.password = password
    self.loginerror = ''
    self.token = ''
    self.login = False
    
    if token == '':
      self._login(username,password)
    else:
      self.login = True
      self.token = token
  
  # Login
  def _login(self,username,password):
    ''' 
      POST to myPlex to sign in and get PMS token :
        X-Plex-Platform (Platform name, eg iOS, MacOSX, Android, LG, etc)
        X-Plex-Platform-Version (Operating system version, eg 4.3.1, 10.6.7, 3.2)
        X-Plex-Provides (one or more of [player, controller, server])
        X-Plex-Product (Plex application name, eg Laika, Plex Media Server, Media Link)
        X-Plex-Version (Plex application version number)
        X-Plex-Device (Device name and model number, eg iPhone3,2, Motorola XOOM, LG5200TV)
        X-Plex-Client-Identifier (UUID, serial number, or other number unique per device)
      @private
      @returns string PMS token
    '''
    self.username = username
    self.password = password
    
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    h.add_credentials(self.username, self.password)
    h.follow_all_redirects = True
    
    headers={    'X-Plex-Platform': _X_PLEX_PLATFORM,
                 'X-Plex-Platform-Version': _X_PLEX_PLATFORM_VERSION,
                 'X-Plex-Provides': _X_PLEX_PROVIDES,
                 'X-Plex-Product': _X_PLEX_PRODUCT,
                 'X-Plex-Version': _X_PLEX_VERSION,
                 'X-Plex-Device': _X_PLEX_DEVICE,
                 'X-Plex-Client-Identifier': _X_PLEX_CLIENT_IDENTIFIER}
    body = ''
    
    try:
      response, content = h.request(_PLEX_SIGNIN_URL, 'POST', body=body, headers=headers)
    except:  
      try:
        self._info('_getToken.ERROR.errors returned by myPlex server. details in log')
        print response
        print content
        self.loginerror = 'MyPlex server returned http status code ' + response['status']
      except:
        self._info('_getToken.ERROR.failed to connect to myPlex server')
        self.loginerror = 'Failed to get response from myPlex server'
                
      self.login = False
      return self.login
      
    print response
    print content
    
    if response['status'] == '201':
      print '201'
      dom = xml.dom.minidom.parseString(content)
      print content
      token = dom.getElementsByTagName('authentication-token')[0]
      self.token = token.childNodes[0].data
      print self.token
      
      if self.token != '':
        self.login = True
      else:
        self.login = False
    else:
      self._info('_getToken.ERROR.errors returned by myPlex server. details in log')
      print response
      print content
      self.login = False
      self.token = ''
      self.loginerror = 'MyPlex server returned error ' + response['status']
      
    return self.login
    
  # Servers
  def get_servers(self):
    '''
      Create list of servers from MyPlex server
      https://my.plexapp.com/pms/system/library/sections
      http://<host>:<port><path>/all?X-Plex-Token=<accessToken>
      @access public
      @return list of servers
    '''
    listing = []
    try:
      url = _PLEX_SERVERS_URL + '?X-Plex-Token=' + self.token
      document = urllib2.urlopen(url)
    except:
      self._info('_getServers.ERROR.failed to connect to myPlex server')
      filename = "C:\Users\Richard Crook\AppData\Roaming\XBMC\servers.xml"
      document = open(filename)
      
    dom = xml.dom.minidom.parse(document)
        
    servers = dom.getElementsByTagName("Server")
    for server in servers: 
      url = _PLEX_SECTIONS_URL + '?X-Plex-Token=' + self.token
      title = server.getAttribute("name")
      self._info(('Appending server: %s') % title)
      listing.append({ _TITLE: title, _URL: url, _TOKEN: self.token })
    return listing
  
  # Sections
  def get_sections(self,server):
    '''
      Create list of sections from MyPlex 
      https://my.plexapp.com/pms/system/library/sections?X-Plex-Token=<accessToken>
      @access public
      @return list of sections
    '''    
    listing = []
    try:
      url = _PLEX_SECTIONS_URL + '?X-Plex-Token=' + self.token
      document = urllib2.urlopen(url)
    except:
      self._info('_getSections.ERROR.failed to connect to myPlex server')
      filename = "C:\Users\Richard Crook\AppData\Roaming\XBMC\sections.xml"
      document = open(filename)
      
    dom = xml.dom.minidom.parse(document)
        
    sections = dom.getElementsByTagName("Directory")
    for section in sections:
      if server == section.getAttribute("serverName"):
        # http://<host>:<port>/library/sections/<sectionid>/all?X-Plex-Token=<accessToken> 
        serverToken = section.getAttribute("accessToken")
        url = section.getAttribute("key") + '/all?X-Plex-Token=' + serverToken
        title = section.getAttribute("title") 
        host = section.getAttribute("host") + ':' + section.getAttribute("port")
        self._info(('Appending section: %s') % url)
        listing.append({ _TITLE: title, _URL: url, _HOST: host, _TOKEN: serverToken })
    return listing
  
  # @feature: add Music, Pictures, TV Shows and MyPlex Queue, Watched and Unwatched
  
  #Videos
  def get_videos(self, url):
    '''
      Create list of videos from remote Plex server
      http://<host>:<port><path>/all?X-Plex-Token=<accessToken>
      @access public
      @return list of videos
    '''
    listing = []
    self._info(('get_videos.opening url: %s') %url )
    try:
      document = urllib2.urlopen(url)
    except:
      self._info('_getVideos.ERROR.failed to connect to myPlex server') 
      filename = "C:\Users\Richard Crook\AppData\Roaming\XBMC\media.xml"
      document = open(filename)
    
    dom = xml.dom.minidom.parse(document)
    #token = str(url).partition('?X-Plex-Token=')[2]
    host = str(url).partition('/library/')[0]
    
    videos = dom.getElementsByTagName("Video")
    for video in videos:
      title = video.getAttribute("title")
      medias = video.getElementsByTagName("Media")
      for media in medias:
        parts = media.getElementsByTagName("Part")
        for part in parts:
          # http://<host>:<port><key>?X-Plex-Token=<accessToken>
          videoUrl = host + part.getAttribute("key") + '?X-Plex-Token=' + self.token
          self._info(('Appending video: %s.') % videoUrl)
          listing.append({ VIDEO_TITLE: title, VIDEO_STREAM_URL: videoUrl })
    return listing
  
  def _info(self,msg):
    '''
      Print information to log
      @access private
    '''
    print 'MyPlexClient.' + msg
