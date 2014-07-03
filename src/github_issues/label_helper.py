import os
import sys

if __name__=='__main__':
    SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(SRC_ROOT)

import requests
from utils.msg_util import *
from settings.base import GITHUB_LOGIN, GITHUB_PASSWORD, GITHUB_TARGET_USERNAME, GITHUB_TARGET_REPOSITORY
import json



class LabelHelper:
    
    def __init__(self):
        """The add label to issue seems broken in pygithub3, just use this for now"""
        self.auth = (GITHUB_LOGIN, GITHUB_PASSWORD)


    def clear_labels(self, issue_id):
        msgt('Clear Labels for an Issue.  Issue: [%s]' % (issue_id))
        #DELETE /repos/:owner/:repo/issues/:number/labels
        label_url = 'https://api.github.com/repos/%s/%s/issues/%s/labels' % (GITHUB_TARGET_USERNAME, GITHUB_TARGET_REPOSITORY, issue_id)
        req = requests.delete(label_url, auth=self.auth)
        msg('labels deleted!') 
        
        

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
    
    
    
    def get_label_from_id_name(self, label_info_dict, key_name=None, label_prefix=''):
        """
        Expects a dict in one of 2 formats (where key_name is "status"):
            Format 1:
            "status": { "id": 1, "name": "New"  },
        
            Format 2:
            { "id":3, "name":"UX/UI Component"}
            
        """
        if not type(label_info_dict) is dict:
            return None
        
        # For Format 1 above
        if key_name is not None:
            label_info_dict = label_info_dict.get(key_name, None)
            if label_info_dict is None:
                return None
        
        if label_info_dict.has_key('id') and label_info_dict.has_key('name'):
            if label_prefix:
                return '%s %s' % (label_prefix, label_info_dict['name'])
            return label_info_dict['name']
        
        return None
        
    
    def get_label_names(self, redmine_issue_dict):
        """
        Read a redmine issue and a make a list of formatted label names for
         - status
         - tracker
         - component
         
        If the labels don't yet exist in GitHub, create them 
        """
        if not type(redmine_issue_dict) is dict:
            return []
            
        label_names = []
        
        # Add status
        status_label_name = self.get_label_from_id_name(redmine_issue_dict, 'status', 'Status:')
        if status_label_name:
            label_names.append(status_label_name)

        # Add tracker
        tracker_label_name = self.get_label_from_id_name(redmine_issue_dict, 'tracker', 'Tracker:')
        if tracker_label_name:
            label_names.append(tracker_label_name)

        # Add priority
        priority_label_name = self.get_label_from_id_name(redmine_issue_dict, 'priority', 'Priority:')
        if priority_label_name:
            label_names.append(priority_label_name)

        # Add component
        #   "custom_fields": [
        #        {
        #            "id": 1, 
        #            "value": "0", 
        #            "name": "Usability Testing"
        #        }
        #    ],        
        #
        custom_fields = redmine_issue_dict.get('custom_fields', None)
        if custom_fields and len(custom_fields) > 0:
            for cf_dict in custom_fields:
                component_label_name = self.get_label_from_id_name(cf_dict, None, 'Component:')
                if component_label_name:
                    label_names.append(component_label_name)

        return label_names
            
"""
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
    