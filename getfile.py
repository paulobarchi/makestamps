import requests
import shutil
from requests.auth import HTTPBasicAuth

prefix = "https://desar2.cosmology.illinois.edu/DESFiles/desarchive/"

def getCred():
    with open("cred") as f:
        lines = f.readlines()
        return lines[0].strip(), lines[1].strip()

def download_file(url):
    user, password = getCred()
    url = prefix + url
    # print(url)
    # exit()
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True, auth=HTTPBasicAuth(user, password))
    with open(local_filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

    return local_filename

if __name__ == "__main__":
    import sys
    fileurl = sys.argv[1]
    if fileurl.startswith(prefix):
        fileurl = fileurl[len(prefix):]
    else:
        pass
    download_file(fileurl)
