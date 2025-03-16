"""
Processes issue data for burndown chart generation.
"""
import datetime
import json
from data.IssueMapper import IssueMapper
from data.AlgorithmStrategy import StoryPercentageAlgorithm, TaskBasedAlgorithm
from config.configuration import Configuration

class DataProcessor:
    """
    Process issue data for burndown chart generation.
    """
    def __init__(self):
        """
        Initialize the data processor.
        """
        self.story_percentage_algorithm = StoryPercentageAlgorithm()
        self.task_based_algorithm = TaskBasedAlgorithm()
        
    def process_project_data(self, project_data):
        """
        Process raw project data into usable formats.
        
        Args:
            project_data (dict): Raw project data from API
            
        Returns:
            tuple: (Issues dict, Stories-to-tasks dict)
        """
        try:
            return IssueMapper.map_raw_data_to_models(project_data)
        except Exception as e:
            print(f"Error in process_project_data: {e}")
            # Return empty dictionaries as fallback
            return {}, {}
        
    def get_available_sprints(self, story_data):
        """
        Get a list of all available sprints/iterations in the data.
        
        Args:
            story_data (dict): Dictionary mapping story IDs to their data
            
        Returns:
            list: List of sprint/iteration names
        """
        try:
            # Get the configured iteration tag name (default to "Sprint")
            iteration_tag_name = getattr(Configuration, "ITERATION_TAG_NAME", "Sprint")
            print(f"Looking for iteration tag name: {iteration_tag_name}")
            
            # Set to store unique iteration values
            iterations = set()
            iteration_tag_found = False
            
            # For debugging, let's examine the first story in detail
            if story_data:
                first_story_id = next(iter(story_data))
                first_story = story_data[first_story_id]
                first_story_info = first_story.get("__story_data", {})
                print(f"First story data structure: {type(first_story_info).__name__}")
                
                if isinstance(first_story_info, dict):
                    print(f"First story keys: {list(first_story_info.keys())}")
                    # Try to print a few values to see their structure
                    for key in first_story_info:
                        if key in ["Sprint", "Iteration", "title", "id"]:
                            print(f"  {key}: {first_story_info[key]} (type: {type(first_story_info[key]).__name__})")
                else:
                    # If it's an object, try to get its attributes
                    print(f"First story attributes: {dir(first_story_info)}")
            
            # Check stories for iteration field
            for story_id, story in story_data.items():
                if not story:
                    continue
                    
                # Get the story info
                story_info = story.get("__story_data", {})
                
                # For debugging, print the first few story structures
                if isinstance(story_info, dict) and len(iterations) < 3:
                    print(f"Story {story_id} keys: {list(story_info.keys())}")
                
                # Handle various ways iteration might be stored
                iteration_value = None
                field_found = False
                
                # 1. Check if story_info is an object with attribute matching iteration_tag_name (case insensitive)
                if hasattr(story_info, 'sprint'):
                    iteration_value = story_info.sprint
                    field_found = True
                elif hasattr(story_info, iteration_tag_name.lower()):
                    iteration_value = getattr(story_info, iteration_tag_name.lower())
                    field_found = True
                
                # 2. Check if story_info is a dict with key matching iteration_tag_name (case insensitive)
                elif isinstance(story_info, dict):
                    # Look for exact match first
                    if iteration_tag_name in story_info:
                        iteration_value = story_info[iteration_tag_name]
                        field_found = True
                    else:
                        # Try case-insensitive match
                        for key in story_info:
                            if isinstance(key, str) and key.lower() == iteration_tag_name.lower():
                                iteration_value = story_info[key]
                                field_found = True
                                break
                
                # Add iteration value to set if it's valid (handle various types)
                if iteration_value is not None:
                    # Convert to string if not already
                    if isinstance(iteration_value, str):
                        iterations.add(iteration_value)
                        iteration_tag_found = True
                    elif isinstance(iteration_value, (int, float)):
                        # Convert numbers to strings
                        iterations.add(str(iteration_value))
                        iteration_tag_found = True
                    elif isinstance(iteration_value, dict) and 'title' in iteration_value:
                        # Handle nested dict with title
                        iterations.add(iteration_value['title'])
                        iteration_tag_found = True
                    else:
                        # Try to convert to string as a last resort
                        try:
                            iterations.add(str(iteration_value))
                            iteration_tag_found = True
                        except:
                            pass
                
                # Print debugging info for the first few items
                if len(iterations) <= 3 and field_found:
                    print(f"Found iteration value: {iteration_value} (type: {type(iteration_value).__name__})")
                    
            # If no iterations found, try searching for any field that might be an iteration
            if not iteration_tag_found:
                print("No standard iteration tags found, searching for potential iteration fields...")
                
                potential_tags = ["Iteration", "Sprint", "Cycle", "Release", "Milestone"]
                
                for story_id, story in story_data.items():
                    if not story:
                        continue
                        
                    story_info = story.get("__story_data", {})
                    
                    if isinstance(story_info, dict):
                        # Look for any keys that might indicate iterations
                        for key in story_info:
                            if isinstance(key, str) and any(tag.lower() in key.lower() for tag in potential_tags):
                                value = story_info[key]
                                if value is not None:
                                    try:
                                        # Convert value to string if not already
                                        str_value = str(value) if not isinstance(value, str) else value
                                        iterations.add(str_value)
                                        print(f"Found potential iteration field '{key}' with value: {str_value}")
                                    except:
                                        pass
            
            # If still no iterations found, return a default
            if not iterations:
                print("No iteration values found, using default")
                default_sprint = getattr(Configuration, "DEFAULT_SPRINT", "N/A")
                iterations.add(default_sprint)
                
            # Convert to sorted list, filtering out None values and empty strings
            iteration_list = [s for s in iterations if s is not None and s != ""]
            
            # Print all found iterations for debugging
            print(f"Found {len(iteration_list)} iteration values: {iteration_list}")
            
            # Sort iterations with special handling for Sprint/Iteration numbers
            try:
                # Try to sort by numeric part if the format is like "Sprint X" or "Iteration Y"
                def extract_number(s):
                    # Extract numeric part from strings like "Sprint 5" or "Iteration 3"
                    if not isinstance(s, str):
                        return s
                    
                    parts = s.split()
                    for part in parts:
                        try:
                            return int(part)
                        except ValueError:
                            pass
                    return s
                
                # Sort numerically if possible, otherwise lexicographically
                sorted_iterations = sorted(iteration_list, key=extract_number)
                return sorted_iterations
            except Exception as e:
                print(f"Error sorting iterations: {e}")
                # Fall back to simple sort
                return sorted(iteration_list)
        except Exception as e:
            print(f"Error in get_available_sprints: {e}")
            # Return default sprint as fallback
            default_sprint = getattr(Configuration, "DEFAULT_SPRINT", "N/A")
            return [default_sprint]
        
    def calculate_burndown(self, story_data, algorithm_type, start_date, end_date, sprint_name):
        """
        Calculate burndown data based on algorithm.
        
        Args:
            story_data (dict): Dictionary mapping story IDs to their data
            algorithm_type (int): 1 for story percentage, 2 for task-based
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            sprint_name (str): Name of the sprint to filter by
            
        Returns:
            list: List of burndown data points
        """
        try:
            # Convert string dates to Date objects and normalize to midnight
            try:
                start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            except (ValueError, TypeError):
                # Default to 30 days ago if date parsing fails
                start = datetime.datetime.now() - datetime.timedelta(days=30)
                start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            try:
                end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                end = end.replace(hour=0, minute=0, second=0, microsecond=0)
            except (ValueError, TypeError):
                # Default to today if date parsing fails
                end = datetime.datetime.now()
                end = end.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Generate array of dates between start and end (at midnight)
            date_range = []
            current_date = start
            while current_date <= end:
                # Create a new date object to avoid reference issues
                date_range.append(datetime.datetime(
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    0, 0, 0, 0
                ))
                current_date += datetime.timedelta(days=1)
                
            # Use the appropriate algorithm
            if algorithm_type == 1:
                return self.story_percentage_algorithm.calculate_burndown(
                    story_data, date_range, sprint_name
                )
            else:
                return self.task_based_algorithm.calculate_burndown(
                    story_data, date_range, sprint_name
                )
                
        except Exception as e:
            print(f"Error in calculate_burndown: {e}")
            return []