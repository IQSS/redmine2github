from __future__ import print_function
import os
import sys
import json


if __name__=='__main__':
    SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(SRC_ROOT)

from datetime import datetime

from jinja2 import Template
from jinja2 import Environment, PackageLoader

from utils.msg_util import *
from github_issues.md_translate import translate_for_github


#from settings.base import GITHUB_LOGIN, GITHUB_PASSWORD, GITHUB_TARGET_REPOSITORY, GITHUB_TARGET_USERNAME
from settings.base import get_github_auth   #GITHUB_LOGIN, GITHUB_PASSWORD, GITHUB_TARGET_REPOSITORY, GITHUB_TARGET_USERNAME
from settings.base import REDMINE_SERVER#, REDMINE_API_KEY, REDMINE_ISSUES_DIRECTORY

import pygithub3

class GithubMilestoneManager:
    """
    Certain redmine attributes, such as "fixed_version", will be translated into milestones
    """
    
    def __init__(self):     
        self.github_conn = None
        self.milestone_service = None
        self.get_github_conn()   
        
    def get_github_conn(self):

        if self.github_conn is None:
            #auth = dict(login=GITHUB_LOGIN, password=GITHUB_PASSWORD, repo=GITHUB_TARGET_REPOSITORY, user=GITHUB_TARGET_USERNAME)
            self.github_conn = pygithub3.Github(**get_github_auth())
        return self.github_conn
        
    def get_create_milestone_number(self, title):
        """Given a milestone title, retrieve the milestone number.
        If the milestone doesn't exist, then create it and return the new number
        """
        if not title:
            return None
        
        mnum = self.get_mile_stone_number(title)
        if mnum:
            return mnum
        
        
        mstone = self.get_milestones_service().create({'title': title})
    
        return mstone.number
    
    def get_mile_stone_number(self, title):
        """Given a milestone title, retrieve the milestone number.
        
        :param title: str, the title of the milestone
        :returns: int or None.  The milestone number or None, if the milestone is not found
        """
        
        if not title:
            return None
        
        milestones = self.get_milestones_service().list()
        """
        for page in milestones:
            print('--page--')
            for resource in page:
                print('--resource--')
                print (resource)
                print (resource.number)
                print (resource.title)
        return
        """
        for page in milestones:
            for resource in page:
                if resource.title == title:
                    return resource.number
        return None
    
    
    def get_milestones_service(self):
        
        if self.milestone_service is None:
            self.milestone_service = pygithub3.services.issues.Milestones(**get_github_auth())
            #labels_service = pygithub3.services.issues.Labels(**auth)
            # #labels_service = pygithub3.services.issues.Labels(**auth)
            #pygithub3.services.issues.Comments(**config)

        return self.milestone_service
        
        
if __name__=='__main__':
    mstones = GithubMilestoneManager()
    #print(mstones.get_create_milestone_number('Pre-Alpha'))
    #print(mstones.get_mile_stone_number('Pre-Alpha'))
    print(mstones.get_create_milestone_number('We did it'))
        