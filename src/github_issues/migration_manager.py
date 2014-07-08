import os, sys

if __name__=='__main__':
    SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(SRC_ROOT)

import time
import re
import json
from settings.base import get_github_auth, REDMINE_ISSUES_DIRECTORY, USER_MAP_FILE, LABEL_MAP_FILE, MILESTONE_MAP_FILE, REDMINE_TO_GITHUB_MAP_FILE


from github_issues.user_map_helper import UserMapHelper
from github_issues.github_issue_maker import GithubIssueMaker
from utils.msg_util import *


class MigrationManager:
    """Move the files to github"""
    
    def __init__(self, redmine_json_directory, redmine2github_map_file, **kwargs):
        
        self.redmine_json_directory = redmine_json_directory
        
        # Keep track of redmine issue #'s and related github issue #'s
        self.redmine2github_map_file = redmine2github_map_file
        
        
        self.include_comments = kwargs.get('include_comments', True)
        self.include_assignee = kwargs.get('include_assignee', True)


        self.user_mapping_filename = kwargs.get('user_mapping_filename', None)
        self.label_mapping_filename = kwargs.get('label_mapping_filename', None)
        self.milestone_mapping_filename = kwargs.get('milestone_mapping_filename', None)

        # Start loading with issue number (int) based on json file name
        self.redmine_issue_start_number = kwargs.get('redmine_issue_start_number', 0)

        # (optional) STOP loading at issue number (int) based on json file name.  The stop issue number itself IS loaded
        #       None = go to the end
        self.redmine_issue_end_number = kwargs.get('redmine_issue_end_number', None)

    def does_redmine_json_directory_exist(self):
        if not os.path.isdir(self.redmine_json_directory):
            return False
        return True
        
    def get_redmine_json_fnames(self):
        if not self.does_redmine_json_directory_exist():
            msgx('ERROR: Directory does not exist: %s' % self.redmine_json_directory)
            
        pat ='^\d{1,10}\.json$'
        fnames = [x for x in os.listdir(self.redmine_json_directory) if re.match(pat, x)]
        return fnames

        
    def sanity_check(self):
        # Is there a redmine JSON file directory with JSON files?
        fnames = self.get_redmine_json_fnames()
        if len(fnames)==0:
            msgx('ERROR: Directory [%s] does contain any .json files' % self.redmine_json_directory)
        
        for mapping_filename in [self.user_mapping_filename, self.label_mapping_filename, self.milestone_mapping_filename ]:
            if mapping_filename:   # This mapping files may be None
                if not os.path.isfile(mapping_filename):
                    msgx('ERROR: Mapping file not found [%s]' % mapping_filename)                
        
        
        if not os.path.isdir(os.path.dirname(self.redmine2github_map_file)):
            msgx('ERROR: Directory not found for redmine2github_map_file [%s]' % self.redmine2github_map_file)                
            
        
        if not type(self.redmine_issue_start_number) is int:
            msgx('ERROR: The start issue number is not an integer [%s]' % self.redmine_issue_start_number)                

        if not type(self.redmine_issue_end_number) in (None, int):
            msgx('ERROR: The end issue number must be an integer of None [%s]' % self.redmine_issue_end_number)                
            
            if type(self.redmine_issue_end_number) is int:
                if not self.redmine_issue_end_number >= self.redmine_issue_start_number:
                    msgx('ERROR: The end issue number [%s] must greater than or equal to the start issue number [%s]' % (self.redmine_issue_end_number, self.redmine_issue_start_number))                
                    
        
    def get_user_map_helper(self):
        if not self.user_mapping_filename:
            return None
            
        user_map_helper = UserMapHelper(self.user_mapping_filename)
        
        if user_map_helper.get_key_count() == 0:
            msgx('ERROR. get_user_map_helper.  No names found in user map: %s' % self.user_mapping_filename)
        
        return user_map_helper
        
        
    def save_dict_to_file(self, d):
        
        d_str = json.dumps(d)
        fh = open(self.redmine2github_map_file, 'w')
        fh.write(d_str)
        fh.close()

        
    def get_dict_from_map_file(self):
        
        # new dict, file doesn't exist yet
        if not os.path.isfile(self.redmine2github_map_file):
            return {}   # {redmine issue # : github issue #}
        
        fh = open(self.redmine2github_map_file, 'r')
        content = fh.read()
        fh.close()
        
        # let it blow up if incorrect
        return json.loads(content)


    def migrate_related_tickets(self):
        """
        After github issues are already migrated, go back and udpate the descriptions to include "related tickets
        
        
        """
        
        gm = GithubIssueMaker()
         
        issue_cnt = 0
        redmine2github_issue_map = self.get_dict_from_map_file()
        
        for json_fname in self.get_redmine_json_fnames():
            
            # Pull the issue number from the file name
            redmine_issue_num = int(json_fname.replace('.json', ''))

            # Start processing at or after redmine_issue_START_number
            if not redmine_issue_num >= self.redmine_issue_start_number:
                msg('Skipping Redmine issue: %s (start at %s)' % (redmine_issue_num, self.redmine_issue_start_number ))
                continue        # skip tAttempt to create issue
                # his
            
            # Don't process after the redmine_issue_END_number
            if self.redmine_issue_end_number:
                if redmine_issue_num > self.redmine_issue_end_number:
                    print redmine_issue_num, self.redmine_issue_end_number
                    break
            
            issue_cnt += 1

            msgt('(%s) Loading redmine issue: [%s] from file [%s]' % (issue_cnt, redmine_issue_num, json_fname))
            json_fname_fullpath = os.path.join(self.redmine_json_directory, json_fname)
        
            gm.update_github_issue(json_fname_fullpath, redmine2github_issue_map)
            
    
    
    def migrate_issues(self):
        
        self.sanity_check()

        # Load a map if a filename was passed to the constructor
        #
        user_map_helper = self.get_user_map_helper()    # None is ok
        # Note: for self.label_mapping_filename, None is ok
        gm = GithubIssueMaker(user_map_helper=user_map_helper\
                        , label_mapping_filename=self.label_mapping_filename\
                        , milestone_mapping_filename=self.milestone_mapping_filename
                         )
            
        # Iterate through json files
        issue_cnt = 0
        
        mapping_dict = self.get_dict_from_map_file()    # { redmine issue : github issue }
        for json_fname in self.get_redmine_json_fnames():
            
            # Pull the issue number from the file name
            redmine_issue_num = int(json_fname.replace('.json', ''))

            # Start processing at or after redmine_issue_START_number
            if not redmine_issue_num >= self.redmine_issue_start_number:
                msg('Skipping Redmine issue: %s (start at %s)' % (redmine_issue_num, self.redmine_issue_start_number ))
                continue        # skip tAttempt to create issue
                # his
            
            # Don't process after the redmine_issue_END_number
            if self.redmine_issue_end_number:
                if redmine_issue_num > self.redmine_issue_end_number:
                    print redmine_issue_num, self.redmine_issue_end_number
                    break
            
            issue_cnt += 1

            msgt('(%s) Loading redmine issue: [%s] from file [%s]' % (issue_cnt, redmine_issue_num, json_fname))
            json_fname_fullpath = os.path.join(self.redmine_json_directory, json_fname)
            gm_kwargs = { 'include_assignee' : self.include_assignee \
                         , 'include_comments' : self.include_comments \
                        }
            github_issue_number = gm.make_github_issue(json_fname_fullpath, **gm_kwargs)
        
            if github_issue_number:
                mapping_dict.update({ redmine_issue_num : github_issue_number})
                self.save_dict_to_file(mapping_dict)
        
            if issue_cnt % 50 == 0:
                msgt('sleep 2 seconds....')
                time.sleep(2)

if __name__=='__main__':
    json_input_directory = os.path.join(REDMINE_ISSUES_DIRECTORY, '2014-0708')

    kwargs = dict(include_comments=True\
                , include_assignee=False\
                , redmine_issue_start_number=1828\
                , redmine_issue_end_number=1828\
                #, user_mapping_filename=USER_MAP_FILE       # optional
                , label_mapping_filename=LABEL_MAP_FILE     # optional
                , milestone_mapping_filename=MILESTONE_MAP_FILE # optional
            )
    mm = MigrationManager(json_input_directory\
                            , REDMINE_TO_GITHUB_MAP_FILE\
                            , **kwargs)
    mm.migrate_issues()
    #mm.migrate_related_tickets()


        