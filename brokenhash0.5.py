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
    parser.add_argument ("-m", "--md5", help = "Enter the hash value in hex digest format")
    args = parser.parse_args()  
    if not (args.password or args.md5):
        return False  #if they did not enter a password, run manually, regardless of what else was entered
    elif args.hash:
        validHexCharacters = ['A','B','C','D','E','F','a','b','c','d','e','f','0','1','2','3','4','5','6','7','8','9']
        for character in args.hash:
            if character not in validHexCharacters:
                print("Hash value given does not appear to be valid hex digest (contains inappropriate characters).")
                return False
            else:
                return (str(args.hash), 'hash')
    else:        
        return (str(args.password), 'plaintext')
    
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
    import requests
    import re
    try:
        searchForm = {'q':passhash,'qs':'bs',"QBLH":'form'}
        rawresult = requests.post('https://www.bing.com/search', data = searchForm)
        result = rawresult.text
        print(result.encode('utf-8'))
        print("Something")
    except IOError:
        quit('Unable to reach Bing')
    if foundinresult(plaintext, result):
        return True
    if foundinresult('No results found for ' + passhash + '.',result):
        return False
    binglist = []
    resultsbody = re.search('\d+? results\<(.+)', cookbytes(result))
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
    commandLineInput = checkargs()
    if commandLineInput:
        if commandLineInput(1) == 'hash':
            passhash = commandLineInput(0)
        else:
            plaintext = commandLineInput(0)
            passhash = False
    else:
        plaintext = askforpassword()
        passhash = False
    if not passhash:
        passhash = gethash(plaintext)
    if foundonbing(passhash, plaintext):
        quit('This password has a broken hash')
    else:
        quit('This password appears unbroken')

main()
