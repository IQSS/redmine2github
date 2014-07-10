import os, sys

"""
Create something like this for github markdown

|Label Name|Label Color|
|------------|------------|
|Priority: Critical|ff9900|
|Priority: High|e11d21|
|Priority: Medium|cc6666|
|Status: Design|66ff66|
|Status: Dev|66cc66|
|Status: QA|336633|
|Type: Bug|fef2c0|
|Type: Feature|fef2c0|
|Type: Suggestion|fef2c0|
|Component: (component name 1)|c7def8|
|Component: (component name 2)|c7def8|

"""
def msg(s): print (s)
def dashes(): msg(40*'-')
def msgt(s): dashes(); msg(s); dashes()
def msgx(s): msgt('Error.  Exiting'); msg(s); dashes(); sys.exit(0)

def get_md_trow(*col_str_vals):
    trow = '|%s|' % ('|'.join(col_str_vals))
    return trow

def get_trow_split(num_cols):    
    dash_list = [ '-'*12 for x in range(0, num_cols)]
    return get_md_trow(*dash_list)
    return trow

def make_md_table(label_fname):
    if not os.path.isfile(label_fname):
        msgx('File not found [%s]' % label_fname)
        
    flines = open(label_fname, 'r').readlines()
    
    # strip lines and skip comments
    flines = [x.strip() for x in flines if len(x.strip()) > 0 and not x.strip()[:1]=='#']
    
    # split lines into two parts
    info_lines = [x.split('|') for x in flines if len(x.split('|'))==2]
    
    cnt = 0
    tlines = []
    tlines.append(get_md_trow('Label Name', 'Label Color'))
    tlines.append(get_trow_split(2))
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
        
        md_row = get_md_trow(label_name, label_color)
        tlines.append(md_row)
    print '\n'.join(tlines)


if __name__=='__main__':
    if len(sys.argv) == 2:
        make_md_table(sys.argv[1])
    else:
        msg('\nPlease use a label input file:')
        msg('\n   >python make_md_table.py label_input.txt\n')
