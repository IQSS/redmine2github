import getpass
from os.path import abspath, dirname, join
import sys

PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(PROJECT_ROOT)

#
#   Redmine API information
#
REDMINE_SERVER = 'https://redmine.my-org.edu'

# See http://www.redmine.org/projects/redmine/wiki/Rest_api#Authentication
# "You can find your API key on your account page..."
REDMINE_API_KEY = 'my-api-key from remdine account page'    

GITHUB_SERVER = 'https://api.github.com'
GITHUB_LOGIN = 'github username'
GITHUB_PASSWORD_OR_PERSONAL_ACCESS_TOKEN = getpass.getpass('Enter github pw:')

GITHUB_TARGET_REPOSITORY = 'test-issue-migrate'
GITHUB_TARGET_USERNAME = 'target-repo-github-username'

WORKING_FILES_DIRECTORY = join(PROJECT_ROOT, 'working_files')
REDMINE_ISSUES_DIRECTORY = join(WORKING_FILES_DIRECTORY, 'redmine_issues')

# JSON file mapping { redmine issue # : github issue # }
REDMINE_TO_GITHUB_MAP_FILE = join(WORKING_FILES_DIRECTORY, 'redmine2github_issue_map.json')

# (optional) csv file mapping Redmine users to github users.  
# Manually created.  Doesn't check for name collisions
# example, see settings/sample_user_map.csv
USER_MAP_FILE = join(WORKING_FILES_DIRECTORY, 'redmine2github_user_map.csv')

# (optional) csv file mapping Redmine status, tracker, priority, and custom fields names to github labels.
# Manually created.  Doesn't check for name collisions
#   example, see settings/sample_label_map.csv
LABEL_MAP_FILE = join(WORKING_FILES_DIRECTORY, 'redmine2github_label_map.csv')

# (optional) csv file mapping Redmine "target version" to GitHub milestones.
# Manually created.  Doesn't check for name collisions
#   example, see settings/sample_milestone_map.csv
MILESTONE_MAP_FILE = join(WORKING_FILES_DIRECTORY, 'redmine2github_milestone_map.csv')

def get_github_auth():
   return dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD_OR_PERSONAL_ACCESS_TOKEN, repo=GITHUB_TARGET_REPOSITORY, user=GITHUB_TARGET_USERNAME)
