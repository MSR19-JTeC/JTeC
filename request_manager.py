import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

from contextlib import closing

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def request(url, git_username, git_access_token, switch_account):
    # print("URL:", url)
    call_counter = 0
    while True:
        if call_counter == 15:
            print("Goodnight! See ya in 1 hour...")
            time.sleep(3600)

        s = requests.Session()
        s.auth = (git_username[switch_account], git_access_token[switch_account])
        # s.headers.update({"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)", "Referer": "http://example.com"})

        try:
            with closing(requests_retry_session(session=s).get(url, timeout=5)) as temp_json:
                ret_json = temp_json.json()
        except Exception as e:
            raise e

        if type(ret_json) != list:
            if "message" in ret_json.keys():
                if "API rate limit exceeded for user ID" in ret_json["message"]:
                    switch_account = (switch_account + 1) % len(git_username)
                    call_counter += 1
                    print("\tSkipping {}".format(git_username[switch_account]), "| Message:", ret_json["message"])
                elif "Repository access blocked" in ret_json["message"] or "Not Found" == ret_json["message"]:
                    print("Repository access blocked OR Not Found")
                    return 0, switch_account
                elif "No commit found for SHA: master" in ret_json["message"]:
                    return 1, switch_account
                elif "Git Repository is empty." in ret_json["message"]:
                    return 2, switch_account
                elif "No commit found for SHA" in ret_json["message"]:
                    return 3, switch_account
            else:
                return ret_json, switch_account
        else:
            return ret_json, switch_account
