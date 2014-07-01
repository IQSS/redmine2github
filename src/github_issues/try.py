import requests
from settings.base import GITHUB_LOGIN, GITHUB_PASSWORD
import json
from requests import Request, Session

auth = (GITHUB_LOGIN, GITHUB_PASSWORD)

repo_str = 'test-issue-migrate'
user_str = 'user'

url = 'https://api.github.com/repos/%s/%s/issues/1/labels' % (user_str, repo_str)
labels = json.dumps(['invalid', 'bug', 'enhancement', 'duplicate'])#['Bug', 'invalid'])
print 'labels', labels
req = requests.post(url, auth=auth, data=labels) #'POST', url, ['invalid'])
req.text

#-------------------------------

labels = json.dumps([])#['Bug', 'invalid'])
print 'labels', labels
req = requests.put(url, auth=auth, data=labels) #'POST', url, ['invalid'])
req.text


