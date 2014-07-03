import csv
import os
from utils.msg_util import *

class LabelInfo:
    ATTR_NAMES = """redmine_type redmine_name github_label_name github_label_color""".split()
    
    def __init__(self, row):
        if not row or not len(row) == 4:
            msgx('Expected 4 values in this row: %s' % row)
        
        for idx, item in enumerate(row):
            self.__dict__[self.ATTR_NAMES[idx]] = item.strip()

    def get_label_dict_info(self):
        return { self.redmine_name : self}
        
class LabelMap:
    
    def __init__(self, label_map_fname):
        self.label_map_fname = label_map_fname
        #self.map_lookup = {}    # redmine_type : { redmine_name : LabelInfo }
        self.label_lookup = {}    # { redmine_name : LabelInfo }
        
        self.load_map_lookup()
    
    def get_key_count(self):
        return len(self.map_lookup)
        
    def get_label_info_objects(self):
        if not type(self.label_lookup) is dict:
            return None
            
        return self.label_lookup.values()
        
    def load_map_lookup(self):
        if not os.path.isfile(self.label_map_fname):
            msgx('Error: user name file not found: %s' % self.label_map_fname)

        msgt('Loading label map: %s' % self.label_map_fname)
        with open(self.label_map_fname, 'rb') as csvfile:
            map_reader = csv.reader(csvfile, delimiter=',')#, quotechar='|')
            row_num = 0
            for row in map_reader:
                row_num += 1
                if row_num == 1: continue       # skip header row
                if len(row) == 0: continue
                if row[0].startswith('#'): continue
                label_info = LabelInfo(row)
                
                self.label_lookup.update(label_info.get_label_dict_info())                

        msg('Label dict loaded as follows.\nRemember: the "redmine_type" column in the .csv is ignored by the system--it is only for user convenience')
        dashes()
        for redmine_name, label_info in self.label_lookup.items():
            msg('[%s] -> [%s][%s]' % (redmine_name, label_info.github_label_name, label_info.github_label_color))


    def get_github_label_from_redmine_name(self, redmine_name):
        if not redmine_name:
            return None
        
        label_info = self.label_lookup.get(redmine_name.strip(), None)
        if label_info:
            return label_info.github_label_name
        return None
