"""
Main entry point for the burndown chart generator.
"""
import json
import os
import traceback
from api.ProjectFetcher import ProjectFetcher
from data.IssueMapper import IssueMapper
from visualization.BurndownChart import BurndownChart

def main():
    """
    Main function to run the burndown chart generator.
    """
    print("Starting burndown chart generator...")
    
    # Step 1: Fetch project data from GitHub
    try:
        print("Fetching project data from GitHub...")
        project_fetcher = ProjectFetcher()
        project_data = project_fetcher.fetch_project_data(save_to_file=True)
        print("Project data fetched successfully.")
    except Exception as e:
        print(f"Error fetching project data: {e}")
        # Try to load from existing file if available
        try:
            print("Trying to load project data from existing file...")
            with open('result.json', 'r') as f:
                project_data = json.load(f)
            print("Project data loaded from file.")
        except Exception as load_error:
            print(f"Error loading project data from file: {load_error}")
            return
    
    # Step 2: Map raw data to domain models
    try:
        print("Mapping project data to domain models...")
        issues, story_to_tasks = IssueMapper.map_raw_data_to_models(project_data)
        print(f"Mapped {len(issues)} issues and {len(story_to_tasks)} stories.")
    except Exception as e:
        print(f"Error mapping project data: {e}")
        traceback.print_exc()  # Print detailed traceback
        return
    
    # Step 3: Generate burndown chart
    try:
        print("Generating burndown chart...")
        # Get issue dictionaries that can be serialized to JSON
        serializable_story_to_tasks = {}
        for story_id, story_data in story_to_tasks.items():
            serializable_story_to_tasks[story_id] = {}
            
            # Handle __story_data
            if "__story_data" in story_data:
                story_obj = story_data["__story_data"]
                if hasattr(story_obj, '__dict__'):
                    # For Issue objects
                    serializable_story = {
                        "id": story_obj.id,
                        "title": story_obj.title,
                        "Sprint": story_obj.sprint,
                        "Estimation": story_obj.estimation,
                        "subIssuesSummary": story_obj.sub_issues_summary
                    }
                    serializable_story_to_tasks[story_id]["__story_data"] = serializable_story
                else:
                    # For dictionaries
                    serializable_story_to_tasks[story_id]["__story_data"] = story_data["__story_data"]
            
            # Handle tasks
            for task_id, task in story_data.items():
                if task_id != "__story_data":
                    if hasattr(task, '__dict__'):
                        # For Issue objects
                        serializable_task = {
                            "id": task.id,
                            "title": task.title,
                            "closed": task.closed,
                            "closedAt": task.closed_at.isoformat() if task.closed_at else None,
                            "Estimation": task.estimation,
                            "timelineItems": task.timeline_items
                        }
                        serializable_story_to_tasks[story_id][task_id] = serializable_task
                    else:
                        # For dictionaries
                        serializable_story_to_tasks[story_id][task_id] = task
        
        chart_generator = BurndownChart(serializable_story_to_tasks)
        output_path = chart_generator.generate_interactive_html("sprint_burndown.html")
        print(f"Burndown chart generated successfully: {output_path}")
        
        # Open the chart in the default browser if possible
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(output_path)}")
        except Exception as browser_error:
            print(f"Note: Could not open the chart in browser: {browser_error}")
    except Exception as e:
        print(f"Error generating burndown chart: {e}")
        traceback.print_exc()  # Print detailed traceback
        return
    
    print("Done!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled exception in main: {e}")
        traceback.print_exc()