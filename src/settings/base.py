
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

# (optional) json dict mapping redmine users to github users
USER_MAP_FILE = config.WORKING_FILES_DIRECTORY

def get_github_auth():
   return dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD, repo=GITHUB_TARGET_REPOSITORY, user=GITHUB_TARGET_USERNAME)
