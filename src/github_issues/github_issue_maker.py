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
import csv

from settings.base import get_github_auth, REDMINE_SERVER

import pygithub3

class GithubIssueMaker:
    """
    Given a Redmine issue in JSON format, create a GitHub issue.
    These issues should be moved from Redmine in order of issue.id.  This will allow mapping of Redmine issue ID's against newly created Github issued IDs.  e.g., can translate related issues numbers, etc.
    """
    ISSUE_STATE_CLOSED = 'closed'
    
    def __init__(self, user_map_helper=None, label_mapping_filename=None, milestone_mapping_filename=None):        
        self.github_conn = None
        self.comments_service = None
        self.milestone_manager = MilestoneHelper(milestone_mapping_filename)
        self.label_helper = LabelHelper(label_mapping_filename)
        self.jinja_env = Environment(loader=PackageLoader('github_issues', 'templates'))
        self.user_map_helper = user_map_helper
        
    def get_comments_service(self):
        if self.comments_service is None:
            self.comments_service = pygithub3.services.issues.Comments(**get_github_auth())
           
        return self.comments_service

        
    def get_github_conn(self):
        
        if self.github_conn is None:
            self.github_conn = pygithub3.Github(**get_github_auth())
        return self.github_conn
    
    def format_name_for_github(self, author_name, include_at_sign=True):
        """
        (1) Try the user map
        (2) If no match, return the name
        """
        if not author_name:
            return None
            
        if self.user_map_helper:
            github_name = self.user_map_helper.get_github_user(author_name, include_at_sign)
            if github_name is not None:
                return github_name
        return author_name
        
    
    def get_redmine_assignee_name(self, redmine_issue_dict):
        """
        If a redmine user has a github account mapped, add the person as the assignee
        
        "assigned_to": {
            "id": 4, 
            "name": "Philip Durbin"
        },
        /cc @kneath @jresig
        """
        if not type(redmine_issue_dict) is dict:
            return None
    
        redmine_name = redmine_issue_dict.get('assigned_to', {}).get('name', None)
        if redmine_name is None:
            return None
        
        return redmine_name

        
    def get_assignee(self, redmine_issue_dict):
        """
        If a redmine user has a github account mapped, add the person as the assignee
        
        "assigned_to": {
            "id": 4, 
            "name": "Philip Durbin"
        },
        /cc @kneath @jresig
        """
        if not type(redmine_issue_dict) is dict:
            return None
    
        redmine_name = redmine_issue_dict.get('assigned_to', {}).get('name', None)
        if redmine_name is None:
            return None
        
        github_username = self.format_name_for_github(redmine_name, include_at_sign=False)
        
        return github_username
    
    
    def update_github_issue_with_related(self, redmine_json_fname, redmine2github_issue_map):
        """
        Update a GitHub issue with related tickets as specfied in Redmine
        
        - Read the current github description
        - Add related notes to the bottom of description
        - Update the description
        
        "relations": [
              {
                  "delay": null, 
                  "issue_to_id": 4160, 
                  "issue_id": 4062, 
                  "id": 438, 
                  "relation_type": "relates"
              }, 
              {
                  "delay": null, 
                  "issue_to_id": 3643, 
                  "issue_id": 4160, 
                  "id": 439, 
                  "relation_type": "relates"
              }
          ], 
          "id": 4160,
        """
        if not os.path.isfile(redmine_json_fname):
            msgx('ERROR.  update_github_issue_with_related. file not found: %s' % redmine_json_fname)
        
        json_str = open(redmine_json_fname, 'r').read()
        rd = json.loads(json_str)       # The redmine issue as a python dict
        
        if rd.get('relations', None) is None:
            msg('no relations')
            return
            
        redmine_issue_num = rd.get('id', None)
        if redmine_issue_num is None:
            return
            
        github_issue_num = redmine2github_issue_map.get(str(redmine_issue_num), None)
        if github_issue_num is None:
            msg('Redmine issue not in nap')
            return


        # Related tickets under 'relations'
        #
        github_related_tickets = []
        original_related_tickets = []
        for rel in rd.get('relations'):
            issue_to_id = rel.get('issue_to_id', None)
            if issue_to_id is None:
                continue
            if rd.get('id') == issue_to_id:  # skip relations pointing to this ticket
                continue
            
            original_related_tickets.append(issue_to_id)
            related_github_issue_num = redmine2github_issue_map.get(str(issue_to_id), None)
            msg(related_github_issue_num)
            if related_github_issue_num:
                github_related_tickets.append(related_github_issue_num)
        github_related_tickets.sort()
        original_related_tickets.sort()
        #
        # end: Related tickets under 'relations'
        
        
        # Related tickets under 'children'
        #
        # "children": [{ "tracker": {"id": 2, "name": "Feature"    }, "id": 3454, "subject": "Icons in results and facet"    }, ...]
        #
        github_child_tickets = []
        original_child_tickets = []
        
        child_ticket_info = rd.get('children', [])
        if child_ticket_info:
            for ctick in child_ticket_info:
            
                child_id = ctick.get('id', None)
                if child_id is None:
                    continue
                
                original_child_tickets.append(child_id)
                child_github_issue_num = redmine2github_issue_map.get(str(child_id), None)
            
                msg(child_github_issue_num)
                if child_github_issue_num:
                    github_child_tickets.append(child_github_issue_num)
            original_child_tickets.sort()
            github_child_tickets.sort()
        #
        # end: Related tickets under 'children'


        #
        # Update github issue with related and child tickets
        #
        #
        if len(original_related_tickets) == 0 and len(original_child_tickets)==0:
            return
        
        # Format related ticket numbers
        #
        original_issues_formatted = [ """[%s](%s)""" % (x, self.format_redmine_issue_link(x)) for x in original_related_tickets]
        original_issues_str = ', '.join(original_issues_formatted)
        
        related_issues_formatted = [ '#%d' % x for x in github_related_tickets]
        related_issue_str = ', '.join(related_issues_formatted)
        msg('Redmine related issues: %s' % original_issues_str)
        msg('Github related issues: %s' % related_issue_str)
        
        
        # Format children ticket numbers
        #
        original_children_formatted = [ """[%s](%s)""" % (x, self.format_redmine_issue_link(x)) for x in original_child_tickets]
        original_children_str = ', '.join(original_children_formatted)

        github_children_formatted = [ '#%d' % x for x in github_child_tickets]
        github_children_str = ', '.join(github_children_formatted)
        msg('Redmine sub-issues: %s' % original_children_str)
        msg('Github sub-issues: %s' % github_children_str)
        
        try:
            issue = self.get_github_conn().issues.get(number=github_issue_num)
        except pygithub3.exceptions.NotFound:
            msg('Issue not found!')
            return
            
        template = self.jinja_env.get_template('related_issues.md')
            
        template_params = { 'original_description' : issue.body\
                            , 'original_issues' : original_issues_str\
                            , 'related_issues' : related_issue_str\
                            , 'child_issues_original' : original_children_str\
                            , 'child_issues_github' : github_children_str\
                            
                            }

        updated_description = template.render(template_params)

        issue = self.get_github_conn().issues.update(number=github_issue_num, data={'body':updated_description})
        
        msg('Issue updated!')#' % issue.body)
        
        
    def format_redmine_issue_link(self, issue_id):
        if issue_id is None:
            return None
            
        return os.path.join(REDMINE_SERVER, 'issues', '%d' % issue_id) 
        
    
    def close_github_issue(self, github_issue_num):
    
        if not github_issue_num:
            return False
        msgt('Close issue: %s' % github_issue_num)
        
        try:
             issue = self.get_github_conn().issues.get(number=github_issue_num)
        except pygithub3.exceptions.NotFound:
             msg('Issue not found!')
             return False
        
        if issue.state == self.ISSUE_STATE_CLOSED:
            msg('Already closed')
            return True
            
        updated_issue = self.get_github_conn().issues.update(number=github_issue_num, data={'state': self.ISSUE_STATE_CLOSED })
        if not updated_issue:
            msg('Failed to close issue')
            return False
        
        if updated_issue.state == self.ISSUE_STATE_CLOSED:
            msg('Issue closed')
            return True
            
        msg('Failed to close issue')
        return False
        
    
    
    def make_github_issue(self, redmine_json_fname, **kwargs):
        """
        Create a GitHub issue from JSON for a Redmine issue.
        
        - Format the GitHub description to include original redmine info: author, link back to redmine ticket, etc
        - Add/Create Labels
        - Add/Create Milestones
        """
        if not os.path.isfile(redmine_json_fname):
            msgx('ERROR.  make_github_issue. file not found: %s' % redmine_json_fname)
        
        include_comments = kwargs.get('include_comments', True)
        include_assignee = kwargs.get('include_assignee', True)
        
        json_str = open(redmine_json_fname, 'r').read()
        rd = json.loads(json_str)       # The redmine issue as a python dict

        #msg(json.dumps(rd, indent=4))
        msg('Attempt to create issue: [#%s][%s]' % (rd.get('id'), rd.get('subject') ))
        
        # (1) Format the github issue description 
        #
        #
        template = self.jinja_env.get_template('description.md')
        
        author_name = rd.get('author', {}).get('name', None)
        author_github_username = self.format_name_for_github(author_name)
        
        desc_dict = {'description' : translate_for_github(rd.get('description', 'no description'))\
                    , 'redmine_link' : self.format_redmine_issue_link(rd.get('id'))\
                    , 'redmine_issue_num' : rd.get('id')\
                    , 'start_date' : rd.get('start_date', None)\
                    , 'author_name' : author_name\
                    , 'author_github_username' : author_github_username\
                    , 'redmine_assignee' : self.get_redmine_assignee_name(rd)
        }
        
        description_info = template.render(desc_dict)
        
        #
        # (2) Create the dictionary for the GitHub issue--for the github API
        #
        #self.label_helper.clear_labels(151)
        github_issue_dict = { 'title': rd.get('subject')\
                    , 'body' : description_info\
                    , 'labels' : self.label_helper.get_label_names_from_issue(rd)
                    }
                    
        milestone_number = self.milestone_manager.get_create_milestone(rd)
        if milestone_number:
            github_issue_dict['milestone'] = milestone_number

        if include_assignee:
            assignee = self.get_assignee(rd)
            if assignee:
                github_issue_dict['assignee'] = assignee
            
        msg( github_issue_dict)
        
        #
        # (3) Create the issue on github
        #
        issue_obj = self.get_github_conn().issues.create(github_issue_dict)
        #issue_obj = self.get_github_conn().issues.update(151, github_issue_dict)
        
        msgt('Github issue created: %s' % issue_obj.number)
        msg('issue id: %s' % issue_obj.id)
        msg('issue url: %s' % issue_obj.html_url)
        
        
        # Map the new github Issue number to the redmine issue number
        #
        #redmine2github_id_map.update({ rd.get('id', 'unknown') : issue_obj.number })

        #print( redmine2github_id_map)
        
        #
        # (4) Add the redmine comments (journals) as github comments
        #
        if include_comments:
            journals = rd.get('journals', None)
            if journals:
                self.add_comments_for_issue(issue_obj.number, journals)


        #
        #   (5) Should this issue be closed?
        #
        if self.is_redmine_issue_closed(rd):
            self.close_github_issue(issue_obj.number)

        return issue_obj.number


    def is_redmine_issue_closed(self, redmine_issue_dict):
        """
        "status": {
            "id": 5, 
            "name": "Completed"
        },
        """
        if not type(redmine_issue_dict) == dict:
            return False
            
        status_info = redmine_issue_dict.get('status', None)
        if not status_info:
            return False
            
        if status_info.has_key('id') and status_info.get('id', None) == 5:
            return True
        
        return False
            
            
            
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
                
            author_name = j.get('user', {}).get('name', None)
            author_github_username = self.format_name_for_github(author_name)
            
            note_dict = { 'description' : translate_for_github(notes)\
                         , 'note_date' : j.get('created_on', None)\
                         , 'author_name' : author_name\
                         , 'author_github_username' : author_github_username\
                         }
            comment_info =  comment_template.render(note_dict)
            comment_obj = self.get_comments_service().create(issue_num, comment_info)
            dashes()
            msg('comment created')

            msg('comment id: %s' % comment_obj.id)
            msg('api issue_url: %s' % comment_obj.issue_url)
            msg('api comment url: %s' % comment_obj.url)
            msg('html_url: %s' % comment_obj.html_url)
            #msg(dir(comment_obj))


if __name__=='__main__':
    #auth = dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD_OR_PERSONAL_ACCESS_TOKEN, repo=GITHUB_TARGET_REPOSITORY, user=GITHUB_TARGET_USERNAME)
    #milestone_service = pygithub3.services.issues.Milestones(**auth)
    #comments_service = pygithub3.services.issues.Comments(**auth)
    #fname = 03385.json'
    #gm.make_github_issue(fname, {})

    import time
    
    issue_filename = '/Users/rmp553/Documents/iqss-git/redmine2github/working_files/redmine_issues/2014-0702/04156.json'
    gm = GithubIssueMaker()
    for x in range(100, 170):
        gm.close_github_issue(x)
    #gm.make_github_issue(issue_filename, {})
    
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
        
        
        
        
        
        