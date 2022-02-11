import pytest
import urllib3
from urllib.parse import urlencode, quote
import argparse
from src.md2jira import Checklist, ChecklistItemStatus, MD2Jira, Issue, IssueType

pytest.args = argparse.ArgumentParser()
pytest.args.JIRA_PROJECT_KEY = 'DRT'
pytest.issue = Issue(
    IssueType.Story, 
    '', 
    'checklist test ticket', 
    'description has `TEST`',
    '# Default Checklist\n* [done] Watch Frozen 2\n* [done] Dry Tears\n* [in progress] Walk in circles\n* [open] Rewatch Frozen 2\n'
)

class TestMD2JIRA:
    def test_create(self):
        md2jira    = MD2Jira(pytest.args)
        issue      = pytest.issue
        issue_data = md2jira.prepare_issue(issue)
        result     = md2jira.create_issue(issue, issue_data)
        if result.key != '':
            pytest.issue     = result
            pytest.issue_key = result.key
        assert result != None
        assert type(result) == Issue
        assert result.type == IssueType.Story
        assert result.key != ''

    def test_read(self):
        md2jira    = MD2Jira(pytest.args)
        result     = md2jira.read_issue(pytest.issue_key)
        assert result != None
        assert type(result) == Issue
        assert result.type == IssueType.Story
        assert result.key != ''
        assert result.key == pytest.issue_key
        assert result.summary == pytest.issue.summary
        assert type(result.checklist) is Checklist
        assert result.checklist.items is not None
        assert len(result.checklist.items) == 4
        sum_open        = 0
        sum_in_progress = 0
        sum_done        = 0
        for i in result.checklist.items: 
            status = ChecklistItemStatus(i.status)
            if status == ChecklistItemStatus.OPEN:
                sum_open += 1
            if status == ChecklistItemStatus.IN_PROGRESS:
                sum_in_progress += 1
            if status == ChecklistItemStatus.DONE:
                sum_done += 1
        assert sum_open == 1
        assert sum_in_progress == 1
        assert sum_done == 2

    def test_delete(self):
        md2jira    = MD2Jira(pytest.args)
        issue      = Issue(IssueType.Story, pytest.issue_key)
        result     = md2jira.delete_issue(issue)
        assert type(result) == urllib3.response.HTTPResponse
        assert result.reason == 'No Content'
        assert result.status == 204