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
app_2 = typer.Typer(
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


@app_2.command()
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
    
    
    goal = "Write a compact, concise 1 day meal plan for a single athlete"
    
    prompt_inputs_spec={
        "height": "Athlete's height in cm",
        "weight": "Athlete's weight in kg", 
        "goal": "Goal of the athlete",
        "restrictions": "Dietary restrictions of the athlete"
    }
    
    dataset_generator = DatasetGenerator(task_description=goal, prompt_inputs_spec=prompt_inputs_spec, filename="dataset.json")
    # dataset_generator.run(num_cases=10, max_parallel_tasks=3)
    
    extra_criteria="""
        The output should include:
        - Daily caloric total
        - Macronutrient breakdown
        - Meals with exact foods, portions, and timing
    """

    #########################################################
    # Basic Prompt
    #########################################################

    def basic_prompt(prompt_inputs):
        prompt = f"""
        What should this person eat?
        
        Height: {prompt_inputs["height"]}
        Weight: {prompt_inputs["weight"]}
        Goal: {prompt_inputs["goal"]}
        Dietary Restrictions: {prompt_inputs["restrictions"]}
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
        Generate a one-day meal plan for an athlete that meets their dietary restrictions.

            <athlete_information> 
            - Height: {prompt_inputs["height"]} 
            - Weight: {prompt_inputs["weight"]} 
            - Goal: {prompt_inputs["goal"]} 
            - Dietary restrictions: {prompt_inputs["restrictions"]} 
            </athlete_information>

            Guidelines:
            1. Include accurate daily calorie amount
            2. Show protein, fat, and carb amounts
            3. Specify when to eat each meal
            4. Use only foods that fit restrictions
            5. List all portion sizes in grams
            6. Keep budget-friendly if mentioned

            Here is an example with a sample input and an ideal output:
            <sample_input>
            height: 170
            weight: 70
            goal: Maintain fitness and improve cholesterol levels
            restrictions: High cholesterol
            </sample_input>
            <ideal_output>
            Here is a one-day meal plan for an athlete aiming to maintain fitness and improve cholesterol levels:

            *   **Calorie Target:** Approximately 2500 calories
            *   **Macronutrient Breakdown:** Protein (140g), Fat (70g), Carbs (340g)

            **Meal Plan:**

            *   **Breakfast (7:00 AM):** Oatmeal (80g dry weight) with berries (100g) and walnuts (15g). Skim milk (240g).
                *   Protein: 15g, Fat: 15g, Carbs: 60g
            *   **Mid-Morning Snack (10:00 AM):** Apple (150g) with almond butter (30g).
                *   Protein: 7g, Fat: 18g, Carbs: 25g
            *   **Lunch (1:00 PM):** Grilled chicken breast (120g) salad with mixed greens (150g), cucumber (50g), tomato (50g), and a light vinaigrette dressing (30g). Whole wheat bread (60g).
                *   Protein: 40g, Fat: 15g, Carbs: 70g
            *   **Afternoon Snack (4:00 PM):** Greek yogurt (170g, non-fat) with a banana (120g).
                *   Protein: 20g, Fat: 0g, Carbs: 40g
            *   **Dinner (7:00 PM):** Baked salmon (140g) with steamed broccoli (200g) and quinoa (75g dry weight).
                *   Protein: 40g, Fat: 20g, Carbs: 80g
            *   **Evening Snack (9:00 PM):** Small handful of almonds (20g).
                *   Protein: 8g, Fat: 12g, Carbs: 15g

            This meal plan prioritizes lean protein sources, whole grains, fruits, and vegetables, while limiting saturated and trans fats to support healthy cholesterol levels.
            </ideal_output>
            This example meal plan is well-structured, provides detailed information on food choices and quantities, and aligns with the athlete's goals and restrictions.
        """
        conversation = Conversation(max_tokens=1000)
        return conversation.chat(role="user", text=prompt, temperature=0.0)  

    eval_pipeline = EvalPipeline(dataset_generator=dataset_generator, grader=grader, prompt_function=advanced_prompt)
    eval_pipeline.run(extra_criteria=extra_criteria, dataset_file="dataset.json", run_syntax_grade=False)


if __name__ == "__main__":
    app_2()
