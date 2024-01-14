#!/usr/bin/python
import requests
import re
from bs4 import BeautifulSoup
#device = input("Codename: ")
device="spes"
content = requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/miui/full/{}.md".format(device))
fb_rom_regex=''' *<li style=\"padding-bottom: 10px;\">
 *<h5><b>Type: </b>Fastboot</h5>
 *</li>
 *<li style=\"padding-bottom: 10px;\">
 *<h5><b>Size: </b>\d*[.]\d GB</h5>
 *</li>'''

images = set(re.findall("\"\/.*\/.*\/.*\/\"",content.text))
dload_size = 0 #GB

allowed_domains = "cdn-ota\.azureedge\.net|cdnorg\.d\.miui\.com|bn\.d\.miui\.com"
valid_url_regex = "https://({})/.*\.tgz".format(allowed_domains)
print(valid_url_regex)
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
    dload_size +=actual_size
    prettified_page = BeautifulSoup(requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/{}/updates/{}/{}.md".format(os,device,ver)).text).prettify()
    all_links = re.findall(" *<button class=\"btn btn-primary\" id=\"download\" onclick=\"window\.open\('https://.*\.tgz', '_blank'\);\" style=\"margin: 7px;\" type=\"button\">",prettified_page)
    links = []
    for k in all_links:
        f=re.search(valid_url_regex, k)
        if f:
            links.append(f[0])
    print(links)
    releases.append([os,ver,links])



print("Collecting {} puppies".format(device))
print("Xiaomi serious skill issue, left {} GB of puppies behind".format(dload_size))

