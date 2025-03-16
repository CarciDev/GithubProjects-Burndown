"""
Utilities for data structure manipulations.
"""

class DataStructureUtils:
    """
    Utilities for working with data structures.
    """
    @staticmethod
    def restructure_data(story_data):
        """
        Restructure data to ensure stories and tasks are in the expected format.
        
        Args:
            story_data (dict): Dictionary mapping story IDs to their data
            
        Returns:
            dict: Restructured data with stories and tasks
        """
        restructured_data = {}
        
        for story_id, story in story_data.items():
            # Create story entry with __story_data
            restructured_data[story_id] = {
                "__story_data": story
            }
            
        return restructured_data
        
    @staticmethod
    def safely_get_nested_value(data_dict, *keys, default=None):
        """
        Safely get a nested value from a dictionary.
        
        Args:
            data_dict (dict): Dictionary to get the value from
            *keys: Keys to access the nested value
            default: Default value to return if the key path doesn't exist
            
        Returns:
            any: The value at the key path, or the default value
        """
        current = data_dict
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current
        
    @staticmethod
    def extract_labels(labels_dict):
        """
        Extract label names from a labels dictionary.
        
        Args:
            labels_dict (dict): Dictionary containing label nodes
            
        Returns:
            list: List of label names
        """
        labels = []
        if isinstance(labels_dict, dict) and "nodes" in labels_dict:
            for label in labels_dict["nodes"]:
                if isinstance(label, dict) and "name" in label:
                    labels.append(label["name"])
        return labels
        
    @staticmethod
    def filter_issues_by_sprint(issues, sprint_name):
        """
        Filter issues by sprint name.
        
        Args:
            issues (dict): Dictionary of issues
            sprint_name (str): Sprint name to filter by
            
        Returns:
            dict: Filtered dictionary of issues
        """
        return {
            issue_id: issue for issue_id, issue in issues.items()
            if issue.get("Sprint") == sprint_name
        }
        
    @staticmethod
    def count_issues_by_type(issues):
        """
        Count issues by type.
        
        Args:
            issues (dict): Dictionary of issues
            
        Returns:
            dict: Dictionary with counts by type
        """
        counts = {}
        for issue in issues.values():
            if isinstance(issue, dict) and "issueType" in issue and isinstance(issue["issueType"], dict):
                issue_type = issue["issueType"].get("name")
                if issue_type:
                    counts[issue_type] = counts.get(issue_type, 0) + 1
        return counts
