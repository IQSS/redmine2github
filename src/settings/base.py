
import settings.local as config

#
#   Redmine API information
#   https://redmine.hmdc.harvard.edu
#
REDMINE_SERVER = config.REDMINE_SERVER   
REDMINE_API_KEY = config.REDMINE_API_KEY


#
#   GitHub API information
#   https://github.com/blog/1509-personal-api-tokens
#
GITHUB_SERVER = config.GITHUB_SERVER
GITHUB_LOGIN = config.GITHUB_LOGIN
GITHUB_PASSWORD = config.GITHUB_PASSWORD

GITHUB_TARGET_REPOSITORY = config.GITHUB_TARGET_REPOSITORY
GITHUB_TARGET_USERNAME = config.GITHUB_TARGET_USERNAME


#
#  Working files directory
#
WORKING_FILES_DIRECTORY = config.WORKING_FILES_DIRECTORY
REDMINE_ISSUES_DIRECTORY = config.REDMINE_ISSUES_DIRECTORY 

# (optional) csv file mapping Redmine users to github users.  
# Manually created.  Doesn't check for name collisions
#   example, see settings/sample_user_map.csv
USER_MAP_FILE = config.USER_MAP_FILE        

# (optional) csv file mapping Redmine status, tracker, priority, and custom fields names to github labels.
# Manually created.  Doesn't check for name collisions
#   example, see settings/sample_label_map.csv
LABEL_MAP_FILE = config.LABEL_MAP_FILE      

def get_github_auth():
   return dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD, repo=GITHUB_TARGET_REPOSITORY, user=GITHUB_TARGET_USERNAME)
