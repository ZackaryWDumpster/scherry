import logging
import requests
import datetime
from functools import cache
import parse
from scherry.utils.cfg import cfg
from scherry.utils.dictionary import ERROR, getDeep

info_parse = "{id}/{id2}/{branch}/{filename}"

@cache
def raw_resolve(url : str):
    """
    taking ZackaryW/scherry/main/scherry_bucket_test.zip
    return {
        "id" : ZackaryW/scherry
        "branch" : main  
        "filename" : scherry_bucket_test.zip    
    }
    
    """
    res = parse.parse(info_parse, url)
    if res is None:
        return None
    
    res= res.named
    return f"{res['id']}/{res['id2']}", res["branch"], res["filename"]

last_commit_api_url = "https://api.github.com/repos/{id}/commits?path={filename}&limit=1"

def git_last_commit_date(id, filename):
    r = requests.get(last_commit_api_url.format(id=id, filename=filename))
    try:
        rjson = r.json()
    except Exception:
        return None

    datestr = getDeep(rjson, 0, "commit", "committer", "date")

    dateobj = datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")

    return dateobj

baseurl= "https://raw.githubusercontent.com/{url}"

def download_github_raw_content(url : str):
    url = baseurl.format(url=url)
    res = requests.get(url)
    return res.content

_cache = {}
def _retrieve_cache(giturl, filepath):
    global _cache
    if giturl not in _cache:
        with open(filepath, 'r') as f:
            return f.read()
    return _cache[giturl]

def retrieve_file(giturl: str, filepath: str = None):
    global _cache
    
    # Parse the GitHub URL to extract id, branch, and filename
    id_branch_filename = raw_resolve(giturl)
    if id_branch_filename is None:
        raise ValueError("Invalid GitHub URL")

    id, branch, filename = id_branch_filename

    # Check if the file has been pulled in the last day
    last_pull_key = ["filecache", giturl, "lastpull"]
    last_commit_key = ["filecache", giturl, "lastcommit"]
    last_pull = cfg.getDeep(*last_pull_key)
    if last_pull is not ERROR:
        last_pull_date = datetime.datetime.strptime(last_pull, "%Y-%m-%dT%H:%M:%SZ")
        if (datetime.datetime.now() - last_pull_date).days < 1:
            logging.info("File already pulled in the last day")
            return _retrieve_cache(giturl, filepath)

    # Get the date of the last commit
    last_commit_date = git_last_commit_date(id, filename)
    if last_commit_date is None:
        raise ValueError("Could not retrieve the last commit date")

    # Check if the file on GitHub is newer
    stored_last_commit_date = cfg.getDeep(*last_commit_key)
    if stored_last_commit_date is not ERROR:
        stored_last_commit_date = datetime.datetime.strptime(stored_last_commit_date, "%Y-%m-%dT%H:%M:%SZ")
        if stored_last_commit_date >= last_commit_date:
            logging.info("Local file is up to date")
            return _retrieve_cache(giturl, filepath)

    # Download and replace the file content
    content = download_github_raw_content(giturl)
    if filepath is not None:
        with open(filepath, 'wb') as file:
            file.write(content)

    # Update last pull and commit dates in the configuration
    cfg.setDeep(*last_pull_key, datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
    cfg.setDeep(*last_commit_key, last_commit_date.strftime("%Y-%m-%dT%H:%M:%SZ"))
    
    _cache[giturl] = content
    return content

def check_retrieved(giturl: str):
    """
    Check if the given GitHub URL has been retrieved recently.
    Does not perform downloading.

    :param giturl: GitHub URL to check.
    :return: Status message indicating if the file has been retrieved or not.
    """
    # Parse the GitHub URL to extract id, branch, and filename
    id_branch_filename = raw_resolve(giturl)
    if id_branch_filename is None:
        raise ValueError("Invalid GitHub URL")

    id, branch, filename = id_branch_filename

    # Check if the file has been pulled in the last day
    last_pull_key = ["filecache", giturl, "lastpull"]
    last_commit_key = ["filecache", giturl, "lastcommit"]
    last_pull = cfg.getDeep(*last_pull_key)
    if last_pull is not ERROR:
        last_pull_date = datetime.datetime.strptime(last_pull, "%Y-%m-%dT%H:%M:%SZ")
        if (datetime.datetime.now() - last_pull_date).days < 1:
            logging.info("File was pulled in the last day")
            return True

    # Check if the last commit info is available
    stored_last_commit_date = cfg.getDeep(*last_commit_key)
    if stored_last_commit_date is not ERROR:
        logging.info("Last commit information available")
        return True

    return False
