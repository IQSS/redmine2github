## redmine2github

Scripts to migrate redmine tickets to github issues.  This is for a 1-time move--so it's a mix of automation and manual decisions

### Setup with [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html#basic-installation)

* ```mkvirtualenv redmine_move```
* ```pip install -r requirements/base.txt```

### Make a config file

* Copy "/src/settings/local_sample.py to "/src/settings/local.py" and fill in variables
* Fill in your redmine and github credentials
    * For the Redmine API key, see ["You can find your API key on your account page..."](http://www.redmine.org/projects/redmine/wiki/Rest_api#Authentication)
    * For github, enter your credentials.
        (To do, use a [Personal API token](https://github.com/blog/1509-personal-api-tokens))
        
### Workflow
        
#### (1) Download your open redmine issues

* Each issue is saved as a .json file, including relevant "children", "journals", "watchers", "relations"
    * The file naming convention is by ticket issue number.  
        * e.g. Issue 387 becomes "00387.json"
    * Files are saved to the following directory:
        * from settings/local.py:  (REDMINE_ISSUES_DIRECTORY)/(current date in 'YYYY_MMDD' format)
* A json dict is saved to "issues_list.json" that maps the redmine issue number to the issue subject.  For example:

```javascript
    {
        "03982": "Create Genomics Metadata Block", 
        "04050": "Additional Astronomy FITS File Metadata Support for Units", 
        "04051": "Metadata: Astronomy - Changes to Ingest and Display of Resolution Elements", 
        "04072": "Edit Dataverse: Checking/unchecking use facets from Host Dataverse undoes any changes in the rest of the form."
    }
    
```

#### (2) Migrate your issues to a github repository

---

Note 1:  Once added, a github issue **cannot be deleted**.  Therefore, to test your migration, create a new "scratch" github repository.  Once you're satisfied that the migration works, delete the scratch repository.   
---

--- 

Note 2: The current [GitHub API limit](https://developer.github.com/v3/rate_limit/) is 5,000/day.  Adding each issue may use up to 3 API calls.  Plan appropriately.

+ API Call 1: Create issue with labels, milestones, assignee 
    + This process creates a json file mapping { Redmine issue number : GitHub issue number}
+ API Calls 2 & 3 (optional): After all issues are moved
    + Call 2: Read each GitHub issue
    + At the bottom of the description, use the Redmine->GitHub issue number mapping to add related issue numbers
    + Update the GitHub description
        