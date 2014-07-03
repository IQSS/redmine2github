import getpass
from os.path import abspath, dirname, join
import sys

PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(PROJECT_ROOT)

#
#   Redmine API information
#
REDMINE_SERVER = 'https://redmine.hmdc.harvard.edu'

# See http://www.redmine.org/projects/redmine/wiki/Rest_api#Authentication
# "You can find your API key on your account page..."
REDMINE_API_KEY = 'my-api-key from remdine account page'    

GITHUB_SERVER = 'https://api.github.com'
GITHUB_LOGIN = 'github username'
GITHUB_PASSWORD = getpass.getpass('Enter github pw:')

GITHUB_TARGET_REPOSITORY = 'test-issue-migrate'
GITHUB_TARGET_USERNAME = 'target-repo-github-username'

WORKING_FILES_DIRECTORY = join(PROJECT_ROOT, 'working_files')
REDMINE_ISSUES_DIRECTORY = join(WORKING_FILES_DIRECTORY, 'redmine_issues')

# (optional) json dict mapping redmine users to github users
USER_MAP_FILE = join(WORKING_FILES_DIRECTORY, 'redmine2github_user_map.json')

def get_github_auth():
   return dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD, repo=GITHUB_TARGET_REPOSITORY, user=GITHUB_TARGET_USERNAME)
