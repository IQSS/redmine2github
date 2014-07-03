from __future__ import print_function
import os
import sys
import json


if __name__=='__main__':
    SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(SRC_ROOT)

from datetime import datetime

from jinja2 import Template
from jinja2 import Environment, PackageLoader

from utils.msg_util import *
from github_issues.md_translate import translate_for_github
from github_issues.milestone_helper import MilestoneHelper
from github_issues.label_helper import LabelHelper


from settings.base import get_github_auth, REDMINE_SERVER

import pygithub3

class GithubIssueMaker:
    """
    Given a Redmine issue in JSON format, create a GitHub issue.
    These issues should be moved from Redmine in order of issue.id.  This will allow mapping of Redmine issue ID's against newly created Github issued IDs.  e.g., can translate related issues numbers, etc.
    """
    
    def __init__(self):        
        self.github_conn = None
        self.comments_service = None
        self.milestone_manager = MilestoneHelper()
        self.label_helper = LabelHelper()
        self.jinja_env = Environment(loader=PackageLoader('github_issues', 'templates'))

    def get_comments_service(self):
        if self.comments_service is None:
            #auth = dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD, repo=GITHUB_TARGET_REPOSITORY, user=GITHUB_TARGET_USERNAME)
            self.comments_service = pygithub3.services.issues.Comments(**get_github_auth())
            #labels_service = pygithub3.services.issues.Labels(**auth)
            # #labels_service = pygithub3.services.issues.Labels(**auth)
            #pygithub3.services.issues.Comments(**config)
            
        return self.comments_service
        
    def get_github_conn(self):
        
        if self.github_conn is None:
            self.github_conn = pygithub3.Github(**get_github_auth())
        return self.github_conn
    
        
    def make_github_issue(self, redmine_json_fname, redmine2github_id_map={}):
        """
        Create a GitHub issue from JSON for a Redmine issue.
        
        - Format the GitHub description to include original redmine info: author, link back to redmine ticket, etc
        - Add/Create Labels
        - Add/Create Milestones
        """
        if not os.path.isfile(redmine_json_fname):
            msgx('ERROR.  make_github_issue. file not found: %s' % redmine_json_fname)
            
        json_str = open(redmine_json_fname, 'r').read()
        rd = json.loads(json_str)       # The redmine issue as a python dict

        #msg(json.dumps(rd, indent=4))
        msg('Attempt to create issue: [#%s][%s]' % (rd.get('id'), rd.get('subject') ))
        
        # (1) Format the github issue description 
        #
        #
        template = self.jinja_env.get_template('description.md')
        desc_dict = {'description' : translate_for_github(rd.get('description', 'no description'))\
                    , 'redmine_link' : os.path.join(REDMINE_SERVER, 'issues', '%d' % rd.get('id'))\
                    , 'start_date' : rd.get('start_date', None)\
                    , 'author_name' : rd.get('author', {}).get('name', None)\
                    
        }
        
        description_info = template.render(desc_dict)
        
        #
        # (2) Create the dictionary for the GitHub issue--for the github API
        #
        #self.label_helper.clear_labels(151)
        github_issue_dict = { 'title': rd.get('subject')\
                    , 'body' : description_info\
                    , 'labels' : self.label_helper.get_label_names(rd)
                    }
                    
        milestone_number = self.milestone_manager.get_create_milestone(rd)
        if milestone_number:
            github_issue_dict['milestone'] = milestone_number

        msg( github_issue_dict['labels'])
        
        #
        # (3) Create the issue on github
        #
        issue_obj = self.get_github_conn().issues.create(github_issue_dict)
        #issue_obj = self.get_github_conn().issues.update(151, github_issue_dict)
        
        msgt('issue number: %s' % issue_obj.number)
        msg('issue id: %s' % issue_obj.id)
        
        # Map the new github Issue number to the redmine issue number
        #
        redmine2github_id_map.update({ rd.get('id', 'unknown') : issue_obj.number })

        print( redmine2github_id_map)
        
        #
        # (4) Add the redmine comments (journals) as github comments
        #
        journals = rd.get('journals', None)
        if journals:
            self.add_comments_for_issue(issue_obj.number, journals)



    def xget_create_milestone(self, redmine_issue_dict):
        # Add milestones!
        #
        # "fixed_version": {
        #    "id": 96, 
        #    "name": "4.0 - review for weekly assignment"
        # },
        #
        if not type(redmine_issue_dict) is dict:
            return None
            
        fixed_version = rd.get('fixed_version', {})
        if not fixed_version.has_key('name'):
            return None
        
            
        mstone_name = fixed_version['name']
        if mstone_name: 
            milestone_number = self.get_create_milestone_number(mstone_name)
            if not milestone_number:
                msgx('Milestone number not found for: [%s]' % mstone_name)

            return milestone_number
    
        return None

        # Add milestone to issue
        #        mstone_dict =  { 'milestone' : milestone_number}
        #        print(mstone_dict)
        #    issue_obj = self.get_github_conn().issues.update(issue_obj.number, mstone_dict)



    def add_comments_for_issue(self, issue_num, journals):
        """
        Add comments
        """
        if journals is None:
            msg('no journals')
            return
        
        comment_template = self.jinja_env.get_template('comment.md')
        
        for j in journals:
            notes = j.get('notes', None)
            if not notes:
                continue
            note_dict = { 'description' : translate_for_github(notes)\
                         , 'note_date' : j.get('created_on', None)\
                         , 'author_name' : j.get('user', {}).get('name', None)\
                         }
            comment_info =  comment_template.render(note_dict)
            comment_obj = self.get_comments_service().create(issue_num, comment_info)
            msg('comment created')

            msgt('id: %s' % comment_obj.id)
            msg('issue_url: %s' % comment_obj.issue_url)
            msg('html_url: %s' % comment_obj.html_url)
            msg('url: %s' % comment_obj.url)
            #msg(dir(comment_obj))


if __name__=='__main__':
    #auth = dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD, repo=GITHUB_TARGET_REPOSITORY, user=GITHUB_TARGET_USERNAME)
    #milestone_service = pygithub3.services.issues.Milestones(**auth)
    #comments_service = pygithub3.services.issues.Comments(**auth)
    #fname = 03385.json'
    #gm.make_github_issue(fname, {})

    import time
    
    issue_filename = '/Users/rmp553/Documents/iqss-git/redmine2github/working_files/redmine_issues/2014-0702/04156.json'
    gm = GithubIssueMaker()
    gm.make_github_issue(issue_filename, {})
    
    sys.exit(0)
    root_dir = '/Users/rmp553/Documents/iqss-git/redmine2github/working_files/redmine_issues/2014-0702/'
    
    cnt =0
    for fname in os.listdir(root_dir):
        if fname.endswith('.json'):
            
            num = int(fname.replace('.json', ''))
            if num < 3902: continue
            msg('Add issue from: %s' % fname)
            cnt+=1
            fullname = os.path.join(root_dir, fname)
            gm.make_github_issue(fullname, {})
            if cnt == 150:
                break
                
            if cnt%50 == 0:
                msg('sleep 2 secs')
                time.sleep(2)
        
            #sys.exit(0)
        
        
        
        
        
        