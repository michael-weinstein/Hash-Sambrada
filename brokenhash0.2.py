#!/usr/bin/env python

def checkargs():  #subroutine for validating commandline arguments
    import argparse 
    plaintext = False
    parser = argparse.ArgumentParser()
    parser.add_argument ("-p", "--password", help = "Enter the plaintext of the password on the commandline")
    args = parser.parse_args()  
    if not (args.password):
        return False
    else:
        return str(args.password)
    
def gethash(password):
    import hashlib 
    passhash = hashlib.md5(rawbytes(password))
    passhash = cookhashbytes(passhash)
    return passhash

def rawbytes(stringin):
    return bytes(stringin)#, 'utf-8')

def cookhashbytes(passhash):
    return passhash.hexdigest()

def cookbytes(rawbytes):
    return str(rawbytes.decode('utf-8'))

def crackedonweb(passhash, plaintext, cracksites = False):
    import urllib
    if not cracksites:
        cracksites = ['http://md5.znaet.org/md5/', 'http://www.md5-hash.com/md5-hashing-decrypt/', 'http://md5cracker.org/decrypted-md5-hash/', 'http://md5reverse.insdy.net/decrypt_md5/']
        cracksites = (site + passhash for site in cracksites)            
    #could this be sped up by doing each site as a thread in a multithreading scheme?
    #this could be more powerful by having it do a POST the site and search each one through its own engine if they can't take the hash on the URL line
    #the ideal would be to feed it as a google search and regex the google result page, but that would require getting google to play ball
    for site in cracksites:
        #try:
        response = urllib.urlopen(site)
        #except :
        #    continue
        searchresult = response.read()
        if searchresult:
            if foundinresult(plaintext, searchresult):
                return True
        else:
            continue
    return False

def googleresults(passhash, plaintext, zeroinformation = True):  #does not work, google seems to get pissed off over this and hangs up on us
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
    if zeroinformation:
        return crackcache
    else:
        return cracksites
    
def crackedonpygoogle(passhash, plaintext):  #trying this approach
    from pygoogle import pygoogle
    googleresult = pygoogle(passhash)  #default is for moderate safe search.  Probably OK to let this be, since we won't find porn while googling a password hash.  Probably throwing caution (and Rule 34) to the wind here.
    googleresult.pages = 1
    resulturls = googleresult.get_urls()
    for i in range(0,len(resulturls)):
        resulturls[i] = str(resulturls[i])
    if crackedonweb(passhash, plaintext, resulturls):
        return True
    else:
        return False

def foundinresult(plaintext, searchresult):
    import re
    found = rawbytes(plaintext) in searchresult
    if found:
        return True
    else:
        return False
    
def askforpassword():
    password = False
    while not password:
        print ('Please enter the password to check.')
        try:
            password = str(input('>>'))
        except:
            password = False
        if not password:
            print ('Invalid entry, please try again.')
    return password

def main():
    plaintext = checkargs()
    if not plaintext:
        plaintext = askforpassword()
    passhash = gethash(plaintext)
#    if crackedonweb(passhash, plaintext):
    if crackedonpygoogle(passhash, plaintext):
        print('This password has a broken hash')
    else:
        print('This password is safe.')
    quit('Goodbye')

main()
    
    