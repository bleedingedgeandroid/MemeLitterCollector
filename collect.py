#!/usr/bin/python
import requests
import re
from bs4 import BeautifulSoup
from env import TOKEN
from github import Github,Auth,UnknownObjectException
import os as OS
from urllib.parse import urlparse

#device = input("Codename: ")
device="spes"
user = "MIUI-MIRROR"
auth = Auth.Token(TOKEN)
hub = Github(auth=auth)
repo = hub.get_repo("{}/{}".format(user,device))
print(repo.url)
content = requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/miui/full/{}.md".format(device))
size_regex="\d*\.?\d* GB"
def sortInternal(list):
    list.sort(key=lambda x: x[1])
    return list
def summation(sizes):
    j = 0 # GB
    for k in sizes:
        j += float(k[:-3])
    return j
def seperateRecoveryFastboot(links):
    print(links)
    recovery = []
    fastboot = []
    for j in links:
        if j[-3:] == "tgz":
            print("Found FastBoot link {}".format(j))
            fastboot.append(j)
        elif j[-3:] == "zip":
            print("Found Recovery Link {}".format(j))
            recovery.append(j)
    return [fastboot,recovery]
images = set(re.findall("\"\/.*\/.*\/.*\/\"",content.text))
#dload_size = 0 #GB
total_size = 0 #GB

allowed_domains = "cdn-ota\.azureedge\.net|cdnorg\.d\.miui\.com|bn\.d\.miui\.com"
valid_url_regex = "https:\/\/(?:{})/.*\.(?:zip|tgz)".format(allowed_domains)
releases =[]

for i in images:
    os=i[:-2].split("/")[1]
    ver= i[:-2].split("/")[-1]
    release = requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/{}/updates/{}/{}.md".format(os,device,ver))
    print("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/{}/updates/{}/{}.md".format(os,device,ver))
    actual_size = summation(re.findall(size_regex,release.text))
    print(actual_size)
    total_size +=actual_size
    prettified_page = BeautifulSoup(release.text).prettify()
    all_links = re.findall(valid_url_regex,prettified_page)
    links = seperateRecoveryFastboot(all_links)
    releases.append([os,ver,links,actual_size])

print("Collecting {} puppies".format(device))
print("Xiaomi has {} GB of puppies".format(total_size))

releases = sortInternal(releases)

for i in releases:
    try:
        repo.get_release(i[1]) # This will error out if the repo does not have this release.
        print("Release found for {}".format(i[1]))
        releases.remove(i)
        total_size -= i[3]
    except UnknownObjectException:
        print("No release found for {}".format(i[1]))

print("Need to download {} gigabytes of images".format(total_size))
m = releases[1]
print("Downloading FastBoot Images for {}".format(m[1]))
filename = OS.path.basename(urlparse(m[2][0][0]).path)
valid_url_arg = ' '.join(m[2][0])
print('axel -c -n 100 -U "MIUI-MIRROR-BOT/1.0" -o {} {}'.format(filename,valid_url_arg))
OS.system('axel -c -n 100 -U "MIUI-MIRROR-BOT/1.0" -o {} {}'.format(filename,valid_url_arg))
print("Splitting FastBoot Images for {}".format(m[1]))
OS.system("split -d -b 1950MB {} {}.part".format(filename,filename))
print("Downloading Recovery Images for {}".format(m[1]))
filename = OS.path.basename(urlparse(m[2][1][0]).path)
valid_url_arg = ' '.join(m[2][1])
print('axel -c -n 100 -U "MIUI-MIRROR-BOT/1.0" -o {} {} '.format(filename,valid_url_arg))
OS.system('axel -c -n 100 -U "MIUI-MIRROR-BOT/1.0" -o {} {}'.format(filename,valid_url_arg))
print("Splitting Recovery Images for {}".format(m[1]))
OS.system("split -d -b 1950MB {} {}.part".format(filename,filename))