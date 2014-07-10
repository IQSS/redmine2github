l = [
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Status%3A+QA",
    "name": "Status: QA",
    "color": "336633"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Type%3A+Feature",
    "name": "Type: Feature",
    "color": "fef2c0"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Component%3A+Search%2FBrowse",
    "name": "Component: Search/Browse",
    "color": "c7def8"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Component%3A+UX+%26+Upgrade",
    "name": "Component: UX & Upgrade",
    "color": "c7def8"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Priority%3A+Medium",
    "name": "Priority: Medium",
    "color": "cc6666"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Type%3A+Suggestion",
    "name": "Type: Suggestion",
    "color": "fef2c0"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Status%3A+Design",
    "name": "Status: Design",
    "color": "66ff66"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Status%3A+Dev",
    "name": "Status: Dev",
    "color": "66cc66"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Component%3A+High-level",
    "name": "Component: High-level",
    "color": "c7def8"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Component%3A+Metadata",
    "name": "Component: Metadata",
    "color": "c7def8"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Priority%3A+High",
    "name": "Priority: High",
    "color": "e11d21"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Component%3A+API",
    "name": "Component: API",
    "color": "c7def8"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Component%3A+File+Upload+%26+Handling",
    "name": "Component: File Upload & Handling",
    "color": "c7def8"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Component%3A+Migration",
    "name": "Component: Migration",
    "color": "c7def8"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Priority%3A+Critical",
    "name": "Priority: Critical",
    "color": "ff9900"
  },
  {
    "url": "https://api.github.com/repos/IQSS/dataverse/labels/Type%3A+Bug",
    "name": "Type: Bug",
    "color": "fef2c0"
  }
]

fmt = []
for info in l:
    m = '%s|%s' % (info.get('name'), info.get('color'))
    print m
    fmt.append(m)
    
fmt.sort()
print '-' *50
print '\n'.join(fmt)
