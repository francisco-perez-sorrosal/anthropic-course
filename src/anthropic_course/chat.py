from anthropic_course.conversation import Conversation
from anthropic import NOT_GIVEN, NotGiven
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
import loguru

logger = loguru.logger


class Chat:
    def __init__(self, model:str = "claude-3-5-haiku-20241022", max_tokens:int = 10, system_msg:str | NotGiven = NOT_GIVEN):
        print(max_tokens)
        self.conversation = Conversation(model=model, max_tokens=max_tokens, system_msg=system_msg)

    def run(self, temperature:float = 0.0, prefill_text:str | None = None, stop_sequences=["```"]):
        console = Console()
        while True:
            try:
                console.print(Rule("[bold blue]User[/bold blue]"))
                user_input = input("> ")
                console.print(f"> {user_input}")
                self.conversation.chat(role="user", text=user_input, prefill_text=prefill_text, temperature=temperature, streaming=True, stop_sequences=stop_sequences)
                console.print(Rule("[bold blue]Assistant[/bold blue]"))
                console.print(self.conversation.messages[-1]['content'])
                # console.print(self.conversation)
            except KeyboardInterrupt:
                logger.info("Ctrl+C pressed. Exiting...")
                break
