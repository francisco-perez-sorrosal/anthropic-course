"""Main CLI application for anthropic-course."""

import os

import typer
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from anthropic_course.dataset_generator import DatasetGenerator
from anthropic_course.eval_pipeline import EvalPipeline
from anthropic_course.grader import Grader

from .logger import get_logger
from . import __version__

# Load environment variables
load_dotenv()

# Initialize Typer app and Rich console
app = typer.Typer(
    name="anthropic-course",
    help="A simple Python toy/POC project",
    add_completion=False,
)
console = Console()

# Get configured logger
logger = get_logger()


class AppConfig(BaseModel):
    """Application configuration model."""

    debug: bool = Field(default=False, description="Enable debug mode")
    app_name: str = Field(default="Anthropic Course", description="Application name")
    version: str = Field(default=__version__, description="Application version")

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create AppConfig from environment variables."""
        return cls(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            app_name=os.getenv("APP_NAME", "Anthropic Course"),
            version=os.getenv("VERSION", __version__),
        )


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
) -> None:
    """Main application entry point with colorful logging demonstration."""

    # Load configuration
    config = AppConfig.from_env()
    if debug:
        config.debug = True

    # Update logger level if debug is enabled
    if config.debug:
        from .logger import LogConfig, LogLevel, configure_logger

        debug_config = LogConfig(level=LogLevel.DEBUG)
        configure_logger(debug_config)
        # Get fresh logger instance after reconfiguration
        from .logger import get_logger

        global logger
        logger = get_logger()

    # Display startup banner
    banner_text = Text(f"🚀 {config.app_name}", style="bold blue")
    banner_text.append("\n✨ Simple Toy/POC Project", style="italic green")
    banner_text.append(f"\n📦 Version: {config.version}", style="yellow")

    console.print(Panel(banner_text, border_style="blue"))

    # Demonstrate all log levels with colors
    logger.debug("🔍 Debug mode enabled - showing detailed information")
    logger.info("ℹ️  Application started successfully")
    logger.warning("⚠️  This is a warning message")
    logger.error("❌ This is an error message")
    logger.critical("🚨 This is a critical error!")

    # Fun info messages with rich formatting
    logger.info(
        "🎨 [bold blue]Rich[/bold blue] formatting works with [italic green]loguru[/italic green]!"
    )
    logger.info(
        "🌈 [red]Colors[/red] [yellow]are[/yellow] [green]beautiful[/green] [blue]and[/blue] [magenta]fun[/magenta]!"
    )
    logger.info(
        "⚡ [bold]Fast[/bold] and [italic]efficient[/italic] logging with [underline]style[/underline]!"
    )

    # Demonstrate Pydantic validation
    try:
        # This should work
        valid_config = AppConfig(debug=True, app_name="Test App", version="1.0.0")
        logger.info(f"✅ Pydantic validation successful: {valid_config.app_name}")

        # This would raise validation error (commented out to avoid actual error)
        # invalid_config = AppConfig(debug="not_a_boolean")  # This would fail

    except Exception as e:
        logger.error(f"❌ Pydantic validation failed: {e}")

    # Success message
    success_text = Text("✅ All systems operational!", style="bold green")
    console.print(Panel(success_text, border_style="blue"))
    
    #########################################################
    # Eval Pipeline
    #########################################################
    
    BASIC_EVAL_PROMPT = """
    You are an expert code reviewer. Evaluate this AI-generated solution.
    
    Task: 
    <task>
    {task}
    </task>
    
    Solution: 
    <solution>
    {solution}
    </solution>
        
    Output format
    Provide your evaluation as a structured JSON object with the following fields:
    - "strengths": An array of 1-3 key strengths
    - "weaknesses": An array of 1-3 key areas for improvement  
    - "reasoning": A concise explanation of your assessment
    - "score": A number between 1-10
    """
    
    CRITERIA_EVAL_PROMPT = """
    You are an expert code reviewer. Evaluate this AI-generated solution.
    
    Task: 
    <task>
    {task}
    </task>
    
    Solution: 
    <solution>
    {solution}
    </solution>
    
    Criteria you should use to evaluate the solution:
    <solution_criteria>
    {solution_criteria}
    </solution_criteria>
    
    Output format
    Provide your evaluation as a structured JSON object with the following fields:
    - "strengths": An array of 1-3 key strengths
    - "weaknesses": An array of 1-3 key areas for improvement  
    - "reasoning": A concise explanation of your assessment
    - "score": A number between 1-10
    """    
    
    DEFAULT_PROMPT = "Please solve the following task: {task}"
    
    console.print(Panel(f"Evaluating default prompt\n'{DEFAULT_PROMPT}'\nwith three different datasets", border_style="blue"))
    
    console.print(Panel("Basic Dataset Prompt", border_style="green"))
        
    DS_BASIC_PROMPT = """
        Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
        that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
        each representing task that requires Python, JSON, or a Regex to complete. 

        Example output:
        ```json
        [
            {
                "task": "Description of task",
                "format": "python" | "json" | "regex"
            },
            ...additional
        ]
        ```
        Please generate 3 objects.
        """
    
    
    dataset_generator = DatasetGenerator(DS_BASIC_PROMPT, "basic_dataset.json")
    grader = Grader(BASIC_EVAL_PROMPT)
    eval_pipeline = EvalPipeline(dataset_generator, grader, prompt=DEFAULT_PROMPT)
    eval_pipeline.run()
    
    console.print(Panel("Improved Dataset Prompt", border_style="green"))
    
    DS_IMPROVED_PROMPT = """
        Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
        that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
        each representing task that requires Python, JSON, or a Regex to complete.

        Example output:
        ```json
        [
            {
                "task": "Description of task",
                "format": "python" | "json" | "regex"
            },
            ...additional
        ]
        ```

        * Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
        * Focus on tasks that do not require writing much code

        Please generate 3 objects.
        """

    dataset_generator = DatasetGenerator(DS_IMPROVED_PROMPT, "improved_dataset.json")
    grader = Grader(BASIC_EVAL_PROMPT)
    eval_pipeline = EvalPipeline(dataset_generator, grader, prompt=DEFAULT_PROMPT)
    eval_pipeline.run()

    console.print(Panel("Best Dataset Prompt", border_style="green"))
    
    DS_BEST_PROMPT = """
        Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
        that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
        each representing task that requires Python, JSON, or a Regex to complete. It will also include a criteria
        attribute that describes the criteria for evaluating the task.

        Example output:
        ```json
        [
            {
                "task": "Description of task",
                "format": "python" | "json" | "regex",
                "solution_criteria": "A thoughtful criteria for evaluating the task"
            },
            ...additional
        ]
        ```

        * Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
        * Focus on tasks that do not require writing much code
        * The solution criteria should be related to the task at hand and should be composed by a list of thoughtful arguments for evaluating the task.

        Please generate 3 objects.
        """

    dataset_generator = DatasetGenerator(DS_BEST_PROMPT, "best_dataset.json")
    grader = Grader(CRITERIA_EVAL_PROMPT)
    eval_pipeline = EvalPipeline(dataset_generator, grader, prompt=DEFAULT_PROMPT)
    eval_pipeline.run()


    BETTER_PROMPT = """
    Please solve the following task in the best way possible:
    <task>
    {task}
    </task>
    
    Demonstrate your Computer Science and Engineering skills, along with your knowledge of Python, cloud infrastructure and unix systems.
    Focus on the task and only reply with the solution.
    Use your best judgement to solve the task and don't get distracted.
    Try to be as concise and efficient as possible. 
    """
    
    console.print(Panel(f"Evaluating default prompt\n'{BETTER_PROMPT}'\nwith three different datasets", border_style="blue"))
    
    console.print(Panel("Basic Dataset Prompt", border_style="green"))
        
    DS_BASIC_PROMPT = """
        Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
        that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
        each representing task that requires Python, JSON, or a Regex to complete. 

        Example output:
        ```json
        [
            {
                "task": "Description of task",
                "format": "python" | "json" | "regex"
            },
            ...additional
        ]
        ```
        Please generate 3 objects.
        """
    
    
    dataset_generator = DatasetGenerator(DS_BASIC_PROMPT, "basic_dataset.json")
    grader = Grader(BASIC_EVAL_PROMPT)
    eval_pipeline = EvalPipeline(dataset_generator, grader, prompt=BETTER_PROMPT)
    eval_pipeline.run(dataset_file="basic_dataset.json")
    
    console.print(Panel("Improved Dataset Prompt", border_style="green"))
    
    DS_IMPROVED_PROMPT = """
        Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
        that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
        each representing task that requires Python, JSON, or a Regex to complete.

        Example output:
        ```json
        [
            {
                "task": "Description of task",
                "format": "python" | "json" | "regex"
            },
            ...additional
        ]
        ```

        * Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
        * Focus on tasks that do not require writing much code

        Please generate 3 objects.
        """

    dataset_generator = DatasetGenerator(DS_IMPROVED_PROMPT, "improved_dataset.json")
    grader = Grader(BASIC_EVAL_PROMPT)
    eval_pipeline = EvalPipeline(dataset_generator, grader, prompt=BETTER_PROMPT)
    eval_pipeline.run(dataset_file="improved_dataset.json")

    console.print(Panel("Best Dataset Prompt", border_style="green"))
    
    DS_BEST_PROMPT = """
        Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
        that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
        each representing task that requires Python, JSON, or a Regex to complete. It will also include a criteria
        attribute that describes the criteria for evaluating the task.

        Example output:
        ```json
        [
            {
                "task": "Description of task",
                "format": "python" | "json" | "regex",
                "solution_criteria": "A thoughtful criteria for evaluating the task"
            },
            ...additional
        ]
        ```

        * Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
        * Focus on tasks that do not require writing much code
        * The solution criteria should be related to the task at hand and should be composed by a list of thoughtful arguments for evaluating the task.

        Please generate 3 objects.
        """

    dataset_generator = DatasetGenerator(DS_BEST_PROMPT, "best_dataset.json")
    grader = Grader(CRITERIA_EVAL_PROMPT)
    eval_pipeline = EvalPipeline(dataset_generator, grader, prompt=BETTER_PROMPT)
    eval_pipeline.run(dataset_file="best_dataset.json")


if __name__ == "__main__":
    app()
