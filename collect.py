#!/usr/bin/python
import requests
import re
from bs4 import BeautifulSoup
from env import TOKEN
from github import Github,Auth,UnknownObjectException



#device = input("Codename: ")
device="spes"
user = "MIUI-MIRROR"
auth = Auth.Token(TOKEN)
hub = Github(auth=auth)
repo = hub.get_repo("{}/{}".format(user,device))
print(repo.url)
content = requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/miui/full/{}.md".format(device))
fb_rom_regex=''' *<li style=\"padding-bottom: 10px;\">
 *<h5><b>Type: </b>Fastboot</h5>
 *</li>
 *<li style=\"padding-bottom: 10px;\">
 *<h5><b>Size: </b>\d*[.]\d GB</h5>
 *</li>'''

def sortInternal(list):
    list.sort(key=lambda x: x[1])
    return list

images = set(re.findall("\"\/.*\/.*\/.*\/\"",content.text))
#dload_size = 0 #GB
total_size = 0 #GB

allowed_domains = "cdn-ota\.azureedge\.net|cdnorg\.d\.miui\.com|bn\.d\.miui\.com"
valid_url_regex = "https://({})/.*\.tgz".format(allowed_domains)
releases =[]

for i in images:
    os=i[:-2].split("/")[1]
    ver= i[:-2].split("/")[-1]
    release = requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/{}/updates/{}/{}.md".format(os,device,ver))
    if "fastboot" not in release.text.lower():
        print("Skipping {}, no FastBoot Download found.".format(ver))
        continue
    print("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/{}/updates/{}/{}.md".format(os,device,ver))
    fb_size = re.findall(fb_rom_regex,release.text)
    if len(fb_size) != 1:
        print("Something went wrong. Exiting.")
        continue
    actual_size = float(re.search("\d*[.]\d* GB",fb_size[0]).group()[:-3]) # remove " GB"
    print(actual_size)
    total_size +=actual_size
    prettified_page = BeautifulSoup(requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/{}/updates/{}/{}.md".format(os,device,ver)).text).prettify()
    all_links = re.findall(" *<button class=\"btn btn-primary\" id=\"download\" onclick=\"window\.open\('https://.*\.tgz', '_blank'\);\" style=\"margin: 7px;\" type=\"button\">",prettified_page)
    links = []
    for k in all_links:
        f=re.search(valid_url_regex, k)
        if f:
            links.append(f[0])
    print(links)
    releases.append([os,ver,links,actual_size])

print("Collecting {} puppies".format(device))
print("Xiaomi has {} GB of puppies".format(total_size))

releases = sortInternal(releases)

for i in releases:
    print(i[3])
    try:
        repo.get_release(i[1]) # This will error out if the repo does not have this release.
        print("Release found for {}".format(i[1]))
        releases.remove(i)
        total_size -= i[3]
    except UnknownObjectException:
        print("No release found for {}".format(i[1]))

print("Need to download {} gigabytes of images".format(total_size))
