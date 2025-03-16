"""
Strategy pattern for different burndown calculation algorithms.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from models.Issue import Issue

class BurndownAlgorithm(ABC):
    """
    Abstract base class for burndown calculation algorithms.
    """
    @abstractmethod
    def calculate_burndown(self, story_data, date_range, sprint_name):
        """
        Calculate burndown data for the given stories, date range, and sprint.
        
        Args:
            story_data (dict): Dictionary mapping story IDs to their data
            date_range (list): List of dates to calculate burndown for
            sprint_name (str): Name of the sprint to filter by
            
        Returns:
            list: List of burndown data points
        """
        pass
        
    def _is_closed_as_of(self, task, date):
        """
        Check if a task was closed as of a certain date and not reopened.
        
        Args:
            task (dict): Task data
            date (datetime): Date to check
            
        Returns:
            bool: True if the task was closed as of the date, False otherwise
        """
        if not task or not task.get("closed") or not task.get("closedAt"):
            return False
            
        # Create proper date objects and normalize both to midnight UTC
        closed_date = datetime.fromisoformat(task["closedAt"].replace("Z", "+00:00"))
        closed_date = closed_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
        # Make sure we're comparing dates at the same time (midnight)
        compare_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            
        if closed_date > compare_date:
            return False
            
        # Check if it was reopened after being closed
        if self._was_reopened_after(task, compare_date):
            return False
            
        return True
        
    def _was_reopened_after(self, task, date):
        """
        Check if a task was reopened after a certain date.
        
        Args:
            task (dict): Task data
            date (datetime): Date to check
            
        Returns:
            bool: True if the task was reopened after the date, False otherwise
        """
        if not task or not task.get("timelineItems") or not task["timelineItems"].get("nodes"):
            return False
            
        last_event = None
            
        # Normalize the comparison date to midnight
        compare_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            
        # Loop through timeline events to find the last event before the given date
        for event in task["timelineItems"]["nodes"]:
            if not event or not event.get("createdAt"):
                continue
                
            event_date = datetime.fromisoformat(event["createdAt"].replace("Z", "+00:00"))
            event_date = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
                
            if event_date <= compare_date:
                last_event = event
                
        # If the last event is a reopened event, the task was reopened
        return last_event and last_event.get("__typename") == "ReopenedEvent"


class StoryPercentageAlgorithm(BurndownAlgorithm):
    """
    Algorithm 1: Stories with percentage-based completion.
    
    This algorithm calculates burndown based on:
    - Total story points from all stories
    - Percentage completion based on sub-tasks completion status
    """
    def calculate_burndown(self, story_data, date_range, sprint_name):
        """
        Calculate burndown using the story percentage algorithm.
        
        Args:
            story_data (dict): Dictionary mapping story IDs to their data
            date_range (list): List of dates to calculate burndown for
            sprint_name (str): Name of the sprint to filter by
            
        Returns:
            list: List of burndown data points
        """
        try:
            # Calculate total story points
            total_points = 0
            story_points = {}
            
            # Process each story
            for story_id, story_content in story_data.items():
                if not story_content:
                    continue
                    
                # Get story info
                story_info = story_content.get("__story_data", {})
                if not story_info or not story_info.get("Estimation"):
                    continue
                    
                # Skip if not in the selected sprint
                if story_info.get("Sprint") != sprint_name:
                    continue
                    
                # Add to total points
                total_points += story_info["Estimation"]
                
                # Store story information
                tasks = {}
                for task_id, task in story_content.items():
                    if task_id != "__story_data" and task:
                        tasks[task_id] = task
                
                story_points[story_id] = {
                    "id": story_id,
                    "title": story_info.get("title", "Unknown"),
                    "estimation": story_info["Estimation"],
                    "subTasks": (story_info.get("subIssuesSummary", {}).get("total", 0) or len(tasks)),
                    "completedTasks": story_info.get("subIssuesSummary", {}).get("completed", 0),
                    "tasks": tasks
                }
            
            # If no points, default to 100 to show something
            if total_points == 0:
                total_points = 100
                
            # Calculate burndown for each date
            burndown_data = []
            
            for date in date_range:
                remaining_points = total_points
                completed_stories_info = []
                
                # Process each story
                for story_id, story in story_points.items():
                    # Calculate completed tasks as of this date
                    completed_count = 0
                    
                    for task_id, task in story["tasks"].items():
                        if self._is_closed_as_of(task, date):
                            completed_count += 1
                            
                    # Calculate percentage completed
                    percent_complete = 0
                    if story["subTasks"] > 0:
                        percent_complete = (completed_count / story["subTasks"]) * 100
                        
                    # Calculate points burned
                    points_burned = story["estimation"] * (percent_complete / 100)
                    remaining_points -= points_burned
                    
                    # Record story information
                    completed_stories_info.append({
                        "id": story["id"],
                        "title": story["title"],
                        "percentComplete": percent_complete,
                        "burnedPoints": points_burned,
                        "estimation": story["estimation"],
                        "completedTasks": completed_count,
                        "totalTasks": story["subTasks"]
                    })
                
                burndown_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "remainingPoints": max(0, remaining_points),
                    "totalPoints": total_points,
                    "completedStoriesInfo": completed_stories_info
                })
                
            return burndown_data
            
        except Exception as e:
            print(f"Error in StoryPercentageAlgorithm: {e}")
            return []
            

class TaskBasedAlgorithm(BurndownAlgorithm):
    """
    Algorithm 2: Task-based burndown.
    
    This algorithm calculates burndown based on:
    - Tasks' individual estimations
    - If tasks don't have estimations, they inherit proportional points from their parent story
    """
    def calculate_burndown(self, story_data, date_range, sprint_name):
        """
        Calculate burndown using the task-based algorithm.
        
        Args:
            story_data (dict): Dictionary mapping story IDs to their data
            date_range (list): List of dates to calculate burndown for
            sprint_name (str): Name of the sprint to filter by
            
        Returns:
            list: List of burndown data points
        """
        try:
            # Collect all tasks with their estimations
            tasks_info = {}
            total_points = 0
            
            # Process each story
            for story_id, story_content in story_data.items():
                if not story_content:
                    continue
                
                # Skip if no story data
                if not story_content.get("__story_data"):
                    continue
                    
                story_info = story_content["__story_data"]
                
                # Skip if not in the selected sprint
                if story_info.get("Sprint") != sprint_name:
                    continue
                    
                story_estimation = story_info.get("Estimation", 0)
                
                # Get all tasks for this story
                tasks = {}
                for task_id, task in story_content.items():
                    if task_id != "__story_data" and task:
                        tasks[task_id] = task
                        
                task_count = len(tasks)
                
                # Calculate points per task
                points_per_task = story_estimation / task_count if task_count > 0 else 0
                
                # Process each task
                for task_id, task in tasks.items():
                    task_estimation = task.get("Estimation") or points_per_task
                    
                    # Store task info
                    tasks_info[task_id] = {
                        "id": task_id,
                        "title": task.get("title", "Unknown"),
                        "parentId": story_id,
                        "parentTitle": story_info.get("title", "Unknown"),
                        "createdAt": task.get("createdAt"),
                        "closedAt": task.get("closedAt"),
                        "closed": task.get("closed", False),
                        "timelineItems": task.get("timelineItems", {"nodes": []}),
                        "estimation": task_estimation
                    }
                    
                    total_points += task_estimation
                    
            # If no points, default to 100 to show something
            if total_points == 0:
                total_points = 100
                
            # Calculate burndown for each date
            burndown_data = []
            
            for date in date_range:
                remaining_points = 0
                open_tasks_info = []
                
                # Process each task
                for task_id, task in tasks_info.items():
                    # Parse createdAt to datetime
                    task_created_at = datetime.fromisoformat(task["createdAt"].replace("Z", "+00:00")) if task["createdAt"] else datetime.now()
                    task_created = task_created_at <= date
                    
                    # Check if the task is open on this date (considering reopened status)
                    task_open = not self._is_closed_as_of(task, date)
                    
                    # If task is created and still open on this date, add its points
                    if task_created and task_open:
                        remaining_points += task["estimation"]
                        open_tasks_info.append({
                            "id": task["id"],
                            "title": task["title"],
                            "parentId": task["parentId"],
                            "parentTitle": task["parentTitle"],
                            "estimation": task["estimation"]
                        })
                        
                burndown_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "remainingPoints": remaining_points,
                    "totalPoints": total_points,
                    "openTasksInfo": open_tasks_info
                })
                
            return burndown_data
            
        except Exception as e:
            print(f"Error in TaskBasedAlgorithm: {e}")
            return []
