import github
from github import Auth
import time
import os
import shutil
import subprocess
import ntpath
import re


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def update_progress(workdone, description = "Progress"):
    print("\r" + description + ": [{0:50s}] {1:.1f}%".format('#' * int(workdone * 50), workdone*100), end="", flush=True)


def is_version(a):
    alpha_count = 0
    for cur_char in a:
        if cur_char.isalpha(): alpha_count += 1
    if alpha_count == 1: return True
    else: return False


def init_git():
    auth = Auth.Token("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")
    g = github.Github(auth=auth)
    if g.get_user().login == "psjv": print("Connected to user")
    global repo
    repo = g.get_repo("psjv/a")


def print_content():
    contents = repo.get_contents("")
    print(bcolors.OKBLUE + "List of content:" + bcolors.ENDC)
    for content_file in contents:
        print(content_file.name)


def delete_prev_versions():
    regstr = input("Regex of files to delete: ")
    pattern = re.compile(regstr)
    print(bcolors.OKBLUE + "Deleting next files:" + bcolors.ENDC)
    found = 0
    contents = repo.get_contents("")
    for content_file in contents:
        if pattern.match(content_file.name):
            print(bcolors.WARNING + content_file.name + bcolors.ENDC)
            found += 1
    if found == 0: print(bcolors.WARNING + "<No files to delete>" + bcolors.ENDC)

    if input("Confirm deletion [y/n]: ") != "y":
        print(bcolors.FAIL + "Process aborted" + bcolors.ENDC)
        return

    delcnt = 0
    for content_file in contents:
        if pattern.match(content_file.name):
            repo.delete_file(content_file.path, "remove prev version", content_file.sha, branch="main")
            delcnt += 1
            update_progress(delcnt / found)

    print()
    print(bcolors.OKGREEN + "Successfully ended file deletion process" + bcolors.ENDC)


cur_directory = os.getcwd()
catalog_directory = cur_directory + "\\catalog\\"
publish_directory = cur_directory + "\\publish\\"

def publish_files():
    catalog_name = input("Catalog name: ")
    catalog_path = catalog_directory + catalog_name
    if os.path.isfile(catalog_path): print(bcolors.OKGREEN + "Found file" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + f'File {catalog_path} not found' + bcolors.ENDC)
        print(bcolors.FAIL + "Process aborted" + bcolors.ENDC)
        return

    for filename in os.listdir(publish_directory):
        file_path = os.path.join(publish_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    major_version = catalog_name[:1]
    minor_version = catalog_name[2:]
    publish_pathes = []
    for i in range(26):
        cur_path = publish_directory + major_version + chr(97 + i) + minor_version
        shutil.copyfile(catalog_path, cur_path)
        publish_pathes.append(cur_path)

    print(bcolors.OKGREEN + "Copied all files to destination directory" + bcolors.ENDC)
    i = 0
    for path in publish_pathes:
        cmds = "\"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.22000.0\\x64\\signtool.exe\" sign /a /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 " + "\"" + path + "\""
        subprocess.Popen(cmds, shell=True, stdout=subprocess.PIPE)
        i += 1
        update_progress(i / 26, "Signing")
        time.sleep(2)
    print()
    print(bcolors.OKGREEN + "Signed all files" + bcolors.ENDC)
    if input(bcolors.WARNING + "Check manually if signing was successful. Publish to github? [y/n]: " + bcolors.ENDC) != "y":
        print(bcolors.FAIL + "Process aborted" + bcolors.ENDC)
        return
    i = 0
    for path in publish_pathes:
        with open(path, 'rb') as file:
            content = file.read()
        repo.create_file(ntpath.basename(path), 'new_version', content, branch='main')
        i += 1
        update_progress(i / 26, "Publishing")

    print()
    print(bcolors.OKGREEN + "Published successfully" + bcolors.ENDC)


def edit_connection(connection_file):
    contents = repo.get_contents(connection_file)
    print(bcolors.OKBLUE + "Content: " + bcolors.ENDC, end="")
    print(contents.decoded_content)
    new_content = input("Input new name (or [no]): ")
    if (new_content == "no"):
        print(bcolors.FAIL + "Process aborted" + bcolors.ENDC)
        return
    repo.update_file(contents.path, "changed link", '5lp3l4zn33(fileURL) https://raw.githubusercontent.com/psjv/a/main/'+new_content, contents.sha, branch="main")
    print(bcolors.OKGREEN + "Changed successfully" + bcolors.ENDC)



if __name__ == '__main__':
    init_git()
    while True:
        print()
        command = input("Enter command [list/del/pub/con/cod/exit]: ")
        if command == "list": print_content()
        elif command == "del": delete_prev_versions()
        elif command == "pub": publish_files()
        elif command == "con": edit_connection("con")
        elif command == "cod": edit_connection("cod")
        elif command == "exit": exit(0)







# See PyCharm help at https://www.jetbrains.com/help/pycharm/
