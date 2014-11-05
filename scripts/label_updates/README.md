# Add Colored Labels to GitHub Issues via API

## Create a github_specs.json file

* Example file contents

```json
{
    "REPO_OWNER_NAME": "IQSS", 
    "REPO_NAME": "dataverse.org",
    "GITHUB_AUTH_USERNAME": "my_github_username", 
    "GITHUB_PERSONAL_API_TOKEN_OR_PASSWORD": "abcd-abcd-abcd-abcd-abcd-abcd-abcd"
}
```

* Template file: (github_specs/template_github_specs.json)
* ```GITHUB_PERSONAL_API_TOKEN_OR_PASSWORD``` - See [Github instructions to create a Personal API Token](https://github.com/blog/1509-personal-api-tokens)

## Create a label specs file

### Label Guide / Colors

The Label Name/Color table below shows the label names and colors for:

* Priority
* Status
* Type
* Components - Add specific component names for your file
 
- Sample file: ["sample_label_input.txt"](https://github.com/IQSS/redmine2github/blob/master/scripts/label_updates/label_specs/sample_label_input.txt) 

### Label Name/Color table

+ [See label colors in Dataverse](https://github.com/IQSS/dataverse/issues/new)


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

Notes:
+ All Types have the same color
+ All Components have the same color

### Run label making scripts

The [add_update_labels.py](https://github.com/IQSS/redmine2github/blob/master/scripts/label_updates/add_update_labels.py) script in this directory may be used to script in your labels via the GitHub API.

1.  Fill in the "MANDATORY VARIABLES" at the top.
1.  Create a issue map similar to 
1.  Run the script against the file:

```python
>python add_update_labels.py sample_label_input.txt
```
