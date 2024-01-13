#!/usr/bin/python
import requests
import re
device = input("Codename: ")

content = requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/miui/full/{}.md".format(device))

images = set(re.findall("\"\/.*\/.*\/.*\/\"",content.text))
dload_size = 0 #GB
for i in images:
    os=i[:-2].split("/")[1]
    ver= i[:-2].split("/")[-1]
    release = requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/{}/updates/{}/{}.md".format(os,device,ver))
    if "fastboot" not in release.text.lower():
        print("Skipping {}, no FastBoot Download found.".format(ver))
        continue
    print("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/{}/updates/{}/{}.md".format(os,device,ver))
    fb_size = re.findall(''' *<li style=\"padding-bottom: 10px;\">
 *<h5><b>Type: </b>Fastboot</h5>
 *</li>
 *<li style=\"padding-bottom: 10px;\">
 *<h5><b>Size: </b>\d*[.]\d GB</h5>
 *</li>''',release.text)
    if len(fb_size) != 1:
        print("Something went wrong. Exiting.")
        continue
    actual_size = float(re.search("\d*[.]\d* GB",fb_size[0]).group()[:-3]) # remove " GB"
    dload_size +=actual_size



print("Collecting {} puppies".format(device))
print("Xiaomi serious skill issue, left {} GB of puppies behind".format(dload_size))