import os
import base64
import csv
import credentials, request_manager


def isJavaTest(file_name):
    return file_name[-5:] == ".java" and (file_name[-9:] == "Test.java" or file_name[:4] == "Test")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def get_size_and_loc(start_path):
    total_size = 0
    total_file_len = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
            total_file_len += file_len(fp)
    return total_size, total_file_len

def download(user_repo, tree_url, switch_account):
    tree_data, switch_account = request_manager.request("{}{}".format(tree_url, "?recursive=1"), git_username, git_access_token, switch_account)

    for file in tree_data["tree"]:
        if file["type"] == "blob" and isJavaTest(file["path"]):
            file_url = file["url"]

            data, switch_account = request_manager.request(file_url, git_username, git_access_token, switch_account)

            path = user_repo + "/".join(file["path"].split("/")[:-1])
            if not os.path.exists(path):
                os.makedirs(path)

            print("\t{}{}".format(user_repo, file["path"]))

            if data["encoding"] != "base64":
                print("\tFILE IS NOT BASE64!!!")
            else:
                with open(user_repo + file["path"], "wb") as file_out:
                    file_out.write(base64.b64decode(data["content"]))
    return switch_account


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def retrieve_master_tree(repo, user, commit, git_username, git_access_token, switch_account):
    master_url = "https://api.github.com/repos/{}/{}/commits/{}".format(user, repo, commit)
    master_data, switch_account = request_manager.request(master_url, git_username, git_access_token, switch_account)
    tree_url = master_data["commit"]["tree"]["url"]
    return tree_url, switch_account

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



if __name__ == "__main__":
    # personal Github Account credentials
    git_username, git_access_token = credentials.load("tokens.txt")

    repo_list = "Java_repositories_to_download.csv"

    if not os.path.isfile(repo_list):
        print(repo_list, "file is missing!")
        exit()

    visited_keys = set()
    csv_out = "JTeC.csv"
    if not os.path.isfile(csv_out):
        with open(csv_out, "w") as file_out:
            file_out.write("{},{},{},{},{},{},{},{},{}\n".format("repo_id", "user", "repo", "fork_id", "commit", "commit_date", "#tests", "size", "LOC"))
    else:
        with open(csv_out) as infile:
            h = next(infile)
            for line in infile:
                repo_id, user, repo, fork_id, last_commit_sha, commit_date, number_of_tests, size, LOC  = (x.strip() for x in line.split(","))
                visited_keys.add(int(repo_id))

    switch_account = 0

    with open(repo_list) as file_in, open(csv_out, "a") as file_out:
        h = next(file_in)
        for line in file_in:
            repo_id, user, repo, fork_id, last_commit_sha, commit_date, number_of_tests  = (x.strip() for x in line.split(","))

            size = "-"
            LOC = "-"
            if int(repo_id) not in visited_keys:
                user_repo = "JTeC/{}/{}/".format(user, repo)
                tree_url, switch_account = retrieve_master_tree(repo, user, last_commit_sha, git_username, git_access_token, switch_account)
                switch_account = download(user_repo, tree_url, switch_account)
                size, LOC = get_size_and_loc(user_repo)

                file_out.write("{},{},{},{},{},{},{},{},{}\n".format(repo_id, user, repo, fork_id, last_commit_sha, commit_date, number_of_tests, size, LOC))
            
