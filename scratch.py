#!/usr/bin/env python

passhash = 'MD5'
import json
import urllib
args = {'q' : passhash,
        'v' : '1.0',
        'start' : 0,
        'rsz': 8,
        'safe' : 'off',    #Rule 34 says there will be MD5 hash porn on the Internet.  If so, would it be distinguishable from an MD5 of the Sound of Music, The Bible, or Flowers for Algernon?  Probably not.
        'filter' : 1,    
        'hl'    : 'en'
        }
query = urllib.urlencode(args)    
rawresults = urllib.urlopen('http://ajax.googleapis.com/ajax/services/search/web?' + query)
sortedresults = json.loads(rawresults.read())
if not sortedresults.has_key('responseStatus') and sortedresults.get('responseStatus') != 200: #if this doesn't evaluate lazy, we might have problems
    sortedresults = False
if not sortedresults:
    quit('Google result error')
cracksites = []
crackcache = []
for result in sortedresults['responseData']['results']:
    if result:
        cracksites.append(str(result['unescapedUrl']).strip('\'"'))
        crackcache.append(str(result['cacheUrl']).strip('\'"'))
print('Something')
pass
quit()