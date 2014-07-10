from __future__ import print_function
import os
from os.path import dirname, join, abspath, isdir
import sys
import json
import urllib2

try:
    from urlparse import urljoin
except:
    from urllib.parse import urljoin        # python 3.x
    
# http://python-redmine.readthedocs.org/
from redmine import Redmine

if __name__=='__main__':
    SRC_ROOT = dirname(dirname(abspath(__file__)))
    sys.path.append(SRC_ROOT)


from jinja2 import Template
from jinja2 import Environment, PackageLoader

from utils.msg_util import *
from settings.base import GITHUB_TARGET_REPOSITORY, GITHUB_TARGET_USERNAME, get_gethub_issue_url
from redmine_ticket.redmine_issue_downloader import RedmineIssueDownloader

class RedmineIssueUpdater:
    """
    For a Redmine project moved to github, update the redmine ticket with the github link
    """
    
    #TIME_FORMAT_STRING = '%Y-%m%d-%H%M'
    TIME_FORMAT_STRING = '%Y-%m%d'

    # Redmine tickets are written to JSON files with the naming convention  "(issue id).json"
    # For file sorting, preceding zeros are tacked on.  
    #   Example: If  ZERO_PADDING_LEVEL=5:
    #               issue #375 is written to file "00375.json"
    #               issue #1789 is written to file "01789.json"
    #               issue #2 is written to file "00002.json"
    #
    # If your issue numbers go beyond 99,999 then increase the ZERO_PADDING_LEVEL
    #    
    def __init__(self, redmine_server, redmine_api_key, project_name_or_identifier, issues_dirname, redmine2github_id_map_filename):
        """
        Constructor
        
        :param redmine_server: str giving the url of the redmine server.  e.g. https://redmine.myorg.edu/
        :param redmine_api_key: str with a redmine api key
        :param project_name_or_identifier: str or int with either the redmine project id or project identifier
        :param issues_base_directory: str, directory to download the redmine issues in JSON format.  Directory will be crated
        """
        self.redmine_server = redmine_server
        self.redmine_api_key = redmine_api_key
        self.project_name_or_identifier = project_name_or_identifier
        self.issue_dirname = issues_dirname
        msg('redmine2github_id_map_filename: %s' % redmine2github_id_map_filename)
        self.redmine2github_id_map = json.loads(open(redmine2github_id_map_filename, 'r').read())
        
        self.redmine_conn = None
        self.redmine_project = None
        
        self.jinja_env = Environment(loader=PackageLoader('redmine_ticket', 'templates'))
        
        self.setup()
        
    def setup(self):
        self.connect_to_redmine()
        if not isdir(self.issue_dirname):
            msgx('Directory doesn\'t exist: %s' % self.issue_dirname)
        
        
    def connect_to_redmine(self):
        self.redmine_conn = Redmine(self.redmine_server, key=self.redmine_api_key)
        self.redmine_project = self.redmine_conn.project.get(self.project_name_or_identifier)
        msg('Connected to server [%s] project [%s]' % (self.redmine_server, self.project_name_or_identifier))


    def update_tickets(self):
   
        redmine_keys = self.redmine2github_id_map.keys()
        redmine_keys.sort()
        redmine_keys = set(redmine_keys)
        
        ticket_cnt = 0
        for redmine_issue_num in redmine_keys:
            ticket_cnt +=1
            
            msgt('(%s) Updating redmine ticket: %s' % (ticket_cnt, redmine_issue_num))
            github_issue_id = self.redmine2github_id_map.get(redmine_issue_num)
            msg('github_issue_id: %s' % github_issue_id)
    
            fname = redmine_issue_num.zfill(RedmineIssueDownloader.ZERO_PADDING_LEVEL) + '.json'
            redmine_issue_fname = os.path.join(self.issue_dirname, fname)
            if not os.path.isfile(redmine_issue_fname):
                msgx('file not found: %s' % redmine_issue_fname)
            redmine_issue_dict = json.loads(open(redmine_issue_fname, 'r').read())

            github_issue_url = get_gethub_issue_url(github_issue_id)
            
            template = self.jinja_env.get_template('description_with_github_link.md')

            original_description = redmine_issue_dict.get('description', None)                
            #if not original_description:
            #    msgx('Description not found in file: %s' % redmine_issue_fname)
            
            template_params = { 'original_description' : original_description\
                          , 'github_issue_id' : github_issue_id\
                          , 'github_repo' : GITHUB_TARGET_REPOSITORY\
                          , 'github_username' : GITHUB_TARGET_USERNAME\
                          , 'github_issue_url' : github_issue_url\
                        }

            updated_description = template.render(template_params)
            
            #msg(updated_description)
            
            update_params = dict(project_id=self.project_name_or_identifier\
                                , description=updated_description\
                                )
            
            
            updated_record =  self.redmine_conn.issue.update(resource_id=int(redmine_issue_num)\
                                        , **update_params)
            
            dashes()
            
            if updated_record is True:
                msg('-----> Updated!')
            else:
                msgx('Updated Failed!') 
                           
            
            


if __name__=='__main__':
    from settings.base import REDMINE_SERVER, REDMINE_API_KEY, REDMINE_ISSUES_DIRECTORY, REDMINE_TO_GITHUB_MAP_FILE
    
    issues_dir = os.path.join(REDMINE_ISSUES_DIRECTORY, 'x2014-0709')
    #rn = RedmineIssueDownloader(REDMINE_SERVER, REDMINE_API_KEY, 'dvn', REDMINE_ISSUES_DIRECTORY)
    rn = RedmineIssueUpdater(REDMINE_SERVER, REDMINE_API_KEY, 1, issues_dir, REDMINE_TO_GITHUB_MAP_FILE)
    rn.update_tickets()