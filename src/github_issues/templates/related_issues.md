{{ original_description }}

{% if  related_issues or original_issues %}

---

{% if related_issues %}Related issue(s): {{ related_issues }}{% endif %}
{% if original_issues %}Redmine related issue(s): {{ original_issues }}{% endif %}

---
{% endif %}

{% if  child_issues_github or child_issues_original %}
---

{% if child_issues_github %}Child issue(s): {{ child_issues_github }}{% endif %}
{% if child_issues_original %}Redmine child issue(s): {{ child_issues_original }}{% endif %}

---

{% endif %}

