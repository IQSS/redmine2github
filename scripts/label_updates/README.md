## Label Guide / Colors

The Label Name/Color table below shows the label names and colors for:

* Priority
* Status
* Type
* Components - Add specific component names for your file
 

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

### Scripting in your labels

The [add_update_labels.py](https://github.com/IQSS/redmine2github/blob/master/scripts/label_updates/add_update_labels.py) script in this directory may be used to script in your labels via the GitHub API.

1.  Fill in the "MANDATORY VARIABLES" at the top.
1.  Create a issue map similar to ["sample_label_input.txt"](https://github.com/IQSS/redmine2github/blob/master/scripts/label_updates/sample_label_input.txt)
1.  Run the script against the file:

```python
>python add_update_labels.py sample_label_input.txt
```
