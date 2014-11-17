#!/usr/bin/env python

def checkargs():  #subroutine for validating commandline arguments
    import argparse 
    plaintext = False
    mode = 'unspecified'
    parser = argparse.ArgumentParser()
    parser.add_argument ("-p", "--password", help = "Enter the plaintext of the password on the commandline")
    parser.add_argument ("-z", "--zeroInfo", help = "Zero information mode.  No communication with potential cracking sites.  Hash still will be sent to Google", action = 'store_true')
    parser.add_argument ("-i", "--insecure", help = "Insecure mode.  Allow communication with potential cracking sites, will require sending the hash of the password.", action = 'store_true')
    args = parser.parse_args()  
    if not (args.password):
        return False  #if they did not enter a password, run manually, regardless of what else was entered
    else:
        if args.zeroInfo or args.insecure:
            if args.zeroInfo and args.insecure:
                quit("Zero information mode and insecure cannot both be used.")
            elif args.zeroInfo:
                mode = 'zeroInfo'
            else:
                mode = 'insecure'
        return (str(args.password), mode)
    
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
    class SafariSpoof(urllib.FancyURLopener):
        version = "Safari/8.0"
    urllib._urlopener = SafariSpoof()  #You say hacking, I say problem solving with extreme impoliteness.  Also, sorry Google.
    if not cracksites:
        cracksites = ['http://md5.znaet.org/md5/', 'http://www.md5-hash.com/md5-hashing-decrypt/', 'http://md5cracker.org/decrypted-md5-hash/', 'http://md5reverse.insdy.net/decrypt_md5/']
        cracksites = (site + passhash for site in cracksites)            
    #could this be sped up by doing each site as a thread in a multithreading scheme?
    #this could be more powerful by having it do a POST the site and search each one through its own engine if they can't take the hash on the URL line
    #the ideal would be to feed it as a google search and regex the google result page, but that would require getting google to play ball
    for site in cracksites:
        try:
            response = urllib.urlopen(site)
        except IOError:
            quit('Unable to reach site.')
        except:
            continue
        searchresult = response.read()
        if searchresult:
            if foundinresult(plaintext, searchresult):
                return True
        else:
            continue
    return False

def quickgoogle(plaintext, passhash):  #Google blocks the hell out of this, result always returns an error (missing token)
    import urllib
    class SafariSpoof(urllib.FancyURLopener):
        version = "Safari/8.0"
    urllib._urlopener = SafariSpoof()
    site = 'https://www.google.com/#q=' + passhash
    try:
        googlepage = urllib.urlopen(site)
        searchresult = googlepage.read()
    except IOError:
        quit('Unable to connect to Google')
    except:
        return False
    if googlepage:
        if foundinresult(plaintext, searchresult):
            return True
        else:
            return False
    else:
        return False
    
def bingsearch(passhash, plaintext):
    import urllib
    import re
    class SafariSpoof(urllib.FancyURLopener):
        version = "Safari/8.0"
    urllib._urlopener = SafariSpoof()
    try:
        rawresult = urllib.urlopen('http://www.bing.com/search?q=' + passhash)
        result = rawresult.read()    
    except IOError:
        quit('Unable to reach Bing')
    if foundinresult(plaintext, result):
        return True
    binglist = []
    resultsbody = re.search('\>\d+? results\<(.+)', result)
    if resultsbody:
        resultsbody = resultsbody.group(0)
        binglist = re.findall('\<a href=\"(http:\/\/.+?)\"', resultsbody)
        if binglist:
            if crackedonweb(passhash, plaintext, binglist):
                return True
    return False
    
def googleresults(passhash, plaintext):  #this method works because I'm using the service entrance.  Need to spoof if I want to search cached pages.
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
    try:
        rawresults = urllib.urlopen('http://ajax.googleapis.com/ajax/services/search/web?' + query)
        sortedresults = json.loads(rawresults.read())
    except IOError:
        quit('Unable to reach Google')
    if not sortedresults.has_key('responseStatus') and sortedresults.get('responseStatus') != 200: #if this doesn't evaluate lazy, we might have problems
        sortedresults = False
    if not sortedresults:
        quit('No sorted results')
    cracksites = []
    crackcache = []
    for result in sortedresults['responseData']['results']:
        if result:
            cracksites.append(str(result['unescapedUrl']).strip('\'"'))
            crackcache.append(str(result['cacheUrl']).strip('\'"'))
    for i in range (0,len(crackcache)):
        crackcache[i] += '&client=safari&rls=en&strip=1'
    return (crackcache, cracksites)
    
def foundinresult(plaintext, searchresult):
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
            password = str(raw_input('>>'))
        except:
            password = False
        if not password:
            print ('Invalid entry, please try again.')
    return password

def yesanswer(question):  #asks the question passed in and returns True if the answer is yes, False if the answer is no, and keeps the user in a loop until one of those is given.  Also useful for walking students through basic logical python functions
    answer = False  #initializes the answer variable to false.  Not absolutely necessary, since it should be undefined at this point and test to false, but explicit is always better than implicit
    while not answer:  #enters the loop and stays in it until answer is equal to True
        print (question + ' (Y/N)')  #Asks the question contained in the argument passed into this subroutine
        answer = raw_input('>>') #sets answer equal to some value input by the user
        if str(answer) == 'y' or str(answer) == 'Y':  #checks if the answer is a valid yes answer
            return True  #sends back a value of True because of the yes answer
        elif str(answer) == 'n' or str(answer) == 'N': #checks to see if the answer is a valid form of no
            return False  #sends back a value of False because it was not a yes answer
        else: #if the answer is not a value indicating a yes or no
            print ('Invalid response.')
            answer = False #set ansewr to false so the loop will continue until a satisfactory answer is given

def brokenhash():
    quit('This password has a broken hash.')
    
def safehash():
    quit('This password appears unbroken.')

def main():
    args = checkargs()
    if args:
        plaintext = args[0]
        mode = args[1]
        if mode == 'zeroInfo':
            zeroinfo = True
            insecure = False
        elif mode == 'insecure':
            insecure = True
            zeroinfo = False
        else:
            zeroinfo = False
            insecure = False
    else:
        plaintext = askforpassword()
        zeroinfo = False
        insecure = False
    passhash = gethash(plaintext)
    if bingsearch(passhash, plaintext):
        print('Bing.')
        brokenhash()
    results = googleresults(passhash, plaintext)
    if not results:
        quit('Unable to connect to Google.')
    crackcache = results[0]
    cracksites = results[1]
    if crackcache or cracksites:
        if crackcache:
            if crackedonweb(passhash, plaintext, crackcache):
                brokenhash()
            else:
                if not zeroinfo and (insecure or yesanswer("No crack of this password was found on a cached Google site.\nShould we check the sites directly? (Requires communication with cracking sites)")):
                    if crackedonweb(passhash, plaintext, cracksites):
                        brokenhash()
                    else:
                        if yesanswer("No crack was found using Google.\nTry known cracking sites?"):
                            if crackedonweb(passhash, plaintext):
                                brokenhash()
                            else:
                                safehash()
                        else:
                            safehash()
            if not zeroinfo and (insecure or yesanswer("No pages cached by Google were returned, but some sites were found.\nShould we check the sites directly? (Requires communication with cracking sites)")):
                if crackedonweb(passhash, plaintext, cracksites):
                    brokenhash()
                else:
                    if yesanswer("No crack was found using Google.\nTry known cracking sites?"):
                        if crackedonweb(passhash, plaintext):
                            brokenhash()
                        else:
                            safehash()
            else:
                safehash()
    elif zeroinfo:
        safehash()
    else:                
            if not zeroinfo and (insecure or yesanswer("No Google results were returned.\nTry known cracking sites? (Requires communication with cracking sites)")):
                if crackedonweb(passhash, plaintext):
                    brokenhash()
                else:
                    safehash()
    quit('Goodbye')

main()
    
    