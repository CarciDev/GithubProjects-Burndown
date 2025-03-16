"""
Configuration module for project settings.
"""

class Configuration:
    # GitHub API settings
    GITHUB_TOKEN_API = ""  # GitHub CLASSIC API token
    ORGANIZATION_NAME = "SOEN-390-W2025"
    PROJECT_NUMBER = 1  # Project number in GitHub
    REPOSITORY_NAME = "SOEN-390"
    GITHUB_USERNAME = "CarciDev"
    
    # Issue type settings
    ISSUE_TYPE_STORY = "Feature"
    ISSUE_TYPE_TASK = "Task"
    
    # Tag settings
    ITERATION_TAG_NAME = "Sprint"  # Tag name for iterations
    DEFAULT_SPRINT = "Sprint 4"    # Default sprint to display
    
    # Pipeline settings (kanban board columns with weighted completion)
    PIPELINE = [
        ("No Status", 0.0),
        ("Product Backlog", 0.0),
        ("Sprint Backlog", 0.0),
        ("In Progress", 0.30),
        ("Technical Review and Testing", 0.60),
        ("Done", 1.0)
    ]
    
    # Algorithm settings
    USE_WEIGHTED_ALGORITHM = True  # Whether to use the weighted algorithm
    
    # GitHub GraphQL API endpoint
    GITHUB_GRAPHQL_API = "https://api.github.com/graphql"
    
    @classmethod
    def get_pipeline_weight(cls, status):
        """
        Get the weight for a status in the pipeline.
        
        Args:
            status (str): The status to get the weight for
            
        Returns:
            float: The weight for the status, or 0.0 if not found
        """
        for pipeline_status, weight in cls.PIPELINE:
            if pipeline_status.lower() == status.lower():
                return weight
        return 0.0
    
    @classmethod
    def get_auth_headers(cls):
        """
        Get the authentication headers for GitHub API requests.
        
        Returns:
            dict: Headers dictionary with authentication token
        """
        return {
            "Authorization": f"Bearer {cls.GITHUB_TOKEN_API}", 
            "GraphQL-Features": "issue_types"
        }
