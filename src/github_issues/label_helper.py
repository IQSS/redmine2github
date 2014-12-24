import os
import sys

if __name__=='__main__':
    SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(SRC_ROOT)

import requests
from utils.msg_util import *
from settings.base import GITHUB_LOGIN, GITHUB_PASSWORD_OR_PERSONAL_ACCESS_TOKEN, GITHUB_TARGET_USERNAME, GITHUB_TARGET_REPOSITORY
import json
from github_issues.label_map import LabelMap


class LabelHelper:
    
    def __init__(self, label_map_filename=None):
        """The add label to issue seems broken in pygithub3, just use this for now"""
        self.auth = (GITHUB_LOGIN, GITHUB_PASSWORD_OR_PERSONAL_ACCESS_TOKEN)
        
        self.label_map_filename = label_map_filename
        self.label_map = None
        self.using_label_map = False
        self.load_map()
        
    def load_map(self):
        """
        If a label_map_filename is specified, load it up!
        """
        if self.label_map_filename is None:
            self.using_label_map = False    # a bit redundant
            return
        
        self.label_map = LabelMap(self.label_map_filename)
        self.using_label_map = True
        
        self.make_update_map_labels()
        
        
    def make_update_map_labels(self):
        """
        Go through the label make and make sure they all exist, with the appropriate colors
        """ 
        msgt('Match label map names/color to GitHub')   
        
        for label_info in self.label_map.get_label_info_objects():
            
            msg('\nCheck label: %s %s' % (label_info.github_label_name, label_info.github_label_color))

            #  (1) try to get label
            #
            msg('  (1) Try to retrieve label')            
            label_url = 'https://api.github.com/repos/%s/%s/labels/%s' % (GITHUB_TARGET_USERNAME, GITHUB_TARGET_REPOSITORY, label_info.github_label_name)
            req = requests.get(label_url, auth=self.auth)
            msg('url: %s' % label_url)
            msg('status: %s' % req.status_code)
            
            #  (2) Label exists
            if req.status_code == 200:
                github_label_info = req.json()
                msg('-- label exists\n %s' % github_label_info)
                #print label_info
                
                # (2a) Color matches! -- all done
                if github_label_info.get('color', 'nope') == label_info.github_label_color:
                    msg('-- color matches!')
                    continue
                  
                # (2b) Color doesn't match -- update color
                msg('  (2b) Try to update label color')
                label_url = 'https://api.github.com/repos/%s/%s/labels/%s' % (GITHUB_TARGET_USERNAME, GITHUB_TARGET_REPOSITORY, label_info.github_label_name)
                data = dict(name=label_info.github_label_name\
                            , color=label_info.github_label_color)
                req = requests.patch(label_url, data=json.dumps(data), auth=self.auth)
                if req.status_code == 200:
                    msg('  Color updated!')
                    msg(req.text)
                    continue
                msgx('Color updated failed!')
            
            # (3) Create new label with color
            msg('  (3) Try to create label')
            label_url = 'https://api.github.com/repos/%s/%s/labels' % (GITHUB_TARGET_USERNAME, GITHUB_TARGET_REPOSITORY)
            data = dict(name=label_info.github_label_name\
                        , color=label_info.github_label_color)
            req = requests.post(label_url, data=json.dumps(data), auth=self.auth)
            msg(req.text)
            msg(req.status_code)
            if req.status_code in [ 200, 201]:
                msg('Label created with color!')
                continue
            else:
                msgx('Create label with color failed!')
        
        
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
    
    
    
    def get_label_from_id_name(self, label_info_dict, key_name=None, label_prefix='', non_formatted=False):
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
            if non_formatted:
                return label_info_dict['name']
                
            if label_prefix:
                return '%s %s' % (label_prefix, label_info_dict['name'])

            return label_info_dict['name']
        
        return None
        
    
    def get_label_names_based_on_map(self, redmine_issue_dict):
        """
        We're using the label map, so before using a label, create it with the appropriate color.
        
        If the label doesn't appear in the map, then discard it
        """
        label_names = self.get_label_names(redmine_issue_dict, non_formatted=True)
        
        if len(label_names) == 0:
            return []
        
        mapped_label_names = []

        for name in label_names:
            github_label_name = self.label_map.get_github_label_from_redmine_name(name)
            print 'name', name, 'github_label_name: ', github_label_name
            if github_label_name:
                mapped_label_names.append(github_label_name)
        #msgx('blah')
        return mapped_label_names
            
    def get_label_names_from_issue(self, redmine_issue_dict):
        if self.using_label_map is True:
            return self.get_label_names_based_on_map(redmine_issue_dict)
        
        return self.get_label_names(redmine_issue_dict)
    
    
    def get_label_names(self, redmine_issue_dict, non_formatted=False):
        """
        Read a redmine issue and a make a list of formatted label names for
         - status
         - tracker
         - priority
         - component
         - category
        :returns: list with formatted label names
        """
        if not type(redmine_issue_dict) is dict:
            return []
            
        label_names = []
        
        # Add status
        status_label_name = self.get_label_from_id_name(redmine_issue_dict, 'status', 'Status:', non_formatted)
        if status_label_name:
            label_names.append(status_label_name)

        # Add tracker
        tracker_label_name = self.get_label_from_id_name(redmine_issue_dict, 'tracker', 'Tracker:', non_formatted)
        if tracker_label_name:
            label_names.append(tracker_label_name)

        # Add priority
        priority_label_name = self.get_label_from_id_name(redmine_issue_dict, 'priority', 'Priority:', non_formatted)
        if priority_label_name:
            label_names.append(priority_label_name)

        # Add category
        category_label_name = self.get_label_from_id_name(redmine_issue_dict, 'category', 'Category:', non_formatted)
        if category_label_name:
            label_names.append(category_label_name)

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
                component_label_name = self.get_label_from_id_name(cf_dict, None, 'Component:', non_formatted)
                if component_label_name:
                    label_names.append(component_label_name)

        return label_names
        
if __name__=='__main__':
    from settings.base import LABEL_MAP_FILE
    LabelHelper(LABEL_MAP_FILE)     # load a new label color map
    
            
"""
#labels_service = pygithub3.services.issues.Labels(**auth)
#auth = dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD_OR_PERSONAL_ACCESS_TOKEN)

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
    