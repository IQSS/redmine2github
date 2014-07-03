from __future__ import print_function
import os
from os.path import dirname, join, abspath, isdir
import sys
import json

# http://python-redmine.readthedocs.org/
from redmine import Redmine

if __name__=='__main__':
    SRC_ROOT = dirname(dirname(abspath(__file__)))
    sys.path.append(SRC_ROOT)

from datetime import datetime
from utils.msg_util import *

class RedmineIssueDownloader:
    """
    For a given Redmine project, download the issues in JSON format
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
    ZERO_PADDING_LEVEL = 5
    
    def __init__(self, redmine_server, redmine_api_key, project_name_or_identifier, issues_base_directory):
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
        self.issues_base_directory = issues_base_directory
        
        #self.num_issues = num_issues

        self.redmine_conn = None
        self.redmine_project = None
        
        self.issue_dirname = join(self.issues_base_directory\
                                ,  datetime.today().strftime(RedmineIssueDownloader.TIME_FORMAT_STRING)\
                                )
        
        self.setup()
        
    def setup(self):
        self.connect_to_redmine()
        if not isdir(self.issue_dirname):
            os.makedirs(self.issue_dirname)
            msgt('Directory created: %s' % self.issue_dirname)
        
    def connect_to_redmine(self):
        self.redmine_conn = Redmine(self.redmine_server, key=self.redmine_api_key)
        self.redmine_project = self.redmine_conn.project.get(self.project_name_or_identifier)
        msg('Connected to server [%s] project [%s]' % (self.redmine_server, self.project_name_or_identifier))

    def write_issue_list(self, issue_fname, issue_dict):
        if issue_fname is None or not type(issue_dict) == dict:
            msgx('ERROR: write_issue_list, issue_fname is None or issue_dict not dict')
            return
        fh = open(issue_fname, 'w')
        fh.write(json.dumps(issue_dict))    
        fh.close()
        msg('file updated: %s' % issue_fname)
    
    def show_project_info(self):        
        msg(self.redmine_project._attributes)

    
    def download_tickets2(self):
        """
        Doesn't work b/c "total_count" not available
        """
        pass
        issue_dict = {}
        issue_fname = join(self.issue_dirname, 'issue_list.json') 
        msg('Gathering issue information.... (may take a minute)')

        ticket_cnt = self.redmine_project.total_count       # not available w/o iterating through issues.....
        
        num_loops = self.num_issues / record_retrieval_size
        extra_recs = self.num_issues % record_retrieval_size
        
        msg('num_loops: %d' % num_loops)
        msg('extra_recs: %d' % extra_recs)
        
        cnt = 0
        for loop_num in range(0, num_loops):
            start_record = loop_num * record_retrieval_size
            end_record = (loop_num+1) * record_retrieval_size
            
            msgt('Retrieve records: %s - %s' % (start_record, end_record))
            
            for item in self.redmine_project.issues[start_record:end_record]:
                cnt +=1
                msg('%s - %s' % (item.id, item.subject))
                if cnt >= save_at_count:
                    issue_dict[self.pad_issue_id(item.id)] = item.subject
                    self.save_single_issue(item)
                else:
                    msg('--skipped save--')
            self.write_issue_list(issue_fname, issue_dict)
        
       

    def download_tickets(self, save_at_count=1):
        """
        Download the Redmine tickets and save as individual JSON files.  
        These files are saved to a directory with the naming convention: 
           
            issues_base_directory (from constructor) + YYYY-MMDD
        
        To change the time string format, modify this class's TIME_FORMAT_STRING
        
        :param save_at_count: optional int, start saving the tickets at this ticket count.  The count is specific to this program.  e.g. The print command will show (cnt:1), (cnt:2), etc.  If you want to start saving files at a specific count, then use this parameter.  May be useful if restarting program, etc.
        
        """
        issue_dict = {}
        issue_fname = join(self.issue_dirname, 'issue_list.json') 
        msg('Gathering issue information.... (may take a minute)')
        cnt = 0
        
        for item in self.redmine_conn.issue.all(sort='id'):
            cnt +=1
            dashes()
            msg('(cnt:%s) \nDownload issue id [%s] \nSubject [%s]' % (cnt, item.id, item.subject))
            if cnt >= save_at_count:
                issue_dict[self.pad_issue_id(item.id)] = item.subject
                self.save_single_issue(item)
            else:
                msg('(skip save)')
                
        self.write_issue_list(issue_fname, issue_dict)

    def pad_issue_id(self, issue_id):
        if issue_id is None:
            msgx('ERROR. pad_issue_id. The "issue_id" is None')
        
        return ('%s' % issue_id).zfill(self.ZERO_PADDING_LEVEL)
 
    def save_single_issue(self, single_issue):
        """
        Write a single issue object to a file using JSON format
        
        :param single_issue: Issue object
        """
        if single_issue is None:
            msgx('ERROR. download_single_issue. The "single_issue" is None')
        
        ## FIX: Expensive adjustment -- to pull out full relation and journal info
        json_str = self.get_single_issue(single_issue.id)       # another call to redmine
        
        #json_str = json.dumps(single_issue._attributes, indent=4)

        fullpath = join(self.issue_dirname, self.pad_issue_id(single_issue.id) + '.json')
        open(fullpath, 'w').write(json_str)
        msg('Ticket retrieved: %s' % fullpath)

   
   
    def process_files(self, issues_dirname=None):
        if issues_dirname is None:
            issues_dirname = self.issue_dirname
            
        tracker_info = []
        status_info = []
        priority_info = []
        
        fnames = [x for x in os.listdir(issues_dirname) if x.endswith('.json')]
        for fname in fnames:
            content = open(join(issues_dirname, fname), 'r').read()
            d = json.loads(content)
        
            
            # Tracker Info
            tracker = d.get('tracker', None)
            if tracker:
                tracker_str = '%s|%s' % (tracker['id'], tracker['name'])
                if not tracker_str in tracker_info:
                    tracker_info.append(tracker_str)
            # Status Info
            status = d.get('status', None)
            if status:
                status_str = '%s|%s' % (status['id'], status['name'])
                if not status_str in status_info:
                    status_info.append(status_str)
            
            # Priority Info
            priority = d.get('priority', None)
            if priority:
                priority_str = '%s|%s' % (priority['id'], priority['name'])
                if not priority_str in priority_info:
                    priority_info.append(priority_str)
        #print d.keys()
        msg(tracker_info)
        msg(status_info)
        msg(priority_info)
        
        
    def get_single_issue(self, issue_id):
        """
        Download a single issue
        
        :param ticket_id: int of issue id in redmine
        :returns: json string with issue information
        """
        # test using .issue.get
        issue = self.redmine_conn.issue.get(issue_id, include='children,journals,watchers,relations')
        json_str = json.dumps(issue._attributes, indent=4)
        msg('Issue retrieved: %s' % issue_id)
        return json_str


if __name__=='__main__':
    from settings.base import REDMINE_SERVER, REDMINE_API_KEY, REDMINE_ISSUES_DIRECTORY
    rn = RedmineIssueDownloader(REDMINE_SERVER, REDMINE_API_KEY, 'dvn', REDMINE_ISSUES_DIRECTORY)
    rn.download_tickets()
    #rn.show_project_info()
    #rn.process_files()
    #msg(rn.get_single_issue(4156))
    
"""
import json
c = open('issue_list2.txt', 'r').read()
d = json.loads(c)
print(len(d))
"""
