#!/usr/bin/env python3
'''
Simplified test for automated checking of passwords for broken hash.
Now powered by Bing instead of Google due to Google having too many defenses.
Copyright 2014  Michael M. Weinstein
'''

def promptForPassword():
    import getpass
    password1 = getpass.getpass(" Enter password to test: ")
    password2 = getpass.getpass("Please confirm password: ")
    if not password1 == password2:
        return False
    return password1

class BrokenHashCheck(object):
    
    def __init__(self, searchEngine = "bing"):
        self.searchEngine = searchEngine
        
    def hashIsBroken(self, plaintext):
        passhash = self.gethash(plaintext)
        passhashUpper = self.gethash(plaintext.upper())
        passhashLower = self.gethash(plaintext.lower())
        if self.foundonbing(passhash, plaintext):
            return True
        elif self.foundonbing(passhashUpper, plaintext.upper()):
            return True
        elif self.foundonbing(passhashLower, plaintext.lower()):
            return True
        else:
            return False
        
    def gethash(self, password):
        import hashlib 
        passhash = hashlib.md5(self.rawbytes(password))
        passhash = self.cookhashbytes(passhash)
        return passhash
    
    def rawbytes(self, stringin):
        return bytes(stringin, 'utf-8')
    
    def cookhashbytes(self, passhash):
        return passhash.hexdigest()
    
    def cookbytes(self, rawbytes):
        return str(rawbytes.decode('utf-8'))
    
    def crackedonweb(self, passhash, plaintext, cracksites):
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
                if self.foundinresult(plaintext, searchresult):
                    return True
            else:
                continue
        return False
    
    def foundonbing(self, passhash, plaintext):  #Bing has little or no protection against automated searching.  Lucky us.
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
        if self.foundinresult(plaintext, result):
            return True
        if self.foundinresult('No results found for ' + passhash + '.',result):
            return False
        binglist = []
        resultsbody = re.search('\d+? results\<(.+)', result) #self.cookbytes(result))
        if resultsbody:
            resultsbody = resultsbody.group(0)
            binglist = re.findall('\<a href=\"(http:\/\/.+?)\"', resultsbody)
            if binglist:
                if crackedonweb(passhash, plaintext, binglist):
                    return True
        return False
        
    def foundinresult(self, plaintext, searchresult):
        found = plaintext in searchresult
        if found:
            return True
        else:
            return False
    
if __name__ == '__main__':
    import datetime
    start = datetime.datetime.now()
    password = ""
    while not password:
        password = promptForPassword()
        if not password:
            print("Invalid or unmatching entry. Please enter again.")
    checker = BrokenHashCheck()
    broken = checker.hashIsBroken(password)
    if broken:
        print("WARNING: This password is broken.")
    else:
        print("This password appears safe.")
    