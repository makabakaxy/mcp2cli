# CLI Mapping File Example

Below is a complete `cli/<server>.yaml` example showing the standard output format.
Please strictly follow this format when generating.

## Example: mcp-atlassian.yaml

```yaml
server: mcp-atlassian
version: "1.2.3"
generated_at: "2026-04-02T10:00:00Z"
generated_by: ai

server_aliases:
  - atlassian

command_shortcuts:
  - jira
  - confluence

commands:
  jira:
    _description: "JIRA project management"
    issue:
      _description: "Issue operations"
      create:
        _tool: jira_create_issue
        _description: "Create a new JIRA issue"
        _examples:
          - "mcp2cli mcp-atlassian jira issue create --project-key INFRA --summary 'Fix memory leak' --issue-type Task"
          - "mcp2cli mcp-atlassian jira issue create --project-key DEV --summary 'Add login' --issue-type Story --assignee john@example.com"
      get:
        _tool: jira_get_issue
        _description: "Get issue details by key"
        _examples:
          - "mcp2cli mcp-atlassian jira issue get --issue-key INFRA-1234"
      search:
        _tool: jira_search
        _description: "Search issues using JQL"
        _examples:
          - "mcp2cli mcp-atlassian jira issue search --jql 'project=INFRA AND status=Open'"
      update:
        _tool: jira_update_issue
        _description: "Update an existing issue"
      delete:
        _tool: jira_delete_issue
        _description: "Delete an existing issue"
      transition:
        _tool: jira_transition_issue
        _description: "Transition issue to a new status"
      link:
        _tool: jira_create_issue_link
        _description: "Create a link between two issues"
      comment:
        _description: "Issue comment operations"
        add:
          _tool: jira_add_comment
          _description: "Add a comment to an issue"
        edit:
          _tool: jira_edit_comment
          _description: "Edit an existing comment"
      watcher:
        _description: "Issue watcher operations"
        add:
          _tool: jira_add_watcher
          _description: "Add a watcher to an issue"
        remove:
          _tool: jira_remove_watcher
          _description: "Remove a watcher from an issue"
        list:
          _tool: jira_get_issue_watchers
          _description: "List watchers of an issue"
      worklog:
        _description: "Issue worklog operations"
        add:
          _tool: jira_add_worklog
          _description: "Add a worklog entry"
        list:
          _tool: jira_get_worklog
          _description: "Get worklog entries"
    sprint:
      _description: "Sprint operations"
      create:
        _tool: jira_create_sprint
        _description: "Create a new sprint"
      update:
        _tool: jira_update_sprint
        _description: "Update sprint details"
      list:
        _tool: jira_get_sprints_from_board
        _description: "List sprints for a board"
      issues:
        _tool: jira_get_sprint_issues
        _description: "Get issues in a sprint"
      add-issues:
        _tool: jira_add_issues_to_sprint
        _description: "Add issues to a sprint"
    board:
      _description: "Agile board operations"
      list:
        _tool: jira_get_agile_boards
        _description: "List agile boards"
      issues:
        _tool: jira_get_board_issues
        _description: "Get issues from a board"
    project:
      _description: "Project operations"
      list:
        _tool: jira_get_all_projects
        _description: "List all accessible projects"
      issues:
        _tool: jira_get_project_issues
        _description: "Get all issues in a project"
      components:
        _tool: jira_get_project_components
        _description: "Get project components"
      versions:
        _tool: jira_get_project_versions
        _description: "Get project fix versions"
    version:
      _description: "Version operations"
      create:
        _tool: jira_create_version
        _description: "Create a new fix version"
      batch-create:
        _tool: jira_batch_create_versions
        _description: "Batch create multiple versions"
    field:
      _description: "Field operations"
      search:
        _tool: jira_search_fields
        _description: "Search fields by keyword"
      options:
        _tool: jira_get_field_options
        _description: "Get allowed options for a field"
    link-type:
      _description: "Issue link type operations"
      list:
        _tool: jira_get_link_types
        _description: "List available link types"
  confluence:
    _description: "Confluence wiki operations"
    page:
      _description: "Page operations"
      get:
        _tool: confluence_get_page
        _description: "Get page content by ID or title"
        _examples:
          - "mcp2cli mcp-atlassian confluence page get --page-id 123456789"
          - "mcp2cli mcp-atlassian confluence page get --title 'Meeting Notes' --space-key TEAM"
      create:
        _tool: confluence_create_page
        _description: "Create a new page"
      update:
        _tool: confluence_update_page
        _description: "Update page content"
      delete:
        _tool: confluence_delete_page
        _description: "Delete a page"
      move:
        _tool: confluence_move_page
        _description: "Move a page to a new parent or space"
      children:
        _tool: confluence_get_page_children
        _description: "Get child pages of a page"
      history:
        _tool: confluence_get_page_history
        _description: "Get a historical version of a page"
      diff:
        _tool: confluence_get_page_diff
        _description: "Get diff between two page versions"
      views:
        _tool: confluence_get_page_views
        _description: "Get page view statistics"
      images:
        _tool: confluence_get_page_images
        _description: "Get all images from a page"
    search:
      _tool: confluence_search
      _description: "Search Confluence content"
      _examples:
        - "mcp2cli mcp-atlassian confluence search --query 'project documentation'"
    comment:
      _description: "Comment operations"
      list:
        _tool: confluence_get_comments
        _description: "Get comments for a page"
      add:
        _tool: confluence_add_comment
        _description: "Add a comment to a page"
      reply:
        _tool: confluence_reply_to_comment
        _description: "Reply to an existing comment"
    label:
      _description: "Label operations"
      list:
        _tool: confluence_get_labels
        _description: "Get labels for content"
      add:
        _tool: confluence_add_label
        _description: "Add a label to content"
    attachment:
      _description: "Attachment operations"
      list:
        _tool: confluence_get_attachments
        _description: "List attachments for content"
      upload:
        _tool: confluence_upload_attachment
        _description: "Upload an attachment"
      batch-upload:
        _tool: confluence_upload_attachments
        _description: "Upload multiple attachments"
      download:
        _tool: confluence_download_attachment
        _description: "Download an attachment"
      download-all:
        _tool: confluence_download_content_attachments
        _description: "Download all attachments for content"
      delete:
        _tool: confluence_delete_attachment
        _description: "Delete an attachment"
    user:
      _description: "User operations"
      search:
        _tool: confluence_search_user
        _description: "Search Confluence users"
```

## Format Key Points

1. **Top-level metadata**: `server`, `generated_at`, `generated_by`, `server_aliases`, `command_shortcuts`
2. **commands tree**: Nested YAML dictionary; keys prefixed with `_` are metadata, others are subcommands
3. **Leaf nodes**: Must have `_tool` and `_description`, optionally `_examples`
4. **Intermediate nodes**: Only have `_description`; remaining keys are child nodes
5. **Single-tool operations like search**: Can be placed directly under the parent group without an extra resource layer
