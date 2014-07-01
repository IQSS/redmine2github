#from __future__ import print_function
from os.path import dirname, join, abspath
import sys
import json

# http://python-redmine.readthedocs.org/
from redmine import Redmine

if __name__=='__main__':
    SRC_ROOT = dirname(dirname(abspath(__file__)))
    sys.path.append(SRC_ROOT)

from settings.base import REDMINE_SERVER, REDMINE_API_KEY

class RedmineNavigator:
    
    def __init__(self, redmine_server, redmine_api_key, project_name_or_id):
        self.redmine_server = redmine_server
        self.redmine_api_key = redmine_api_key
        self.project_name_or_id = project_name_or_id

        self.redmine_conn = None
        self.redmine_project = None
        
        self.connect_to_redmine()
        
    def connect_to_redmine(self):
        self.redmine_conn = Redmine(self.redmine_server, key=self.redmine_api_key)
        self.redmine_project = self.redmine_conn.project.get(self.project_name_or_id)
        
if __name__=='__main__':
    rn = RedmineNavigator(REDMINE_SERVER, REDMINE_API_KEY, )

project = r.project.get(1)
print project

for key in dir(project):
    print key
print '-' * 40


attr_keys = {}

#issue = redmine.issue.get(34441, include='children,journals,watchers')

item = r.issue.get(4048, include='children,journals,watchers,relations')
print '-' * 40
print json.dumps(item._attributes, indent=4)
for rel in item.relations:
    print '-' * 40
    #print dir(item.relations)
    print json.dumps(rel._attributes, indent=4)
print '-' * 40

sys.exit(0)
for item in project.issues:
    if not item.id == 4048: continue
    
    print json.dumps(item._attributes, indent=4)
    for rel in item.relations:
        #print dir(item.relations)
        print json.dumps(rel._attributes, indent=4)
    break
    continue

    print item._attributes
    print 'title', item
    print 'id', item.id
    
    print 'status', item.status
    print 'status_id', item.status.id
    print '-' * 40
#key

#print project.id

"""
https://redmine.hmdc.harvard.edu/issues.json?project_id=1&key=blah
https://redmine.hmdc.harvard.edu/projects/1.xml
https://redmine.hmdc.harvard.edu/issues.xml?project_id=1&tracker_id

https://redmine.hmdc.harvard.edu/issues/4602.json&include=relations
?project_id=1&tracker_id

"""
