import os
import sys

if __name__=='__main__':
    SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(SRC_ROOT)

import requests
from utils.msg_util import *
from settings.base import GITHUB_LOGIN, GITHUB_PASSWORD, GITHUB_TARGET_USERNAME, GITHUB_TARGET_REPOSITORY
import json



class LabelService:
    
    def __init__(self):
        """The add label to issue seems broken in pygithub3, just use this for now"""
        self.auth = (GITHUB_LOGIN, GITHUB_PASSWORD)


    def clear_labels(self, issue_id):
        msgt('Clear Labels for an Issue.  Issue: [%s]' % (issue_id))
        #DELETE /repos/:owner/:repo/issues/:number/labels
        label_url = 'https://api.github.com/repos/%s/%s/issues/%s/labels' % (GITHUB_TARGET_USERNAME, GITHUB_TARGET_REPOSITORY, issue_id)
        req = requests.delete(label_url, auth=self.auth)
        print 'labels deleted!' 

    def add_labels_to_issue(self, issue_id, labels=[]):
        msg('Add Labels to Issue.  Issue: [%s] Labels: [%s]' % (issue_id, labels))

        if not issue_id or not type(labels) in [list, tuple]:
            return
        
        if len(labels) == 0:
            return
    
        label_url = 'https://api.github.com/repos/%s/%s/issues/%s/labels' % (GITHUB_TARGET_USERNAME, GITHUB_TARGET_REPOSITORY, issue_id)
    
        #labels = json.dumps(['invalid', 'bug', 'enhancement', 'duplicate'])#['Bug', 'invalid'])
        labels_for_call = json.dumps(labels)
        msg('labels: %s' % labels_for_call)
        
        req = requests.post(label_url, auth=self.auth, data=labels_for_call) 

        msg('result: %s' % req.text)
    
    
    def format_component_name(self, component):
        if not type(component) is dict:
            msgx('ERROR. LabelService. format_component_name. component is not a dict')
            
        if component and component.has_key('id') and component.has_key('name'):
            return 'Component: %s' % component['name']
            #git_component_name = '(%s) %s' % (component['id'], component['name'])
    
        return None
        
        
    def format_tracker_name(self, tracker):
        if not type(tracker) is dict:
            msgx('ERROR. LabelService. format_tracker_name. tracker is not a dict')
            
        if tracker and tracker.has_key('id') and tracker.has_key('name'):
            return 'Tracker: %s' % tracker['name']
            #git_tracker_name = '(%s) %s' % (tracker['id'], tracker['name'])
    
        return None
        
    def format_status_name(self, status):
        if not type(status) is dict:
            msgx('ERROR. LabelService. format_status_name. Status is not a dict')
            
        if status and status.has_key('id') and status.has_key('name'):
            return 'Status: %s' % status['name']
            #git_status_name = '(%s) %s' % (status['id'], status['name'])
    
        return None
                