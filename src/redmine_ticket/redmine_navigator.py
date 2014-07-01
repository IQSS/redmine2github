#from __future__ import print_function
import os
from os.path import dirname, join, abspath, isdir
import sys
import json

# http://python-redmine.readthedocs.org/
from redmine import Redmine

if __name__=='__main__':
    SRC_ROOT = dirname(dirname(abspath(__file__)))
    sys.path.append(SRC_ROOT)

from settings.base import REDMINE_SERVER, REDMINE_API_KEY, REDMINE_ISSUES_DIRECTORY
from datetime import datetime
from utils.msg_util import *

class RedmineNavigator:
    
    #TIME_FORMAT_STRING = '%Y-%m%d-%H%M'
    TIME_FORMAT_STRING = '%Y-%m%d'
    
    def __init__(self, redmine_server, redmine_api_key, project_name_or_id):
        self.redmine_server = redmine_server
        self.redmine_api_key = redmine_api_key
        self.project_name_or_id = project_name_or_id
        self.num_issues = num_issues

        self.redmine_conn = None
        self.redmine_project = None
        
        self.issue_dirname = join(REDMINE_ISSUES_DIRECTORY\
                                ,  datetime.today().strftime(RedmineNavigator.TIME_FORMAT_STRING)\
                                )
        
        self.setup()
        
    def setup(self):
        self.connect_to_redmine()
        if not isdir(self.issue_dirname):
            os.makedirs(self.issue_dirname)
            msgt('Directory created: %s' % self.issue_dirname)
        
    def connect_to_redmine(self):
        self.redmine_conn = Redmine(self.redmine_server, key=self.redmine_api_key)
        self.redmine_project = self.redmine_conn.project.get(self.project_name_or_id)
        msg('Connected to server [%s] project [%s]' % (self.redmine_server, self.project_name_or_id))

    def write_issue_list(self, issue_fname, issue_dict):
        if issue_fname is None or not type(issue_dict) == dict:
            msgx('ERROR: write_issue_list, issue_fname is None or issue_dict not dict')
            return
        fh = open(issue_fname, 'w')
        fh.write(json.dumps(issue_dict))    
        fh.close()
        msg('file updated: %s' % issue_fname)
        
        
    def download_tickets(self):
       
        issue_dict = {}
        issue_fname = join(self.issue_dirname, 'issue_list.txt') 

        for item in self.redmine_project.issues:
            msg('%s - %s' % (item.id, item.subject))
            issue_dict[item.id] = item.subject
            self.download_single_issue(item)
            
        self.write_issue_list(issue_fname, issue_dict)
        return
        
        #fh = open(issue_fname, 'a')
        """
        # not needed, only 700+ tickets
        record_retrieval_size = 100
        num_loops = self.num_issues / record_retrieval_size
        extra_recs = self.num_issues % record_retrieval_size
        print 'num_loops', num_loops
        print 'extra_recs', extra_recs
        
        for loop_num in range(0, num_loops):
            start_record = loop_num * record_retrieval_size
            end_record = (loop_num+1) * record_retrieval_size
            msgt('Retrieve records: %s - %s' % (start_record, end_record))
            for item in self.redmine_project.issues[start_record:end_record]:
                msg('%s - %s' % (item.id, item.subject))
                issue_dict[item.id] = item.subject
           
            self.write_issue_list(issue_fname, issue_dict)
            
        if extra_recs > 0:
            start_record = (num_loops) * record_retrieval_size
            end_record = start_record + extra_recs
            msgt('Retrieve records: %s - %s' % (start_record, end_record))
            for item in self.redmine_project.issues[start_record:end_record]:
                msg('%s - %s' % (item.id, item.subject))
                issue_dict[item.id] = item.subject

            self.write_issue_list(issue_fname, issue_dict)
        """
            
    def download_single_issue(self, single_issue):
        #ticket_id = 4048
        #issue = self.redmine_conn.issue.get(4048, include='children,journals,watchers,relations')
        json_str = json.dumps(single_issue._attributes, indent=4)

        ticket_str = '%d' % single_issue.id
        fullpath = join(self.issue_dirname, '%s.json' % ticket_str.zfill(6)) 
        open(fullpath, 'w').write(json_str)
        msg('Ticket retrieved: %s' % fullpath)
        
        
    def xdownload_issues(self):
        # test using .issue.get
        ticket_id = 4048
        issue = self.redmine_conn.issue.get(4048, include='children,journals,watchers,relations')
        json_str = json.dumps(issue._attributes, indent=4)
        
        ticket_str = '%d' % ticket_id
        fullpath = join(self.issue_dirname, '%s.json' % ticket_str.zfill(6)) 
        open(fullpath, 'w').write(json_str)
        msg('Ticket retrieved: %s' % fullpath)


if __name__=='__main__':
    rn = RedmineNavigator(REDMINE_SERVER, REDMINE_API_KEY, 1)
    rn.download_tickets()
    #rn.download_issues()
    
"""
import json
c = open('issue_list2.txt', 'r').read()
d = json.loads(c)
print len(d)
"""
