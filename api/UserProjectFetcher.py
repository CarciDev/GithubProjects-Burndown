"""
Project data fetcher from GitHub API.
"""
import json
from api.GitHubClient import GitHubClient
from config.configuration import Configuration

class UserProjectFetcher:
    """
    Fetches project data from GitHub API for a specific User.
    """
    def __init__(self):
        self.github_client = GitHubClient()
        
    def fetch_project_data(self, save_to_file=True):
        all_items = self.github_client.fetch_paginated_query(
            create_query_func=self._create_paginated_query,
            process_page_func=self._extract_nodes_from_page
        )
        
        # CHANGED: Updated key name to "user" to match the source
        complete_result = {
            "user": {
                "projectV2": {
                    "items": {
                        "nodes": all_items
                    }
                }
            }
        }
        
        if save_to_file:
            with open('result.json', 'w') as json_file:
                json.dump(complete_result, json_file, indent=4)
                
        return complete_result
        
    def _create_paginated_query(self, cursor=None):
        after_param = f'after: "{cursor}"' if cursor else "after: null"
        
        # CHANGED: Replaced organization(...) with user(login: ...)
        return f"""
        {{
          user(login: "{Configuration.GITHUB_USERNAME}") {{
            projectV2(number: {Configuration.PROJECT_NUMBER}) {{
              items(first: 100, {after_param}) {{
                nodes {{
                  type
                  content {{
                    ... on Issue {{
                      id
                      title
                      state
                      createdAt
                      closed
                      closedAt
                      issueType {{ name }}
                      parent {{ id title }}
                      labels(first: 10) {{
                        nodes {{ name }}
                      }}
                      timelineItems(first: 100, itemTypes: [CLOSED_EVENT, REOPENED_EVENT]) {{
                        nodes {{
                          __typename
                          ... on ClosedEvent {{
                            createdAt
                            actor {{ login }}
                          }}
                          ... on ReopenedEvent {{
                            createdAt
                            actor {{ login }}
                          }}
                        }}
                      }}
                      subIssues(first: 100) {{
                        nodes {{ id title }}
                      }}
                      subIssuesSummary {{
                        completed
                        percentCompleted
                        total
                      }}
                    }}
                  }}
                  fieldValues(first: 100) {{
                    nodes {{
                      ... on ProjectV2ItemFieldIterationValue {{ title }}
                      ... on ProjectV2ItemFieldMilestoneValue {{
                        milestone {{ title }}
                      }}
                      ... on ProjectV2ItemFieldNumberValue {{ number }}
                    }}
                  }}
                }}
                pageInfo {{
                  hasNextPage
                  endCursor
                }}
              }}
            }}
          }}
        }}
        """
        
    def _extract_nodes_from_page(self, page_result):
        # CHANGED: Updated path from "organization" to "user"
        try:
            return page_result["user"]["projectV2"]["items"]["nodes"]
        except (KeyError, TypeError):
            return []