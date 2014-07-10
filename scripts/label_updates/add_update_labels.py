import os, sys
import json
import requests

def msg(s): print (s)
def dashes(): msg(40*'-')
def msgt(s): dashes(); msg(s); dashes()
def msgx(s): msgt('Error.  Exiting'); msg(s); dashes(); sys.exit(0)


# FILL IN THE FOLLOWING MANDATORY VARIABLES
REPO_NAME = 'github repository name'
REPO_OWNER_NAME = 'github repository owner name'

GITHUB_AUTH_USERNAME = 'github-username'
# For A GitHub personal access token: https://github.com/settings/applications#personal-access-tokens
GITHUB_AUTH_TOKEN_OR_PASSWORD = ''  
######## end: neeeded MANDATORY VARIABLES


def add_labels(label_fname):
    if not os.path.isfile(label_fname):
        msgx('File not found [%s]' % label_fname)
        
    flines = open(label_fname, 'r').readlines()
    
    # strip lines and skip comments
    flines = [x.strip() for x in flines if len(x.strip()) > 0 and not x.strip()[:1]=='#']
    
    # split lines into two parts
    info_lines = [x.split('|') for x in flines if len(x.split('|'))==2]
    
    cnt = 0
    for label_info in info_lines:
        run_update_color = False
        if not len(label_info) == 2:    
            continue    # shouldn't happen
        label_info = [x.strip() for x in label_info]
        label_name, label_color = label_info
        label_color = label_color.lower()
        
        if not len(label_name) > 0:
            msgx('The label name is blank!\nFrom line with "%s"' % ('|'.join(label_info)))
        if not len(label_color)==6:
            msgx('This label color should be 6 characters: "%s"\nFrom line with "%s"' % (label_color, 
            '|'.join(label_info)))
        
        cnt += 1
        msgt('(%s) Create label [%s] with color [%s]' % (cnt, label_name, label_color))
                
        get_label_url = 'https://api.github.com/repos/%s/%s/labels/%s' % (REPO_OWNER_NAME, REPO_NAME, label_name )       
        r = requests.get(get_label_url, auth=(GITHUB_AUTH_USERNAME, GITHUB_AUTH_TOKEN_OR_PASSWORD))
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
            r = requests.patch(get_label_url, data=json.dumps(data), auth=(GITHUB_AUTH_USERNAME, GITHUB_AUTH_TOKEN_OR_PASSWORD))
        else:
            create_label_url = 'https://api.github.com/repos/%s/%s/labels' % (REPO_OWNER_NAME, REPO_NAME )
            r = requests.post(create_label_url, data=json.dumps(data), auth=(GITHUB_AUTH_USERNAME, GITHUB_AUTH_TOKEN_OR_PASSWORD))
        
        
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
    
     >python label_update.py [label input filename]
     example: >python label_update.py label_input.txt

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
    if len(sys.argv) == 2:
        add_labels(sys.argv[1])
    else:
        show_instructions()
