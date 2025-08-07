"""Main CLI application for anthropic-course."""

import os

import typer
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from anthropic_course.conversation import Conversation
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
    
    
    goal = "Write a compact, concise suggestion for a dietary supplememnts for a person"
    
    prompt_inputs_spec={
        "goal": "Goal of the person. (e.g. improve health, lose weight, etc.)",
        "height": "Person's height in cm",
        "weight": "Person's weight in kg", 
        "age": "Person's age in years",
        "gender": "Person's gender",
        "current_health_status": "Person's subjective view of their health status. (e.g. from 1 to 10, 10 being the best)",
        "chronic_conditions": "Person's chronic conditions. (e.g. diabetes, hypertension, etc.)",
        "current_medications": "Person's current medications. (e.g. blood pressure medication, diabetes medication, etc.)",
        "dietary_preferences": "Dietary preferences of the person. (e.g. vegan, vegetarian, paleo, etc.)",
        "dietary_restrictions": "Dietary restrictions of the person",
        "physical_activity_level": "Person's physical activity level (sedentary, light, moderate, high)",
        "current_supplements": "Current supplements of the person. (e.g. vitamins, minerals, etc.)"
    }
    
    dataset_generator = DatasetGenerator(task_description=goal, prompt_inputs_spec=prompt_inputs_spec, filename="dataset.json")
    # dataset_generator.run(num_cases=10, max_parallel_tasks=3)
    
    extra_criteria="""
        The output should include:
        - Goal/subgoal breakdown and which supplements are needed to achieve it
        - The supplements will include exact quantity and frequency
        - Reasoning how the supplement suggestion will help the person achieve the goal, and/or help with chronic conditions
        - Interactions with other supplements and medications (if any)
        - Scientific evidence for the suggestion
    """

    #########################################################
    # Basic Prompt
    #########################################################

    def basic_prompt(prompt_inputs):
        prompt = f"""
        What should this person take as suplement?
        
        Goal: {prompt_inputs["goal"]}
        Height: {prompt_inputs["height"]}
        Weight: {prompt_inputs["weight"]}
        Dietary Restrictions: {prompt_inputs["dietary_restrictions"]}
        """
        conversation = Conversation(max_tokens=1000)
        return conversation.chat(role="user", text=prompt, temperature=0.0)    
    
    grader = Grader()
    eval_pipeline = EvalPipeline(dataset_generator=dataset_generator, grader=grader, prompt_function=basic_prompt)
    eval_pipeline.run(extra_criteria=extra_criteria, dataset_file="dataset.json", run_syntax_grade=False)

    #########################################################
    # Advanced Prompt
    #########################################################

    def advanced_prompt(prompt_inputs):
        prompt = f"""
        Generate a dietary supplement plan for a person that meets it's goals.

            <person_information> 
            - Goal: {prompt_inputs["goal"]}
            - Height: {prompt_inputs["height"]} cm
            - Weight: {prompt_inputs["weight"]} kg
            - Age: {prompt_inputs["age"]} years
            - Gender: {prompt_inputs["gender"]}
            - Current health status: {prompt_inputs["current_health_status"]}
            - Chronic conditions: {prompt_inputs["chronic_conditions"]}
            - Current medications: {prompt_inputs["current_medications"]}
            - Dietary preferences: {prompt_inputs["dietary_preferences"]}
            - Dietary restrictions: {prompt_inputs["dietary_restrictions"]}
            - Physical activity level: {prompt_inputs["physical_activity_level"]}
            - Current supplements: {prompt_inputs["current_supplements"]}
            </person_information>

            Guidelines:
            1. Include accurate daily supplement amount (in mg, g, etc.)
            2. Show which supplements are needed to achieve the goal
            3. Specify when to take each supplement
            4. Use only supplements that fit restrictions
            5. List all supplement amounts in mg, g, etc.
            6. Add scientific substantiation and comprehensive medication interaction analysis (if necessary)
            7. Keep budget-friendly if mentioned

            Here is an example with a sample input and an ideal output:
            <sample_input>
            goal: Improve overall health and reduce risk of osteoporosis
            height: 170
            weight: 70
            age: 30
            gender: Male
            current_health_status: 8
            chronic_conditions: None
            current_medications: None
            dietary_preferences: Vegan
            dietary_restrictions: None
            physical_activity_level: Sedentary
            current_supplements: None
            </sample_input>
            <ideal_output>
            Here is a dietary supplement plan for a person aiming to improve health:

            * Goal: Improve health
                * Subgoal: Improve bone health
                    *   **Vitamin D3:** 1000 IU
                        - Vitamin D is important for bone health and immune system support.
                        - Scientific evidence shows that Vitamin D3 can help improve bone health and reduce the risk of osteoporosis.
                * Subgoal: Improve red blood cell production
                    *   **Vitamin B12:** 1000 mcg
                        - Vitamin B12 is important for red blood cell production and nerve function.
                        - Scientific evidence shows that Vitamin B12 can help improve red blood cell production and nerve function.

            This supplement plan prioritizes vitamins and minerals to support the person's health.
            </ideal_output>
            This example supplement plan is well-structured, provides detailed information on supplement choices and quantities, and aligns with the person's goals and restrictions.
        """
        conversation = Conversation(max_tokens=1000)
        return conversation.chat(role="user", text=prompt, temperature=0.0)  

    grader = Grader()
    eval_pipeline = EvalPipeline(dataset_generator=dataset_generator, grader=grader, prompt_function=advanced_prompt)
    eval_pipeline.run(extra_criteria=extra_criteria, run_syntax_grade=False)


if __name__ == "__main__":
    app()
