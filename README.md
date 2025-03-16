# Sprint Burndown Generator

A tool for generating interactive burndown charts based on GitHub project data.

DISCLAMER: The architecture was provided by Claude.Ai. I provided a detailed pseudocode of the algorithm, and detailed functional goals. Due to the limit of time, I resorted to using Ai to speed up the release (I am taking 17.5 credits).

## Features

- Fetches project data from GitHub GraphQL API
- Maps raw data to domain models
- Calculates burndown using two different algorithms:
  - Story-based with percentage completion
  - Task-based burndown
- Generates interactive HTML visualizations with filtering capabilities
- Separates concerns into modular, maintainable code

## Project Structure

```
project/
├── config/
│   └── configuration.py              # Configuration settings
├── models/
│   ├── Issue.py                      # Core Issue model
│   ├── IssueState.py                 # Enum for issue states
│   ├── SubIssue.py                   # SubIssue model
│   └── DayOfWeek.py                  # Day of week utilities
├── api/
│   ├── GitHubClient.py               # GitHub API client
│   └── ProjectFetcher.py             # Project data fetcher
├── data/
│   ├── IssueMapper.py                # Maps raw API data to models
│   ├── DataProcessor.py              # Processes issues for burndown
│   └── AlgorithmStrategy.py          # Different burndown calculation algorithms
├── visualization/
│   ├── BurndownChart.py              # Chart generation logic
│   ├── HTMLGenerator.py              # HTML output generator
│   └── InteractiveComponents.py      # Interactive UI components
├── utils/
│   ├── DateUtils.py                  # Date handling utilities
│   └── DataStructureUtils.py         # Data structure utilities
└── main.py                           # Application entry point
```

## Getting Started

1. Configure GitHub token in `config/configuration.py`
2. Install requirements.txt in a .venv you can create.
3. Run with main.py -> outputs as `sprint_burndown.html`

## Todo: Known Bugs + Features

- [ ] Selecting the date on the burndown html might display the date off by 1. 
  - To fix: Select the next nearest date so it updates correctly on the graph.
- [ ] Algorithm 2 not tested.
- [ ] Algorithm 3 not implemented yet (API immature at this point).
- [ ] Need more testing on different repo's.
- [ ] Automatically fetch the date for the current iteration (and set it to default when loading the html doc)

## Burndown Algorithms

### Algorithm 1: Story Percentage

Uses story estimations with percentage completion based on sub-tasks. As tasks are completed, the story burns down proportionally.

### Algorithm 2: Task-Based

Focuses only on task estimations. If tasks don't have direct estimations, they inherit proportional points from their parent story.

### Algorithm 3 (Unavailable yet): State based

Depending on the state of a task within the pipeline (kanban), a percentage of completion is marked. This can reveal granular details and bottlenecks in the pipeline.

## Core Dependencies

- `gql`: GraphQL client for Python
- `plotly`: Interactive visualizations
- `tabulator`: JavaScript table library (included via CDN)

## Configuration

Update the following in `config/configuration.py`:

- `GITHUB_TOKEN_API`: Your GitHub API token
- `ORGANIZATION_NAME`: Your GitHub organization name
- `PROJECT_NUMBER`: Your GitHub project number
- `ISSUE_TYPE_STORY`: Issue type for stories (e.g., "Feature")
- `ISSUE_TYPE_TASK`: Issue type for tasks (e.g., "Task")

## My SOEN 390 Repository Configuration:

### Issue Types (In My Organization)
- Bug, and other types do not affect the burndown.
![image](https://github.com/user-attachments/assets/0ba7b938-eb56-48bc-9a5f-600e28ac27db)

### Project Tags/Attributes:
1. Go to your GitHub Project view, and access settings:

![image](https://github.com/user-attachments/assets/72a3534b-48e6-4b74-8876-3580e5b6589d)

2. Ensure that the attributes are as follows:

![image](https://github.com/user-attachments/assets/31ee31e9-b3ec-42ca-9e0e-130ec2fb0ca7)
- Sprints is not there by default, but **iterations** are. I renamed it (Field Name). I also created the sprint names to 'Sprint X', x being a number.

![image](https://github.com/user-attachments/assets/5d8e7b21-2e3d-4dde-8a6a-8d50632f7a74)

### Sample Story / Task

![image](https://github.com/user-attachments/assets/a301b834-bfc5-42ba-b61e-787bb4068994)

- Notice Feature in blue (Feature), and the sub issues are in yellow (Task).

![image](https://github.com/user-attachments/assets/3b2866a6-14b8-4d8c-9949-652b99c50083)

- When creating an issue or subissue, ensure that `Issue Type` is defined. Anything else is optional. 

