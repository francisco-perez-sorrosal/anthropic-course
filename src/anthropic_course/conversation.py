import json
from typing import Any, Callable, List, TYPE_CHECKING
from anthropic import NOT_GIVEN, Anthropic, NotGiven
from anthropic.types import Message
import loguru
from rich.console import Console
from rich.rule import Rule

if TYPE_CHECKING:
    from .tools import Tool

logger = loguru.logger

class Conversation:
    def __init__(self, model:str = "claude-3-5-haiku-20241022", max_tokens:int = 10, system_msg:str | NotGiven = NOT_GIVEN):
        self.client = Anthropic()
        self.params = {
            "model": model,
            "max_tokens": max_tokens,
        }
        self.system_msg = system_msg
        self.messages = []
        self.console = Console()

    def _add_message(self, role:str, message: Message | list[Message] | str | None):
        if not message:
            logger.warning("No text provided for message")        
        match (role):
            case "user" | "assistant":
                new_message = {"role": role, "content": message.content if isinstance(message, Message) else message}
            case _:
                raise ValueError(f"Invalid role: {role}")
        self.messages.append(new_message)

    def text_from_message(self, message: Message) -> str:
        return "\n".join([block.text for block in message.content if block.type == "text"])

    def _run_tools(self, tools: List["Tool"], message: Message):
        # TODO Parallelize tool calls
        tool_requests = [block for block in message.content if block.type == "tool_use"]
        tool_result_blocks = []
        
        for tool_request in tool_requests:
            try:
                # Find the matching tool
                matching_tool = None
                for tool in tools:
                    if tool.name == tool_request.name:
                        matching_tool = tool
                        break
                
                if matching_tool is None:
                    raise ValueError(f"Tool not found: {tool_request.name}")
                
                logger.info(f"Running tool: {tool_request.name}")
                
                # Parse the tool request input
                tool_input = {}
                if hasattr(tool_request, 'input') and tool_request.input:
                    match tool_request.input:
                        case str():
                            tool_input = json.loads(tool_request.input)
                        case dict():
                            tool_input = tool_request.input
                        case _:
                            logger.warning(f"Unexpected tool input type: {type(tool_request.input)}")
                            tool_input = {}
                
                # Execute the tool using the Tool.execute method
                result = matching_tool.execute(tool_input)
                
                tool_result_block = {
                    "type": "tool_result",
                    "tool_use_id": tool_request.id,                        
                    "content": json.dumps({"result": result}),
                    "is_error": False
                }
                
            except Exception as e:
                logger.error(f"Error running tool: {tool_request.name if hasattr(tool_request, 'name') else 'unknown'}: {e}")
                tool_result_block = {
                    "type": "tool_result",
                    "tool_use_id": tool_request.id,                        
                    "content": f"Error running tool: {e}",
                    "is_error": True,
                }
            
            tool_result_blocks.append(tool_result_block)
                    
        return tool_result_blocks

    def chat(self, 
             role:str = "user", 
             text:str | None = None, 
             prefill_text:str | None = None, 
             temperature:float = 0.0, 
             streaming:bool = True, 
             stop_sequences:list[str] = [], 
             tools:List["Tool"] = []) -> tuple[Message, str]:
        self._add_message(role, text)
        self.params["system"] = self.system_msg
        self.params["messages"] = self.messages
        self.params["temperature"] = temperature
        self.params["stop_sequences"] = stop_sequences
        # Convert Tool objects to Anthropic format for the API
        anthropic_tools = [tool.to_anthropic_format() for tool in tools]
        self.params["tools"] = anthropic_tools
        if prefill_text:
            self._add_message("assistant", prefill_text)
        if streaming:
            message = ""
            with self.client.messages.stream(**self.params) as stream:
                for text in stream.text_stream:
                    pass
                message = stream.get_final_message()
        else:
            message = self.client.messages.create(**self.params)
        
        self._add_message("assistant", message)

        # Handle multiple sequential tool calls
        while message.stop_reason == "tool_use":
            self.console.print(Rule("[bold red]Assistant wants to use a tool[/bold red]"))
            tool_result_blocks = self._run_tools(tools, message)
            
            # Create a new message with tool results
            self._add_message("user", tool_result_blocks)
            
            # Create a new params dict with tool results for this specific call
            # We need to include the current assistant message and the tool result
            tool_params = self.params.copy()
            tool_params["messages"] = self.messages
            
            # Then trigger a new invocation with the tool result and add it to the history
            message = self.client.messages.create(**tool_params)
            self._add_message("assistant", message)

        return message, self.text_from_message(message)
    
    def __str__(self):
        self.console.print(Rule("[bold red]Full Conversation[/bold red]"))
        return "\n".join([f"{message['role']}: {message['content']}\n" for message in self.messages])
