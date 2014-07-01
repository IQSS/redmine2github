#from __future__ import print_function
from os.path import dirname, join, abspath
import sys

if __name__=='__main__':
    SRC_ROOT = dirname(dirname(abspath(__file__)))
    sys.path.append(SRC_ROOT)

from settings.base import GITHUB_LOGIN, GITHUB_PASSWORD
import pygithub3

#from pygithub3 import Github


#from pygithub import Github
USER = 'USER'
REPO = 'test-issue-migrate'

auth = dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD, repo=REPO, user=USER)
gc = pygithub3.Github(**auth)

print gc.users.get()

for item in gc.issues.list():
    print item

#labels_service = pygithub3.services.issues.Labels(**auth)
#auth = dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD)

#pygithub3.services.issues.Labels

# works!
label_info = dict(name='Week of World Cup', color="006699")
#issues_service.create(label_info)#, user=USER, repo=REPO)

#existing_label = labels_service.get('Bug')
#label_names = ['Bug', ]
labels = json.dumps(['invalid', 'bug', 'enhancement', 'duplicate'])#['Bug', 'invalid'])

labels_service.add_to_issue(1, labels=labels)
#*label_names)
#labels_service.add_to_issue(1, labels=[('label1', 'ffcc00')], user=USER, repo=REPO)

"""
import json, requests
url = 'https://api.github.com/some/endpoint'
>>> data = {'some': 'data'}

>>> r = requests.post(url, data=json.dumps(payload))

"""

#issues_service.add_to_issue(1, user=USER, repo=REPO, labels=['Beta 4.0',])

    
"""
gc.issues.create({'title': 'My test issue'\
                , 'body' :'This needs to be fixed ASAP.'\
                } )#,\
"""                
#for d in dir(gc): print d
#gc.labels_service.add_to_issue(1, 'label1', user=USER, repo=REPO,)
#                assignee='username'))    
    
#for repo in github_conn.get_user().get_repos():
#    print repo.name
#    repo.edit(has_wiki=False)
'''

print github_conn.issues.create(dict(title='My test issue',\
                                body='This needs to be fixed ASAP.',\
                                assignee='username'))

sys.exit(0)
#print gh.repos.list().all()
#issues = gh.issues.list_by_repo('iqss', 'miniverse')
issues = github_conn.issues.list_by_repo('iqss', 'geoconnect')

    
print issues
print dir(issues)
attrs = """title state number milestone""".split()
for item in issues.next():
    print '-' * 40
    for attr in attrs:
        print 'key:[%s] val:[%s]' % (attr, item.__dict__.get(attr, 'not found'))
        

        issues_service.create(dict(title='My test issue',
            body='This needs to be fixed ASAP.',
            assignee='copitux'))

print dir(item.milestone)
'''
#print(octocat_issues)
#octocat_repo_issues = gh.issues.list_by_repo('octocat', 'Hello-World')


