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

WORKING_FILES_DIRECTORY = join(PROJECT_ROOT, 'working_files')
REDMINE_ISSUES_DIRECTORY = join(WORKING_FILES_DIRECTORY, 'redmine_issues')