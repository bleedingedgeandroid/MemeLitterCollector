#!/usr/bin/python
import requests
import re
from bs4 import BeautifulSoup
from env import TOKEN, DEVICE, USER, REPO, MAX_THREADS
from github import Github, Auth, UnknownObjectException
import os as host
from urllib.parse import urlparse
import math
import yaml
import strings
from multiprocessing.pool import ThreadPool


authorization_token = Auth.Token(TOKEN)
github_remote = Github(auth=authorization_token)
mirror_repository = github_remote.get_repo("{}/{}".format(USER, REPO))
device_images = requests.get("https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io"
                             "/master/pages/miui/full/{}.md".format(DEVICE))
size_regex = r"\d*\.?\d* GB"

print("Script powered by XiaomiFirmwareUpdater")
def sort_nestedlist(nested_list):
    nested_list.sort(key=lambda os_entry: os_entry[1])
    return nested_list


def summation(sizes):
    j = 0  # GB
    for k in sizes:
        j += float(k[:-3])
    return j


def separate_recovery_and_fastboot_links(mixed_links):
    recovery = []
    fastboot = []
    for j in mixed_links:
        if j[-3:] == "tgz":
            print("Found FastBoot link {}".format(j))
            fastboot.append(j)
        elif j[-3:] == "zip":
            print("Found Recovery Link {}".format(j))
            recovery.append(j)
    return [fastboot, recovery]


images = set(re.findall(r"\"/.*/.*/.*/\"", device_images.text))
total_size = 0  # GB

allowed_domains = r"cdn-ota\.azureedge\.net|cdnorg\.d\.miui\.com|bn\.d\.miui\.com"
valid_url_regex = r"https:\/\/(?:{})/.*\.(?:zip|tgz)".format(allowed_domains)
releases = []

for i in images:
    os = i[:-2].split("/")[1]
    ver = i[:-2].split("/")[-1]
    release = requests.get(
        "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/"
        "{}/updates/{}/{}.md".format(
            os, DEVICE, ver))
    print(
        "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/xiaomifirmwareupdater.github.io/master/pages/"
        "{}/updates/{}/{}.md".format(
            os, DEVICE, ver))
    actual_size = summation(re.findall(size_regex, release.text))
    print(actual_size)
    total_size += actual_size
    prettified_page = BeautifulSoup(release.text).prettify()
    data_str = re.findall("(?s)---.*---", prettified_page)[0][:-3]
    data_yml = yaml.safe_load(data_str)
    data_str = "# {} \n\r# {}".format(data_yml['name'], data_yml['title'])
    all_links = re.findall(valid_url_regex, prettified_page)
    links = separate_recovery_and_fastboot_links(all_links)
    releases.append([os, ver, links, actual_size, data_str])

print("Collecting {} puppies".format(DEVICE))
print("Xiaomi has {} GB of puppies".format(total_size))

releases = sort_nestedlist(releases)

for i in releases:
    try:
        mirror_repository.get_release(i[1])  # This will error out if the repo does not have this release.
        print("Release found for {}".format(i[1]))
        releases.remove(i)
        total_size -= i[3]
    except UnknownObjectException:
        print("No release found for {}".format(i[1]))

print("Need to download {} gigabytes of images".format(total_size))


def download_and_upload(m):
    files_fb = ""
    fastboot_filename = ""
    files_r = ""
    filename_r = ""
    if not len(m[2][0]) == 0:
        print("Downloading FastBoot Images for {}".format(m[1]))
        fastboot_filename = host.path.basename(urlparse(m[2][0][0]).path)
        axel_url_argument = ' '.join(m[2][0])
        host.system('axel -p -c -U "MIUI-MIRROR-BOT/1.0" -o {} {} > axel.log.{}'.format(fastboot_filename, axel_url_argument,fastboot_filename))
        print("Splitting FastBoot Images for {}".format(m[1]))
        host.system("split -d -a 1 -b 1950MB {} {}.part".format(fastboot_filename, fastboot_filename))
        fastboot_file_size = host.stat(fastboot_filename).st_size / (1000 * 1000)
        fastboot_parts = math.ceil(fastboot_file_size / 1950)
        files_fb = []
        for x in range(fastboot_parts):
            print("Added FastBoot part {}".format(x))
            files_fb.append(fastboot_filename + ".part{}".format(x))
    if not len(m[2][1]) == 0:
        print("Downloading Recovery Images for {}".format(m[1]))
        filename_r = host.path.basename(urlparse(m[2][1][0]).path)
        axel_url_argument = ' '.join(m[2][1])
        host.system('axel -p -c -U "MIUI-MIRROR-BOT/1.0" -o {} {} > axel.log.{} '.format(filename_r, axel_url_argument,filename_r))
        print("Splitting Recovery Images for {}".format(m[1]))
        host.system("split -d -a 1 -b 1950MB {} {}.part".format(filename_r, filename_r))
        recovery_file_size = host.stat(filename_r).st_size / (1000 * 1000)
        recovery_parts = math.ceil(recovery_file_size / 1950)
        files_r = []
        for x in range(recovery_parts):
            print("Added Recovery part {}".format(x))
            files_r.append(filename_r + ".part{}".format(x))
    if (not len(m[2][0]) == 0) and (not len(m[2][0]) == 0):
        release_notes = strings.release_notes_both.format(data=m[4], fileparts_tgz=' '.join(files_fb),
                                                          filename_fb=fastboot_filename,
                                                          fileparts_zip=' '.join(files_r),
                                                          fileparts_tgz_win='+'.join(files_fb),
                                                          fileparts_zip_win='+'.join(files_r), filename_r=filename_r)
    elif len(m[2][1]) == 0:
        release_notes = strings.release_notes_fb.format(data=m[4], fileparts_tgz=' '.join(files_fb),
                                                        filename_fb=fastboot_filename,
                                                        fileparts_tgz_win='+'.join(files_fb))
    else:
        release_notes = strings.release_notes_r.format(data=m[4], fileparts_zip=' '.join(files_r),
                                                       fileparts_zip_win='+'.join(files_r), filename_r=filename_r)

    github_release = mirror_repository.create_git_tag_and_release(tag=m[1], tag_message=m[1], release_name=m[1],
                                                                  release_message=release_notes,
                                                                  object=mirror_repository.get_branch(
                                                                      mirror_repository.default_branch).commit.sha,
                                                                  type="commit")
    if not len(m[2][1]) == 0:
        for m in files_r:
            print("Uploading Recovery part {}".format(m))
            github_release.upload_asset(path=m)
            host.remove(m)

    if not len(m[2][0]) == 0:
        for m in files_fb:
            print("Uploading FastBoot part {}".format(m))
            github_release.upload_asset(path=m)
            host.remove(m)

    host.remove(fastboot_filename)
    host.remove(filename_r)




thread_pool = ThreadPool(MAX_THREADS)

for m in releases:
    thread_pool.apply_async(download_and_upload, (m,))

thread_pool.close()
thread_pool.join()
