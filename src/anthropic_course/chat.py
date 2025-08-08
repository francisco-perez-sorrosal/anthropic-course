from typing import Any, Callable, TYPE_CHECKING
from anthropic_course.conversation import Conversation
from anthropic import NOT_GIVEN, NotGiven
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
import loguru
import typer

from anthropic_course.tools import add_duration_to_datetime, add_duration_to_datetime_schema, create_tool, get_current_datetime, get_current_datetime_schema, set_reminder, set_reminder_schema

if TYPE_CHECKING:
    from anthropic_course.tools import Tool

logger = loguru.logger


class Chat:
    def __init__(self, model:str = "claude-3-5-haiku-20241022", max_tokens:int = 10, system_msg:str | NotGiven = NOT_GIVEN):
        self.conversation = Conversation(model=model, max_tokens=max_tokens, system_msg=system_msg)        
        self.console = Console()
        self.console.print(Panel(f"I'm {model} and I'm limited to Max tokens: {max_tokens}"))

    def run(self, temperature:float = 0.0, prefill_text:str | None = None, stop_sequences=["```"], tools:list["Tool"] = []):
        while True:
            try:
                self.console.print(Rule("[bold blue]User[/bold blue]"))
                user_input = input("> ")
                # console.print(f"> {user_input}")
                message, text = self.conversation.chat(role="user", 
                                                       text=user_input, 
                                                       prefill_text=prefill_text, 
                                                       temperature=temperature, 
                                                       streaming=True, 
                                                       stop_sequences=stop_sequences,
                                                       tools=tools)
                

                self.console.print(Rule("[bold blue]Assistant[/bold blue]"))
                self.console.print(text)
                # self.console.print(self.conversation)
            except KeyboardInterrupt:
                logger.info("Ctrl+C pressed. Exiting...")
                break

def main(
    model: str = typer.Option("claude-3-5-haiku-20241022", help="The model to use for the chat"),
    max_tokens: int = typer.Option(10, help="The maximum number of tokens to use for the chat"),
    system_msg: str = typer.Option(NOT_GIVEN, help="The system message to use for the chat"),
):
    chat = Chat(model=model, max_tokens=max_tokens, system_msg=system_msg)
    
    get_current_datetime_tool = create_tool(
        name="get_current_datetime",
        description="Get the current date and time formatted according to the specified format string. Uses Python strftime format codes (e.g., %Y for year, %m for month, %d for day, %H for hour, %M for minute, %S for second).",
        function=get_current_datetime,
        input_schema=get_current_datetime_schema["input_schema"]
    )

    add_duration_to_datetime_tool = create_tool(
        name="add_duration_to_datetime",
        description="Adds a specified duration to a datetime string and returns the resulting datetime in a detailed format. This tool converts an input datetime string to a Python datetime object, adds the specified duration in the requested unit, and returns a formatted string of the resulting datetime. It handles various time units including seconds, minutes, hours, days, weeks, months, and years, with special handling for month and year calculations to account for varying month lengths and leap years. The output is always returned in a detailed format that includes the day of the week, month name, day, year, and time with AM/PM indicator (e.g., 'Thursday, April 03, 2025 10:30:00 AM').",
        function=add_duration_to_datetime,
        input_schema=add_duration_to_datetime_schema["input_schema"]
    )

    set_reminder_tool = create_tool(
        name="set_reminder",
        description="Creates a timed reminder that will notify the user at the specified time with the provided content. This tool schedules a notification to be delivered to the user at the exact timestamp provided. It should be used when a user wants to be reminded about something specific at a future point in time. The reminder system will store the content and timestamp, then trigger a notification through the user's preferred notification channels (mobile alerts, email, etc.) when the specified time arrives. Reminders are persisted even if the application is closed or the device is restarted. Users can rely on this function for important time-sensitive notifications such as meetings, tasks, medication schedules, or any other time-bound activities.",
        function=set_reminder,
        input_schema=set_reminder_schema["input_schema"]
    )
        
    chat.run(tools=[get_current_datetime_tool, add_duration_to_datetime_tool, set_reminder_tool])

if __name__ == "__main__":
    typer.run(main)
