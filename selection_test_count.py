import json
import os
import subprocess
import sys

import credentials, request_manager


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def isJavaTest(file_name):
    return file_name[-5:] == ".java" and (file_name[-9:] == "Test.java" or file_name[:4] == "Test")

def isPythonTest(file_name):
    return file_name[-3:] == ".py" and (file_name == "tests.py" or file_name[:5] == "test_" or file_name[:6] == "tests_")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Count the number of test files in a project

def count_tests(tree_url, isTest, git_username, git_access_token, switch_account):
    try: 
        tree_data, switch_account = request_manager.request("{}{}".format(tree_url, "?recursive=1"), git_username, git_access_token, switch_account)
        return sum((1 for file in tree_data["tree"] if file["type"] == "blob" and isTest(file["path"]))), switch_account
    except TypeError:
        return False, False
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def change_branch(user, repo, git_username, git_access_token, switch_account):
    default_branch_url = "https://api.github.com/repos/{}/{}".format(user, repo)
    default_branch, switch_account = request_manager.request(default_branch_url, git_username, git_access_token, switch_account)
    default_branch = default_branch["default_branch"]

    master_url = "https://api.github.com/repos/{}/{}/commits/{}".format(user, repo, default_branch)
    master_data, switch_account = request_manager.request(master_url, git_username, git_access_token, switch_account)
    return master_data["commit"]["tree"]["url"], master_data["sha"], master_data["commit"]["committer"]["date"], switch_account

def retrieve_master_tree(line, git_username, git_access_token, switch_account):
    repo_id, user, repo, lang = (x.strip() for x in line.split(","))

    master_url = "https://api.github.com/repos/{}/{}/commits/master".format(user, repo)
    # print(user, repo)
    master_data, switch_account = request_manager.request(master_url, git_username, git_access_token, switch_account)
    if master_data == 1:
        return change_branch(user, repo, git_username, git_access_token, switch_account)
    if master_data == 2:
        return False, False, False, switch_account
    else:
        try:
            last_commit_sha = master_data["sha"]
            tree_url = master_data["commit"]["tree"]["url"]
            commit_date = master_data["commit"]["committer"]["date"]
        except KeyError:
            return change_branch(user, repo, git_username, git_access_token, switch_account)
        except TypeError:
            # master_data == False
            return False, False, False, switch_account
        return tree_url, last_commit_sha, commit_date, switch_account

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
    # personal Github Account credentials
    git_username, git_access_token = credentials.load("tokens.txt")

    if len(sys.argv) <= 1:
        print("You must provide a language in input.")
        exit()

    input_lang = sys.argv[1]
    if input_lang == "Java":
        isTest = isJavaTest
    elif input_lang == "Python":
        isTest = isPythonTest
    else:
        print("Input language not supported")
        exit()

    csv = "public_repositories.csv"
    csv_out = "{}_repositories.csv".format(input_lang)

    last_id = 0

    if not os.path.isfile(csv):
        print("'./public_repositories.csv' file is missing!")
        exit()

    if not os.path.isfile(csv_out):
        with open(csv_out, "w") as file_out:
            file_out.write("{},{},{},{},{},{},{}\n".format("repo_id", "user", "repo", "fork_id", "commit", "commit_date", "#tests"))
    else:
        if sum((1 for line in open(csv_out))) > 1:
            last_line = subprocess.check_output(["tail", "-1", csv_out]).decode("utf-8")
            last_id = int(last_line.split(",")[0].strip())

    switch_account = 0

    with open(csv) as file_in, open(csv_out, "a") as file_out:
        h = next(file_in)
        for line in file_in:
            # print(line)
            repo_id, user, repo, lang = (x.strip() for x in line.split(","))
            lang_list = lang.split(";")

            if int(repo_id) <= last_id:
                continue

            if input_lang in lang_list:  # for all used languages
                print(repo_id, user, repo)
                tree_url, last_commit_sha, commit_date, switch_account = retrieve_master_tree(line, git_username, git_access_token, switch_account)
                if type(tree_url) == type(True) and tree_url is False:
                    continue
                number_of_tests, switch_account = count_tests(tree_url, isTest, git_username, git_access_token, switch_account)
                if type(number_of_tests) == type(True) and number_of_tests is False:
                    continue

                base_url_2 = "https://api.github.com/repos/{}/{}".format(user, repo)
                repo_info, switch_account = request_manager.request(base_url_2, git_username, git_access_token, switch_account)

                # created_at = repo_info["created_at"]
                try:
                    fork_id = repo_info["parent"]["id"]
                except Exception as e:
                    fork_id = "-"

                print("{}/{} LANG: {} #tests: {}".format(user, repo, input_lang, number_of_tests))
                file_out.write("{},{},{},{},{},{},{}\n".format(repo_id, user, repo, fork_id, last_commit_sha, commit_date, number_of_tests))
