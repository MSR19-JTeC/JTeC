from collections import defaultdict
import os

csv_in = "Java_repositories.csv"
csv_out = "Java_repositories_to_download.csv"

repoIDs = defaultdict(int)
repoForks = defaultdict(set)
tcs = 0

with open(csv_in) as infile:
    h = next(infile)
    for line in infile:
        repo_id, user, repo, fork_id, last_commit_sha, commit_date, number_of_tests = line.strip().split(",")
        repoIDs[repo_id] = int(number_of_tests)

        tcs += int(number_of_tests)

        if fork_id != "-":
            repoForks[fork_id].add(repo_id)


print("Number of repositories with test classes (with forks):", len(repoIDs))
print("Number of test classes (with forks):", tcs)

toKeep = set()

for repo, forks in repoForks.items():
    if repo in repoIDs.keys():
        keepID, keepTests = repo, repoIDs[repo]
        for fork in forks:
            if repoIDs[fork] > keepTests:
                keepID, keepTests = fork, repoIDs[fork]
        toKeep.add(keepID)

tcs = 0
number_repositories_to_keep = 0
with open(csv_in) as infile, open(csv_out, "w") as file_out:
    h = next(infile)
    file_out.write("{},{},{},{},{},{},{}\n".format("repo_id", "user", "repo", "fork_id", "commit", "commit_date", "#tests"))
    for line in infile:
        repo_id, user, repo, fork_id, last_commit_sha, commit_date, number_of_tests = line.strip().split(",")
        if repo_id in toKeep and int(number_of_tests) > 0:
            tcs += int(number_of_tests)
            number_repositories_to_keep += 1
            file_out.write("{},{},{},{},{},{},{}\n".format(repo_id, user, repo, fork_id, last_commit_sha, commit_date, number_of_tests))

print("Number of repositories with test classes (no forks):", number_repositories_to_keep)
print("Number of test classes (no forks):", tcs)
