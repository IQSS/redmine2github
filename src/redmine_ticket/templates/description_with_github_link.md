{% if github_issue_url %}

h1. !! Ticket moved to GitHub: "{{github_username}}/{{github_repo}}/{{ github_issue_id }}":{{ github_issue_url }}
{% endif %}


{% if original_description %}
----


{{ original_description }}
{% endif %}