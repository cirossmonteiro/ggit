import functools
import glob
import hashlib
import os
import shutil

def is_file_staged(path):
    for file in open("./.ggit/wip"):
        if path[2:] == file:
            return True
    return False

def wip_append(path):
    with open(".ggit/wip") as fh:
        for file in fh:
            if file[:-1] == path:
                return
    if get_file_status(path) != 1:
        with open(".ggit/wip", 'a') as fh:
            fh.write(path+'\n')

def get_file_status(path):
    with open("./.ggit/head") as fh:
        head = fh.read()
    with open("./.ggit/tree") as fh:
        tree = [line.split(' ') for line in fh.read().split('\n')]
    file_status = 0

    # search for file in commits
    current = head
    while current != '':
        file_commited = f".ggit/commits/{current}/{path[1:]}"

        if os.path.isfile(file_commited): # file's been found
            with open(path) as current_file:
                with open(file_commited) as commmited_file:
                    if current_file.read() == commmited_file.read():
                        file_status = 1
                    else:
                        file_status = 2
            break

        for commit in tree:
            if commit[0] == current:
                current = commit[1] # parent
                break

    # if file_found == 0:
    #     print("File created: ", path)
    # elif file_found == 1:
    #     print("File preserved: ", path)
    # if file_found == 2:
    #     print("File modified: ", path)
    
    return file_status

class Style():
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    RESET = "\033[0m"

class Ggit:
    @staticmethod
    def init():
        os.mkdir(".ggit")
        os.mkdir(".ggit/commits")
        with open(".ggit/branches", 'w') as fh:
            fh.write(f"master")
        with open(".ggit/wip", 'w') as fh:
            fh.write("")
        with open(".ggit/head", 'w') as fh:
            fh.write("")
        with open(".ggit/tree", 'w') as fh:
            fh.write("")

    @staticmethod
    def add(gterms):
        # to-do: check for changes, use code from status
        for gterm in gterms:
            terms = glob.glob(gterm, recursive=True)
            for term in terms:
                if os.path.isfile(term):
                    wip_append(term)
                if os.path.isdir(term):
                    for subdir, dirs, files in os.walk(term):
                        for file in files:
                            if "./.ggit" not in subdir and "./.git" not in subdir:
                                wip_append(f"{subdir}/{file}")

    @staticmethod
    def commit():
        # concating contents from all staged files changed
        with open("./.ggit/wip") as fh:
            files = [file[:-1] for file in fh.readlines()]
        files.sort()
        contents = ""
        for file in files:
            with open(file) as fh:
                contents += fh.read()
        sha = hashlib.sha256(bytes(contents, 'ascii')).hexdigest()
        commit_dir = f"./.ggit/commits/{sha}"
        os.mkdir(commit_dir)
        for file in files:
            file = file.replace("./", '')

            # removing filename from path
            commit_file = f"{commit_dir}/{file}"
            create_dir = '/'.join(commit_file.split('/')[:-1])

            if not os.path.exists(create_dir):
                os.makedirs(create_dir)

            shutil.copy(file, commit_file)

        with open("./.ggit/wip", 'w') as fh:
            fh.write("")
        with open("./.ggit/head") as fh:
            head = fh.read()
        with open("./.ggit/tree", 'a') as fh:
            fh.write(f"{sha} {head}\n")
        with open("./.ggit/head", 'w') as fh:
            fh.write(sha)

    @staticmethod
    def status():
        with open("./.ggit/head") as fh:
            head = fh.read()
        with open("./.ggit/tree") as fh:
            tree = [line.split(' ') for line in fh.read().split('\n')]
        all_files = []
        for subdir, dirs, files in os.walk('.'):
            for file in files:
                if "./.ggit" not in subdir and "./.git" not in subdir:
                    path = f"{subdir}/{file}"
                    file_status = get_file_status(path)                        
                    all_files.append((path, file_status,))
        
        print("Changes to be committed:")
        for file, status in all_files:
            if is_file_staged(file):
                print("    ", Style.GREEN, file, Style.RESET)
        
        print("\nUntracked files:")
        for file, status in all_files:
            if status == 0:
                print("    ", Style.RED, file, Style.RESET)