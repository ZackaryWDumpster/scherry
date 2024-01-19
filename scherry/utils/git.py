import requests

baseurl= "https://raw.githubusercontent.com/{url}"

def download_github_raw_content(url : str):
    url = baseurl.format(url=url)
    res = requests.get(url)
    return res.content