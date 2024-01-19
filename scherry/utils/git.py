from datetime import datetime
import requests

from scherry.utils.dictionary import ERROR, getDeep


_git_filename_cache = {}

def git_filename(url :str):
    global _git_filename_cache
    if url in _git_filename_cache:
        return _git_filename_cache[url]
    
    _git_filename_cache[url] = url.split("/")[-1]
    
    return _git_filename_cache[url]

def _set_git_filename(url :str, filename :str):
    global _git_filename_cache
    _git_filename_cache[url] = filename


git_filename.set = _set_git_filename

baseurl= "https://raw.githubusercontent.com/{url}"

def download_github_raw_content(url : str):
    url = baseurl.format(url=url)
    res = requests.get(url)
    # if 404
    if res.status_code == 404:
        raise RuntimeError("File not found on github")
    
    return res.content

last_commit_api_url = "https://api.github.com/repos/{id}/commits?path={filename}&limit=1"

def git_last_commit_date(id, filename):
    r = requests.get(last_commit_api_url.format(id=id, filename=filename))
    try:
        rjson = r.json()
    except Exception:
        return None

    datestr = getDeep(rjson, 0, "commit", "committer", "date")
    if datestr is ERROR:
        return None
    
    dateobj = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")

    return dateobj