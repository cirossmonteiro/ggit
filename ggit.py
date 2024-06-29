import functools
import glob
import hashlib
import json
import os
import shutil
import time

HEAD_START = "0"*64

def is_file_staged(path):
    status = False
    with open("./.ggit/wip") as fh:
        for file in fh:
            if path[2:] == file:
                status = True
                break
    return status

def wip_append(tree, current, path):
    with open(".ggit/wip") as fh:
        for file in fh:
            if file[:-1] == path:
                return
    if get_file_status(tree, current, path) != 1:
        with open(".ggit/wip", 'a') as fh:
            fh.write(path+'\n')
    

def get_file_status(tree, current, path):
    # with open("./.ggit/head") as fh:
    #     current = fh.read()
    # with open("./.ggit/tree") as fh:
    #     tree = [(line[:64], line[65:129], json.loads(line[130:]), ) for line in fh]
    file_status, path = 0, path[2:]

    while current != HEAD_START:
        for commit in tree:
            if commit[0] == current:
                if path in commit[2]:
                    with open(path) as current_file:
                        if current_file.read() == commit[2][path]:
                            file_status = 1
                        else:
                            file_status = 2
                    current = HEAD_START
                    break
                else:
                    current = commit[1]
                    break
            

    """
    # search for file in commits
    current = head
    while current != HEAD_START:
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
        # print(33, 59, len(current), "0"*64)
    """
    # if file_found == 0:
    #     print("File created: ", path)
    # elif file_found == 1:
    #     print("File preserved: ", path)
    # if file_found == 2:
    #     print("File modified: ", path)
    # print(33, 64)
    return file_status

def wip_to_obj():
    obj = {}
    with open("./.ggit/wip") as fh:
        for file in fh:
            with open(file[:-1]) as fh:
                obj[file[2:-1]] = fh.read()
    return obj



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
            fh.write(HEAD_START)
        with open(".ggit/tree", 'w') as fh:
            fh.write("")

    @staticmethod
    def add(gterms):
        start_time = time.time()
        with open("./.ggit/head") as fh:
            current = fh.read()
        with open("./.ggit/tree") as fh:
            tree = [(line[:64], line[65:129], json.loads(line[130:]), ) for line in fh]
        for gterm in gterms:
            terms = glob.glob(gterm, recursive=True)
            for term in terms:
                if os.path.isfile(term):
                    wip_append(tree, current, term)
                if os.path.isdir(term):
                    for subdir, dirs, files in os.walk(term):
                        for file in files:
                            if "./.ggit" not in subdir and "./.git" not in subdir:
                                wip_append(tree, current, f"{subdir}/{file}")
        print("Git add: %.2fs."%(time.time() - start_time))

    @staticmethod
    def commit():
        # concating contents from all staged files changed
        start_time = time.time()
        with open("./.ggit/wip") as fh:
            files = [file[:-1] for file in fh.readlines()]
        files.sort()
        contents = ""
        for file in files:
            with open(file) as fh:
                contents += fh.read()
        sha = hashlib.sha256(bytes(contents, 'ascii')).hexdigest()
        
        # commit_dir = f"./.ggit/commits/{sha}"
        # os.mkdir(commit_dir)
        # for file in files:
        #     file = file.replace("./", '')

        #     # removing filename from path
        #     commit_file = f"{commit_dir}/{file}"
        #     create_dir = '/'.join(commit_file.split('/')[:-1])

        #     if not os.path.exists(create_dir):
        #         os.makedirs(create_dir)

        #     shutil.copy(file, commit_file)
       
        obj = wip_to_obj()
        with open("./.ggit/head") as fh:
            head = fh.read()
        with open("./.ggit/tree", 'a') as fh:
            fh.write(f"{sha} {head} {json.dumps(obj)}\n")

        with open("./.ggit/wip", 'w') as fh:
            fh.write("")
        
        # with open("./.ggit/tree", 'a') as fh:
        #     fh.write(f"{sha} {head}\n")
        with open("./.ggit/head", 'w') as fh:
            fh.write(sha)
        
        print("Git commit: %.2fs."%(time.time() - start_time))

    @staticmethod
    def status():
        with open("./.ggit/head") as fh:
            current = fh.read()
        with open("./.ggit/tree") as fh:
            tree = [(line[:64], line[65:129], json.loads(line[130:]), ) for line in fh]
        all_files = []
        for subdir, dirs, files in os.walk('.'):
            for file in files:
                if "./.ggit" not in subdir and "./.git" not in subdir:
                    path = f"{subdir}/{file}"
                    file_status = get_file_status(tree, current, path)                        
                    all_files.append((path, file_status,))
        
        print("Changes to be committed:")
        for file, status in all_files:
            if is_file_staged(file):
                print("    ", Style.GREEN, file, Style.RESET)
        
        print("\nUntracked files:")
        for file, status in all_files:
            if status == 0:
                print("    ", Style.RED, file, Style.RESET)