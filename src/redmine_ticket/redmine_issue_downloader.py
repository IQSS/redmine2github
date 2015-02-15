from __future__ import print_function
import os
from os.path import dirname, join, abspath, isdir
import sys
import json
import requests
try:
    from urlparse import urljoin
except:
    from urllib.parse import urljoin        # python 3.x
    
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
    
    def __init__(self, redmine_server, redmine_api_key, project_name_or_identifier, issues_base_directory, **kwargs):
        """
        Constructor
        
        :param redmine_server: str giving the url of the redmine server.  e.g. https://redmine.myorg.edu/
        :param redmine_api_key: str with a redmine api key
        :param project_name_or_identifier: str or int with either the redmine project id or project identifier
        :param issues_base_directory: str, directory to download the redmine issues in JSON format.  Directory will be crated
        :param specific_tickets_to_download: optional, list of specific ticket numbers to download. e.g. [2215, 2216, etc]
        """
        self.redmine_server = redmine_server
        self.redmine_api_key = redmine_api_key
        self.project_name_or_identifier = project_name_or_identifier
        self.issues_base_directory = issues_base_directory
        self.issue_status = kwargs.get('issue_status', '*') # values 'open', 'closed', '*'
        
        self.specific_tickets_to_download = kwargs.get('specific_tickets_to_download', None)
        
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


    def get_issue_count(self):
        msgt('get_issue_count')
        
        issue_query_str = 'issues.json?project_id=%s&limit=1&status_id=%s' \
                            % (self.project_name_or_identifier, self.issue_status)
        
        url = urljoin(self.redmine_server, issue_query_str)
        
        msg('Issue count url: %s' % url)
        
        # Note: Auth purposely uses the API KEY "as a username with a random password via HTTP Basic authentication"
        #   from: http://www.redmine.org/projects/redmine/wiki/Rest_api
        #
        auth = (self.redmine_api_key, 'random-pw')
        r = requests.get(url, auth=auth)
        if not r.status_code == 200:
            msgt('Error!')
            msg(r.text)
            raise Exception("Request for issue count failed! Status code: %s\nUrl: %s\nAuth:%s" % (r.status_code, url, auth))
        
        msg('Convert result to JSON')
        try:
            data = r.json()     # Let it blow up
        except:
            msgt('Error!')
            msg('Data from request (as text): %s' % r.text)
            raise Exception('Failed to convert issue count data to JSON.\nUrl: %s\nAuth:%s" % (url, auth)')
            
        if not data.has_key('total_count'):
            msgx('Total count not found in data: \n[%s]' % data)

        return data['total_count']

        """
from __future__ import print_function
import requests

project_id = 'dvn'
redmine_api_key = 'some-key'
url = 'https://redmine.hmdc.harvard.edu/issues.json?project_id=%s&limit=1' % project_id

#---------------------
# Alternative 1
#---------------------
auth = (redmine_api_key, 'random-pw')
r = requests.get(url, auth=auth)
print (r.text)
print (r.status_code)
data = r.json()
print (data['total_count'])

#---------------------
# Alternative 2
#---------------------
url2 = '%s&key=%s' % (url, redmine_api_key)
r = requests.get(url2)
print (r.text)
print (r.status_code)
data = r.json()
print (data['total_count'])


"""

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
        fyi: Retrieving total count via regular api, not python redmine package
        """
        issue_dict = {}
        issue_fname = join(self.issue_dirname, 'issue_list.json') 
        msg('Gathering issue information.... (may take a minute)')

        ticket_cnt = self.get_issue_count()      
        
        RECORD_RETRIEVAL_SIZE = 100
        
        num_loops = ticket_cnt / RECORD_RETRIEVAL_SIZE
        extra_recs = ticket_cnt % RECORD_RETRIEVAL_SIZE
        if extra_recs > 0:
            num_loops+=1
        #num_loops=3
        msg('num_loops: %d' % num_loops)
        msg('extra_recs: %d' % extra_recs)
        
        cnt = 0
        for loop_num in range(0, num_loops):
            start_record = loop_num * RECORD_RETRIEVAL_SIZE
            end_record = (loop_num+1) * RECORD_RETRIEVAL_SIZE
            
            msgt('Retrieve records via idx (skip last): %s - %s' % (start_record, end_record))
            
            # limit of 100 is returning 125
            rec_cnt = 0
            for item in self.redmine_conn.issue.filter(project_id=self.project_name_or_identifier, status_id=self.issue_status, sort='id', offset=start_record)[:RECORD_RETRIEVAL_SIZE]: #, limit=RECORD_RETRIEVAL_SIZE):   #[start_record:end_record]
                rec_cnt +=1
                cnt +=1
                msg('(%s) %s - %s' % (rec_cnt, item.id, item.subject))
                
                if self.specific_tickets_to_download is not None:
                    # only download specific tickets
                    #
                    if item.id in self.specific_tickets_to_download:
                        self.save_single_issue(item)                    
                        issue_dict[self.pad_issue_id(item.id)] = item.subject
                    continue    # go to next item
                else:
                    # Get all tickets                
                    #
                    self.save_single_issue(item)                    
                    issue_dict[self.pad_issue_id(item.id)] = item.subject
                if rec_cnt == RECORD_RETRIEVAL_SIZE:
                    break
                #continue
                #self.save_single_issue(item)
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
            content = open(join(issues_dirname, fname), 'rU').read()
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
    #rn = RedmineIssueDownloader(REDMINE_SERVER, REDMINE_API_KEY, 'dvn', REDMINE_ISSUES_DIRECTORY)
    #Only import some specific tickets
    #kwargs = dict(specific_tickets_to_download=[1371, 1399, 1843, 2214, 2215, 2216, 3362, 3387, 3397, 3400, 3232, 3271, 3305, 3426, 3425, 3313, 3208])
    rn = RedmineIssueDownloader(REDMINE_SERVER, REDMINE_API_KEY, 1, REDMINE_ISSUES_DIRECTORY, **kwargs)
    rn.download_tickets2()
    
    msg(rn.get_issue_count())
    #rn.show_project_info()
    #rn.process_files()
    #msg(rn.get_single_issue(3232))
    
"""
import json
c = open('issue_list2.txt', 'rU').read()
d = json.loads(c)
print(len(d))
"""
