"""
Issue model representing a GitHub issue.
"""
from models.IssueState import IssueState
from models.SubIssue import SubIssue
from datetime import datetime

class Issue:
    """
    Represents a project issue (story, feature, etc.) that may contain sub-issues.
    """
    def __init__(self, issue_id, title, state, created_at, closed_at=None, 
                 closed=False, issue_type=None, parent=None, labels=None, 
                 timeline_items=None, sub_issues=None, sub_issues_summary=None):
        """
        Initialize an Issue instance.
        
        Args:
            issue_id (str): Unique identifier for the issue
            title (str): Title of the issue
            state (str or IssueState): State of the issue (open or closed)
            created_at (str): ISO timestamp when the issue was created
            closed_at (str, optional): ISO timestamp when the issue was closed
            closed (bool, optional): Whether the issue is closed
            issue_type (dict, optional): Type of the issue (e.g., Feature, Task)
            parent (dict, optional): Parent issue information
            labels (list or dict, optional): List of label dictionaries or dict with nodes
            timeline_items (dict, optional): Timeline events for the issue
            sub_issues (dict, optional): Sub-issues contained in this issue
            sub_issues_summary (dict, optional): Summary of sub-issues status
        """
        self.id = issue_id
        self.title = title
        self.state = state if isinstance(state, IssueState) else IssueState.from_string(state)
        self.created_at = self._parse_datetime(created_at)
        self.closed_at = self._parse_datetime(closed_at) if closed_at else None
        self.closed = closed
        self.issue_type = issue_type or {}
        self.parent = parent
        self.labels = self._extract_labels(labels)
        self.timeline_items = timeline_items or {"nodes": []}
        self.sub_issues = sub_issues or {"nodes": []}
        self.sub_issues_summary = sub_issues_summary or {}
        
        # Additional properties
        self.milestone = None
        self.sprint = None
        self.estimation = None
        self._sub_issue_objects = []
        
    def _parse_datetime(self, datetime_str):
        """
        Parse an ISO format datetime string to a datetime object.
        
        Args:
            datetime_str (str): ISO format datetime string
            
        Returns:
            datetime or None: Parsed datetime object or None if parsing fails
        """
        try:
            return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError, TypeError):
            return None
            
    def _extract_labels(self, labels):
        """
        Extract label names from label objects.
        
        Args:
            labels (dict or list): Dictionary containing label nodes or list of labels
            
        Returns:
            list: List of label names
        """
        result = []
        
        # Handle the case where labels is a dict with nodes
        if isinstance(labels, dict) and "nodes" in labels:
            for label in labels["nodes"]:
                if isinstance(label, dict) and "name" in label:
                    result.append(label["name"])
        # Handle the case where labels is a list
        elif isinstance(labels, list):
            for label in labels:
                if isinstance(label, dict) and "name" in label:
                    result.append(label["name"])
                elif isinstance(label, str):
                    result.append(label)
                    
        return result
        
    def is_story(self):
        """
        Check if this issue is a story/feature.
        
        Returns:
            bool: True if this is a story, False otherwise
        """
        # Check if it has the 'story' label
        if "story" in [label.lower() for label in self.labels]:
            return True
            
        # Check if it's a Feature type without a parent
        if (isinstance(self.issue_type, dict) and 
            self.issue_type.get("name") == "Feature" and 
            self.parent is None):
            return True
            
        return False
        
    def is_task(self):
        """
        Check if this issue is a task/sub-issue.
        
        Returns:
            bool: True if this is a task, False otherwise
        """
        return (isinstance(self.issue_type, dict) and 
                self.issue_type.get("name") == "Task" and 
                self.parent is not None)
                
    def add_sub_issue(self, sub_issue):
        """
        Add a SubIssue object to this Issue.
        
        Args:
            sub_issue (SubIssue): The sub-issue to add
        """
        self._sub_issue_objects.append(sub_issue)
        
    def get_sub_issues(self):
        """
        Get all SubIssue objects associated with this Issue.
        
        Returns:
            list: List of SubIssue objects
        """
        return self._sub_issue_objects
        
    def update_from_field_values(self, field_values):
        """
        Update issue properties from field values.
        
        Args:
            field_values (list): List of field value dictionaries
        """
        for field_value in field_values:
            if isinstance(field_value, dict):
                if "milestone" in field_value and field_value["milestone"]:
                    self.milestone = field_value["milestone"].get("title") if isinstance(field_value["milestone"], dict) else None
                elif "title" in field_value and isinstance(field_value["title"], str) and "Sprint" in field_value["title"]:
                    self.sprint = field_value["title"]
                elif "number" in field_value:
                    try:
                        # Ensure estimation is converted to a float
                        self.estimation = float(field_value["number"]) if field_value["number"] is not None else None
                    except (ValueError, TypeError):
                        self.estimation = None
        
    def get_completion_percentage(self):
        """
        Get the completion percentage based on closed sub-issues.
        
        Returns:
            float: Percentage of completion (0-100)
        """
        # First try to get from sub_issues_summary
        if self.sub_issues_summary and "percentCompleted" in self.sub_issues_summary:
            try:
                return float(self.sub_issues_summary["percentCompleted"])
            except (ValueError, TypeError):
                pass
            
        # Calculate manually if not available or conversion failed
        total_sub_issues = len(self._sub_issue_objects)
        if total_sub_issues == 0:
            return 0.0
            
        closed_sub_issues = sum(1 for sub in self._sub_issue_objects if sub.closed)
        return (closed_sub_issues / total_sub_issues) * 100.0
        
    def __str__(self):
        return (f'Issue(\n'
                f'  id={self.id},\n'
                f'  title={self.title},\n'
                f'  state={self.state},\n'
                f'  created_at={self.created_at},\n'
                f'  closed={self.closed},\n'
                f'  closed_at={self.closed_at},\n'
                f'  issue_type={self.issue_type},\n'
                f'  parent={self.parent},\n'
                f'  labels={self.labels},\n'
                f'  milestone={self.milestone},\n'
                f'  sprint={self.sprint},\n'
                f'  estimation={self.estimation}\n'
                f')')
        
    def __repr__(self):
        return self.__str__()