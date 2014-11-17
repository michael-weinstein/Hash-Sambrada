#!/usr/bin/env python3
'''
Simplified test for automated checking of passwords for broken hash.
Now powered by Bing instead of Google due to Google having too many defenses.
Copyright 2014  Michael M. Weinstein
'''
def checkargs():
    import argparse 
    parser = argparse.ArgumentParser()
    parser.add_argument ("-p", "--password", help = "Enter the plaintext of the password on the commandline")
    args = parser.parse_args()  
    if not (args.password):
        return False  #if they did not enter a password, run manually, regardless of what else was entered
    else:
        return (str(args.password))
    
def gethash(password):
    import hashlib 
    passhash = hashlib.md5(rawbytes(password))
    passhash = cookhashbytes(passhash)
    return passhash

def rawbytes(stringin):
    return bytes(stringin, 'utf-8')

def cookhashbytes(passhash):
    return passhash.hexdigest()

def cookbytes(rawbytes):
    return str(rawbytes.decode('utf-8'))

def crackedonweb(passhash, plaintext, cracksites):
    import urllib.request
    for site in cracksites:
        try:
            response = urllib.request.urlopen(site)
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

def foundonbing(passhash, plaintext):  #Bing has little or no protection against automated searching.  Lucky us.
    import urllib.request
    import re
    try:
        rawresult = urllib.request.urlopen('http://www.bing.com/search?q=' + passhash)
        result = rawresult.read()
    except IOError:
        quit('Unable to reach Bing')
    if foundinresult(plaintext, result):
        return True
    if foundinresult('No results found for ' + passhash + '.',result):
        return False
    binglist = []
    resultsbody = re.search('\>\d+? results\<(.+)', cookbytes(result))
    if resultsbody:
        resultsbody = resultsbody.group(0)
        binglist = re.findall('\<a href=\"(http:\/\/.+?)\"', resultsbody)
        if binglist:
            if crackedonweb(passhash, plaintext, binglist):
                return True
    return False
    
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
    if foundonbing(passhash, plaintext):
        quit('This password has a broken hash')
    else:
        quit('This password appears unbroken')

main()
