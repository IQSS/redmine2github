## redmine2github

Scripts to migrate redmine tickets to github issues.  This is for a 1-time move--so it's a mix of automation and manual decisions.  e.g., Get-it-done, but make the process repeatable.

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

Note 2: The current [GitHub API limit](https://developer.github.com/v3/rate_limit/) is 5,000/day.  Adding each issue may have 1-n API calls.  Plan appropriately.

+ 1 API Call: Create issue with labels, milestones, assignee 
    + This process creates a json file mapping { Redmine issue number : GitHub issue number}
+ 0-n API Calls for comments: A single API call is used to transfer each comment
+ 2 API Calls for related issues (optional): After all issues are moved
    + Call 1: Read each GitHub issue
    + At the bottom of the description, use the Redmine->GitHub issue number mapping to add related issue numbers
    + Call 2: Update the GitHub description
---        

#### Label Map Notes

The label map is optional.  It allows you to assign label names and colors by creating a label map file.

+ See [Sample Label Map, sample_label_map.csv](https://github.com/IQSS/redmine2github/blob/master/src/settings/sample_label_map.csv)
+ Pertains to Redmine name values in fields **status, tracker, priority, or custom_fields**
+ If no map is specified in the [MigrationManager kwargs](https://github.com/IQSS/redmine2github/blob/master/src/github_issues/migration_manager.py#L127):
    * The status, tracker, priority, or custom_fields names in Redmine issues are made into GitHub labels

**Map Notes** - How is the map used


    + The map is specfied in the [settings/local.py file](https://github.com/IQSS/redmine2github/blob/master/src/settings/local_sample.py)
    + If a status, tracker, priority, or custom_field name in a Redmine ticket is NOT found in the map, that name value will NOT be moved to GitHub
    + The map file is "dumb." If you would like to map more than one status name to a single status label, simply repeat it.
    
```csv
redmine_type, redmine_name, github_label_name, github_label_color
status, In Design, Status 3: In Design/Dev,996600
status, In Dev, Status 3: In Design/Dev,996600
``` 

        In the example above, the redmine status names "In Design" and "In Dev" are _both_ mapped to the label named "Status 3: In Design/Dev"
    + When the map is read, the values are trimmed.  e.g. ",    In Design ," would become "In Design" with leading/trailing spaces removed 
    

