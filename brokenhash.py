#!/usr/bin/env python3
'''
Checking passwords for broken hashes.  Now powered by Google's search engine.
Copyright 2017  Michael M. Weinstein
'''

global verbose
verbose = False

def checkargs():
    import argparse 
    parser = argparse.ArgumentParser()
    parser.add_argument ("-t", "--threads", help = "Number of threads to use", type = int, default = 10)
    parser.add_argument ("-c", "--givenCaseOnly", help = "Do not try different cases of the same plaintext", action = 'store_true')
    parser.add_argument ("-l", "--searchResultLimit", help = "Limit the number of search results to get back", type = int, default = 20)
    args = parser.parse_args()  
    return (args.threads, args.givenCaseOnly, args.searchResultLimit)

def hashIsBroken(plaintext, threads = 10, givenCaseOnly = False, searchResultLimit = 100):
    hashpairs = [(plaintext, gethash(plaintext))]
    if not givenCaseOnly:
        if not plaintext.upper() == plaintext:
            hashpairs.append((plaintext.upper(), gethash(plaintext.upper())))
        if not plaintext.lower() == plaintext:
            hashpairs.append((plaintext.upper(), gethash(plaintext.upper())))
    for pair in hashpairs:
        tempPlain, tempHash = pair
        if foundonbing(tempHash, tempPlain, threads, searchResultLimit):
            return True
    for pair in hashpairs:
        tempPlain, tempHash = pair
        if foundongoogle(tempHash, tempPlain, threads, searchResultLimit):
            return True
    else:
        return False
           
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

def foundongoogle(passhash, plaintext, threads, searchResultLimit):
    import google
    urlList = google.search(passhash, stop = searchResultLimit)
    if not urlList:
        return False
    if foundInMultithreadedURLSearch(urlList, plaintext, threads):
        return True
    else:
        return False
    
def foundonbing(passhash, plaintext, threads, searchResultLimit = 0):  #Bing has little or no protection against automated searching.  Lucky us.  Search is not as good, though.
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
    resultsbody = re.search('\d+? results\<(.+)', cookbytes(result))
    if resultsbody:
        resultsbody = resultsbody.group(0)
        binglist = re.findall('\<a href=\"(http:\/\/.+?)\"', resultsbody)
        if searchResultLimit:
            binglist = binglist[0:searchResultLimit]
        if binglist:
            if foundInMultithreadedURLSearch(binglist, plaintext, threads):
                return True
    return False
    
def foundinresult(plaintext, searchresult):
    found = rawbytes(plaintext) in searchresult
    if found:
        return True
    else:
        return False

def makeMatrix(linearList, rowLength, limit = 0):
    if not linearList:
        return []
    if limit:
        linearTrim = linearList[0:limit]
    currentColumn = 0
    currentRow = 0
    matrix = [[]]
    for item in linearTrim:
        if currentColumn == rowLength:
            matrix.append([])
            currentColumn = 0
            currentRow += 1
        matrix[currentRow].append(item)
        currentColumn += 1
    return matrix
    
def foundInMultithreadedURLSearch(urls, plaintext, threads):
    import multiprocessing.pool
    import urllib.request
    
    def getURL(url):
        try:
            response = urllib.request.urlopen(url, timeout = 3)
            return url, response.read(), None
        except Exception as e:
            return url, b"", e
    
    results = multiprocessing.pool.ThreadPool(threads).imap_unordered(getURL, urls)
    text = ""
    for url, html, error in results:
        if rawbytes(plaintext) in html:
            return True
    return False
    
def askforpassword():
    import getpass
    password = False
    while not password:
        password1 = getpass.getpass(' Enter password to test: ')
        password2 = getpass.getpass('Please confirm password: ')
        if not password1 == password2:
            print("Passwords did not match. Please try again.")
            password = False
        else:
            password = password1
    return password

if __name__ == '__main__':
    import datetime
    verbose = True
    start = datetime.datetime.now()
    plaintext = "harry7potter" # askforpassword()
    threads, givenCaseOnly, searchResultLimit = checkargs()
    if hashIsBroken(plaintext, threads, givenCaseOnly, searchResultLimit):
        print('This password has a broken hash')
    else:
        print('This password appears unbroken')
    print("Completed in %s" %(datetime.datetime.now() - start))