#!/usr/bin/python
import requests
import re
device = input("Codename: ")

content = requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/miui/full/{}.md".format(device))

images = re.findall("\"\/.*\/.*\/.*\/\"",content.text)
for i in images:
    os=i[:-2].split("/")[1]
    ver= i[:-2].split("/")[-1]
    release = requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/{}/updates/{}/{}.md".format(os,device,ver))
    if "fastboot" not in release.text.lower():
        print("Skipping {}, no FastBoot Download found.".format(ver))
        continue
    print("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/{}/updates/{}/{}.md".format(os,device,ver))


print("Collecting {} puppies".format(device))