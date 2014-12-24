import os, sys
from os.path import isfile, isdir, join
import json
import requests

def msg(s): print (s)
def dashes(): msg(40*'-')
def msgt(s): dashes(); msg(s); dashes()
def msgx(s): msgt('Error.  Exiting'); msg(s); dashes(); sys.exit(0)


"""
## FILL IN THE FOLLOWING MANDATORY VARIABLES
REPO_NAME = 'github repository name'
REPO_OWNER_NAME = 'github repository owner name'

GITHUB_AUTH_USERNAME = 'github-username'
# For A GitHub personal access token: https://github.com/settings/applications#personal-access-tokens
GITHUB_PERSONAL_API_TOKEN_OR_PASSWORD = ''  
## end: neeeded MANDATORY VARIABLES

"""
class GithubLabelMaker:
    
    GITHUB_SPEC_ATTRIBUTE_NAMES = [ 'REPO_NAME', 'REPO_OWNER_NAME', 'GITHUB_AUTH_USERNAME', 'GITHUB_PERSONAL_API_TOKEN_OR_PASSWORD' ]
    
    def __init__(self, github_specs_filename, label_specs_filename):

        assert isfile(github_specs_filename), "The github_specs file was not found: %s" % github_specs_filename
        assert isfile(label_specs_filename), "The label specs file was not found: %s" % label_specs_filename
        
        self.load_github_specs_from_json_file(github_specs_filename)
        self.add_labels(label_specs_filename)
    
    
    def load_github_specs_from_json_file(self, github_specs_fname):
        """
        Create and load class attributes for each of the GITHUB_SPEC_ATTRIBUTE_NAMES

        e.g. self.REPO_NAME = 'something in JSON file'
        """
        assert isfile(github_specs_fname), "The github_specs file was not found: %s" % github_specs_filename

        try:
            d = json.loads(open(github_specs_fname, 'rU').read())
        except:
            msgx('Could not parse JSON in file: %s' % github_specs_fname)
        
        for attr in self.GITHUB_SPEC_ATTRIBUTE_NAMES:
            if not d.has_key(attr):
                msgx('Value not found for "%s".  The github specs file "%s" must have a "%s"' % (attr, github_specs_fname, attr ))
            #print ('loaded: %s->%s' % (attr, self.__dict__[attr]))
            self.__dict__[attr] = d[attr]
        
        
    def get_github_auth(self):
        return (self.GITHUB_AUTH_USERNAME, self.GITHUB_PERSONAL_API_TOKEN_OR_PASSWORD)

    def get_label_url(self, label_name):
        assert label_name is not None, "Label name cannot be None"
        
        return 'https://api.github.com/repos/%s/%s/labels/%s' % (self.REPO_OWNER_NAME, self.REPO_NAME, label_name )       
        
    def get_create_label_url(self):
        return 'https://api.github.com/repos/%s/%s/labels' % (self.REPO_OWNER_NAME, self.REPO_NAME )
    
    
    def add_labels(self, label_fname):
        assert isfile(label_fname), 'File not found [%s]' % label_fname
          
        flines = open(label_fname, 'rU').readlines()
    
        # strip lines and skip comments
        #
        flines = [x.strip() for x in flines if len(x.strip()) > 0 and not x.strip()[:1]=='#']
    
        # split each line into a tuple: (label_name, label_color)
        #
        info_lines = [x.split('|') for x in flines if len(x.split('|'))==2]
    
        # Create each label--or update the color if label name exists and color is different
        #
        cnt = 0
        for label_info in info_lines:
            run_update_color = False
            
            if not len(label_info) == 2:    
                continue    # shouldn't happen
            
            
            label_info = [x.strip() for x in label_info]    # strip each value
            label_name, label_color = label_info    # split the tuple into 2 vals
            label_color = label_color.lower()   # color in lowercase
            
        
            if len(label_name) == 0:
                msgx('The label name is blank!\nFrom line with "%s"' % ('|'.join(label_info)))
            
            if not len(label_color)==6:
                msgx('This label color should be 6 characters: "%s"\nFrom line with "%s"' % (label_color, 
                '|'.join(label_info)))
        
            cnt += 1
            msgt('(%s) Create label [%s] with color [%s]' % (cnt, label_name, label_color))
                

            github_label_url = self.get_label_url(label_name)   
            msg('github_label_url: %s' % github_label_url)    
            
            r = requests.get(github_label_url, auth=self.get_github_auth())

            if r.status_code == 200:
                label_json = json.loads(r.text)
                if label_json.get('color', '').lower() == label_color:
                    msg('Label already exists with same color!')
                    continue
                else:
                    msg('Label exists BUT different color...')
                    run_update_color = True
        
            data = dict(name=label_name, color=label_color)
            if run_update_color:
                r = requests.patch(get_label_url, data=json.dumps(data), auth=self.get_github_auth())
            else:
                #create_label_url = 'https://api.github.com/repos/%s/%s/labels' % (REPO_OWNER_NAME, REPO_NAME )
                r = requests.post(self.get_create_label_url(), data=json.dumps(data), auth=self.get_github_auth())
        
        
            if r.status_code == 200:
                msg('Label color updated!')
            elif r.status_code == 201:
                msg('Label created!')
            else:
                msg('Label failed!')
            msg(r.text)



def show_instructions():
    dashes()
    msg("""Please run this script from the command line as follows:
    
     >python label_update.py [github_specs.json] [label input filename]
     example: >python label_update.py github_specs_template.json label_input_dataverse-org.txt

-----------------------------
-- Label Input file --
-----------------------------

Each line of the label input file includes:
    (1) label name
    (2) label color (hex) 

This info is separated by a '|' delimiter.

    Format:  "Label Name|Hex Color"

Notes:
    - The file has no header line. 
    - Blank lines and comment lines ('#') are ignored
    - Each line is trimmed
    - Label names and colors are trimmed
    
Example file contents:

Priority: Critical|ff9900
Priority: High|e11d21
# Priority: Medium|cc6666  -- this line is ignored
Status: Design|66ff66
Status: Dev|66cc66
Status: QA|336633


    """)

if __name__=='__main__':
    if len(sys.argv) == 3:
        GithubLabelMaker(sys.argv[1], sys.argv[2])
        #add_labels(sys.argv[1])
    else:
        show_instructions()
