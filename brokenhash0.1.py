#!/usr/bin/env python3

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
    return bytes(stringin, 'utf-8')

def cookhashbytes(passhash):
    return passhash.hexdigest()

def cookbytes(rawbytes):
    return str(rawbytes.decode('utf-8'))

def crackedonweb(passhash, plaintext):
    import urllib
    cracksites = ['http://md5.znaet.org/md5/', 'http://www.md5-hash.com/md5-hashing-decrypt/', 'http://md5cracker.org/decrypted-md5-hash/', 'http://md5reverse.insdy.net/decrypt_md5/']
    #could this be sped up by doing each site as a thread in a multithreading scheme?
    #this could be more powerful by having it do a POST the site and search each one through its own engine if they can't take the hash on the URL line
    #the ideal would be to feed it as a google search and regex the google result page, but that would require getting google to play ball
    for site in cracksites:
        try:
            response = urllib.request.urlopen(site + passhash)
        except :
            continue
        searchresult = response.read()
        if searchresult:
            if foundinresult(plaintext, searchresult):
                return True
        else:
            continue
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
    if crackedonweb(passhash, plaintext):
        print('This password has a broken hash')
    else:
        print('This password is safe.')
    quit('Goodbye')

main()
    
    