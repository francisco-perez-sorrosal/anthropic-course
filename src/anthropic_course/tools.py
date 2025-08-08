from datetime import datetime, timedelta
import json
from typing import Any, Dict, Callable, Union
import inspect
from loguru import logger
from pydantic import BaseModel, Field


class Tool(BaseModel):
    """
    A Pydantic model representing a tool with a Python function and its JSON schema.
    
    Attributes:
        name: The name of the tool
        description: Description of what the tool does
        function: The Python function to execute
        input_schema: JSON schema defining the expected input parameters
    """
    name: str = Field(..., description="The name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    function: Callable | None = Field(..., description="The Python function to execute")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema defining the expected input parameters")
    
    class Config:
        arbitrary_types_allowed = True  # Allow Callable type
    
    def to_anthropic_format(self) -> Dict[str, Any]:
        """
        Convert the tool to Anthropic's expected format for the API.
        
        Returns:
            Dict containing the tool in Anthropic's format
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }
    
    def execute(self, tool_request_params: Dict[str, Any]) -> Any:
        """
        Execute the tool function with the given request parameters.
        
        Args:
            tool_request_params: Dictionary containing the tool request parameters
            
        Returns:
            The result of executing the tool function
        """
        if self.function is None:
            logger.warning(f"Tool {self.name} has no associated function, returning None")
            return None
        
        if not self._validate_request_params(tool_request_params):
            raise ValueError(f"Invalid tool request for {self.name}")
        
        params = self._extract_parameters(tool_request_params)
        
        # Get function signature to filter parameters
        sig = inspect.signature(self.function)
        filtered_params = {}
        for param_name, param_value in params.items():
            if param_name in sig.parameters:
                filtered_params[param_name] = param_value
            else:
                logger.warning(f"Parameter {param_name} not in function signature!!!")
        
        # Execute the function
        return self.function(**filtered_params)
    
    def _validate_request_params(self, tool_request_params: Dict[str, Any]) -> bool:
        """
        Validate that a tool request matches the expected schema.
        
        Args:
            tool_request_params: The tool request containing input parameters
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(tool_request_params, dict):
            return False
        
        properties = self.input_schema.get("properties", {})
        required_fields = self.input_schema.get("required", [])
        
        for field in required_fields:
            if field not in tool_request_params:
                return False
        
        for field in tool_request_params:
            if field not in properties:
                return False
        
        return True
    
    def _extract_parameters(self, tool_request_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and validate parameters from a tool request, applying defaults where needed.
        
        Args:
            tool_request_params: The tool request containing input parameters
            
        Returns:
            Dict[str, Any]: The extracted parameters with defaults applied
        """
        properties = self.input_schema.get("properties", {})
        
        # Start with defaults
        params = {}
        for field_name, field_schema in properties.items():
            if "default" in field_schema:
                params[field_name] = field_schema["default"]
        
        # Override with provided values
        params.update(tool_request_params)
        
        logger.info(f"Params after update: {params}")
        
        return params

def create_tool(name: str, description: str, function: Callable | None, input_schema: Dict[str, Any]) -> Tool:
    """
    Create a Tool instance with the given parameters.
    
    Args:
        name: The name of the tool
        description: Description of what the tool does
        function: The Python function to execute
        input_schema: JSON schema defining the expected input parameters
        
    Returns:
        Tool: A new Tool instance
    """
    return Tool(
        name=name,
        description=description,
        function=function,
        input_schema=input_schema
    )

# Creating tools

def get_current_datetime(format:str = "%Y-%m-%d %H:%M:%S"):
    if format == "":
        raise ValueError("Format cannot be empty")
    return datetime.now().strftime(format)


get_current_datetime_schema = {
  "name": "get_current_datetime",
  "description": "Get the current date and time formatted according to the specified format string. Uses Python strftime format codes (e.g., %Y for year, %m for month, %d for day, %H for hour, %M for minute, %S for second).",
  "input_schema": {
    "type": "object",
    "properties": {
      "format": {
        "type": "string",
        "description": "The strftime format string to format the datetime. Common formats: '%Y-%m-%d %H:%M:%S' for '2024-01-15 14:30:00', '%Y-%m-%d' for '2024-01-15', '%H:%M:%S' for '14:30:00'. Cannot be empty.",
        "default": "%Y-%m-%d %H:%M:%S"
      }
    },
    "required": []
  }
}

def add_duration_to_datetime(
    datetime_str, duration=0, unit="days", input_format="%Y-%m-%d"
) -> str:
    date = datetime.strptime(datetime_str, input_format)

    match unit:
        case "seconds":
            new_date = date + timedelta(seconds=duration)
        case "minutes":
            new_date = date + timedelta(minutes=duration)
        case "hours":
            new_date = date + timedelta(hours=duration)
        case "days":
            new_date = date + timedelta(days=duration)
        case "weeks":
            new_date = date + timedelta(weeks=duration)
        case "months":
            month = date.month + duration
            year = date.year + month // 12
            month = month % 12
            if month == 0:
                month = 12
                year -= 1
            day = min(
                date.day,
                [
                    31,
                    29
                    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
                    else 28,
                    31,
                    30,
                    31,
                    30,
                    31,
                    31,
                    30,
                    31,
                    30,
                    31,
                ][month - 1],
            )
            new_date = date.replace(year=year, month=month, day=day)
        case "years":
            new_date = date.replace(year=date.year + duration)
        case _:
            raise ValueError(f"Unsupported time unit: {unit}")

    return new_date.strftime("%A, %B %d, %Y %I:%M:%S %p")


add_duration_to_datetime_schema = {
    "name": "add_duration_to_datetime",
    "description": "Adds a specified duration to a datetime string and returns the resulting datetime in a detailed format. This tool converts an input datetime string to a Python datetime object, adds the specified duration in the requested unit, and returns a formatted string of the resulting datetime. It handles various time units including seconds, minutes, hours, days, weeks, months, and years, with special handling for month and year calculations to account for varying month lengths and leap years. The output is always returned in a detailed format that includes the day of the week, month name, day, year, and time with AM/PM indicator (e.g., 'Thursday, April 03, 2025 10:30:00 AM').",
    "input_schema": {
        "type": "object",
        "properties": {
            "datetime_str": {
                "type": "string",
                "description": "The input datetime string to which the duration will be added. This should be formatted according to the input_format parameter.",
            },
            "duration": {
                "type": "number",
                "description": "The amount of time to add to the datetime. Can be positive (for future dates) or negative (for past dates). Defaults to 0.",
            },
            "unit": {
                "type": "string",
                "description": "The unit of time for the duration. Must be one of: 'seconds', 'minutes', 'hours', 'days', 'weeks', 'months', or 'years'. Defaults to 'days'.",
            },
            "input_format": {
                "type": "string",
                "description": "The format string for parsing the input datetime_str, using Python's strptime format codes. For example, '%Y-%m-%d' for ISO format dates like '2025-04-03'. Defaults to '%Y-%m-%d'.",
            },
        },
        "required": ["datetime_str"],
    },
}


def set_reminder(content, timestamp):
    print(
        f"----\nSetting the following reminder for {timestamp}:\n{content}\n----"
    )


set_reminder_schema = {
    "name": "set_reminder",
    "description": "Creates a timed reminder that will notify the user at the specified time with the provided content. This tool schedules a notification to be delivered to the user at the exact timestamp provided. It should be used when a user wants to be reminded about something specific at a future point in time. The reminder system will store the content and timestamp, then trigger a notification through the user's preferred notification channels (mobile alerts, email, etc.) when the specified time arrives. Reminders are persisted even if the application is closed or the device is restarted. Users can rely on this function for important time-sensitive notifications such as meetings, tasks, medication schedules, or any other time-bound activities.",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The message text that will be displayed in the reminder notification. This should contain the specific information the user wants to be reminded about, such as 'Take medication', 'Join video call with team', or 'Pay utility bills'.",
            },
            "timestamp": {
                "type": "string",
                "description": "The exact date and time when the reminder should be triggered, formatted as an ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SS) or a Unix timestamp. The system handles all timezone processing internally, ensuring reminders are triggered at the correct time regardless of where the user is located. Users can simply specify the desired time without worrying about timezone configurations.",
            },
        },
        "required": ["content", "timestamp"],
    },
}