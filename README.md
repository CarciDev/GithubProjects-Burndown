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

## Burndown Algorithms

### Algorithm 1: Story Percentage

Uses story estimations with percentage completion based on sub-tasks. As tasks are completed, the story burns down proportionally.

### Algorithm 2: Task-Based

Focuses only on task estimations. If tasks don't have direct estimations, they inherit proportional points from their parent story.

## Algorithm 3 (Unavailable yet): State based

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
