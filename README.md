## redmine2github

Scripts to migrate redmine tickets to github issues.  This is for a 1-time move.

### Setup with [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html#basic-installation)

* ```mkvirtualenv redmine_move```
* ```pip install -r requirements/base.txt```

### Make a config file

* Copy "/src/settings/local_sample.py to "/src/settings/local.py" and fill in variables
* Fill in your redmine and github credentials
    * For the Redmine API key, see ["You can find your API key on your account page..."](http://www.redmine.org/projects/redmine/wiki/Rest_api#Authentication)
    * For github, you can create a [Personal API token](https://github.com/blog/1509-personal-api-tokens)