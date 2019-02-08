def load(credentials_file, sep="\t"):
    git_username = []
    git_access_token = []
    with open(credentials_file) as file_in:
        header = next(file_in)
        for line in file_in:
            user, token = line.split(sep)
            git_username.append(user.strip())
            git_access_token.append(token.strip())

    return git_username, git_access_token
