import csv
import os
from utils.msg_util import *

class UserMapHelper:
    
    def __init__(self, user_map_fname):
        self.user_map_fname = user_map_fname
        self.map_lookup = {}    # Redmine username : Github Account
        self.load_map_lookup()
    
    def get_key_count(self):
        return len(self.map_lookup)
        
    def load_map_lookup(self):
        if not os.path.isfile(self.user_map_fname):
            msgx('Error: user name file not found: %s' % self.user_map_fname)

        with open(self.user_map_fname, 'rb') as csvfile:
            map_reader = csv.reader(csvfile, delimiter=',')#, quotechar='|')
            for row in map_reader:
                if len(row) ==2:
                    self.map_lookup[row[0].strip()] = row[1].strip()

        for k, v in self.map_lookup.items():
            msgt('[%s] -> [%s]' % (k, v))
        msg('User map loaded with %s names' % len(self.map_lookup))

    def get_github_user(self, redmine_name, with_github_at=True):
        if not redmine_name:
            return None
        
        github_name = self.map_lookup.get(redmine_name.strip(), None)
        if github_name is None:
            return None
        
        if with_github_at:
            return '@' + github_name
        
        return github_name