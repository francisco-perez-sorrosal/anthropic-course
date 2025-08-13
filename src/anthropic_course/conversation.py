import json
from typing import Any, Callable, List, TYPE_CHECKING, Union
from anthropic import NOT_GIVEN, Anthropic, NotGiven
from anthropic.types import Message
import loguru
from rich.console import Console
from rich.rule import Rule

from anthropic_course.text_editor import TextEditor

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
        self.text_editor = TextEditor()

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


    def _run_text_editor_tool(self, tool_input):
        logger.info(f"Running text editor tool with input: {tool_input}")
        command = tool_input["command"]
        if command == "view":
            return self.text_editor.view(
                tool_input["path"], tool_input.get("view_range")
            )
        elif command == "str_replace":
            return self.text_editor.str_replace(
                tool_input["path"], tool_input["old_str"], tool_input["new_str"]
            )
        elif command == "create":
            return self.text_editor.create(
                tool_input["path"], tool_input["file_text"]
            )
        elif command == "insert":
            return self.text_editor.insert(
                tool_input["path"],
                tool_input["insert_line"],
                tool_input["new_str"],
            )
        elif command == "undo_edit":
            return self.text_editor.undo_edit(tool_input["path"])
        else:
            raise Exception(f"Unknown text editor command: {command}")


    def _run_tools(self, tools: List[Union["Tool", dict[str, Any]]], message: Message):
        # TODO Parallelize tool calls
        tool_requests = [block for block in message.content if block.type == "tool_use"]
        tool_result_blocks = []
        
        for tool_request in tool_requests:
            try:
                # Find the matching tool in the tools list
                matching_tool = None
                for tool in tools:
                    if isinstance(tool, dict):
                        # Dictionary tool (like text editor)
                        if tool.get("name") == tool_request.name:
                            match tool.get("name"):
                                case "str_replace_editor":
                                    # For text editor tool, we need to handle it specially
                                    matching_tool = self._run_text_editor_tool
                                case "web_search":
                                    # For web search tool, we need to handle it specially
                                    matching_tool = tool
                            break
                    elif hasattr(tool, 'name') and tool.name == tool_request.name:
                        matching_tool = tool
                        if tool.name == "str_replace_editor":
                            # For text editor tool, we need to handle it specially
                            matching_tool = self._run_text_editor_tool
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
                logger.info(f"Tool input: {tool_input}")
                
                # Execute the tool
                if callable(matching_tool) and not hasattr(matching_tool, 'execute'):
                    # For special tools like the text editor tool, call the function directly
                    result = matching_tool(tool_input)
                else:
                    # For Tool objects, use the execute method
                    execute_method = getattr(matching_tool, 'execute', None)
                    if execute_method is not None:
                        result = execute_method(tool_input)
                    else:
                        raise ValueError(f"Tool {tool_request.name} has no execute method")
                
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
             tools:List[Union["Tool", dict[str, Any]]] = []) -> tuple[Message, str]:
        self._add_message(role, text)
        if self.system_msg is not NOT_GIVEN:
            logger.warning("Adding cache control to system message")
            self.params["system"] = [{"type": "text", "text": self.system_msg, "cache_control": {"type": "ephemeral"}}]
        self.params["messages"] = self.messages
        self.params["temperature"] = temperature
        self.params["stop_sequences"] = stop_sequences
        # Convert Tool objects to Anthropic format for the API
        anthropic_tools = []
        for tool in tools:
            if isinstance(tool, dict):
                # It's already a dictionary (like text editor tool)
                anthropic_tools.append(tool)
            else:
                # Check if it's a text editor tool
                if hasattr(tool, 'name') and tool.name == "str_replace_editor":
                    # For text editor tool, use the proper format
                    anthropic_tools.append({
                        "type": "text_editor_20250124",
                        "name": "str_replace_editor"
                    })
                else:
                    # For regular Tool objects, use to_anthropic_format
                    anthropic_tools.append(tool.to_anthropic_format())
                    
        if anthropic_tools:
            logger.info("Adding cache control to last tool")
            last_tool = anthropic_tools[-1].copy()
            last_tool["cache_control"] = {"type": "ephemeral"}
            anthropic_tools[-1] = last_tool
        self.params["tools"] = anthropic_tools
            
        if self.params["model"].startswith("claude-3-5"):
            logger.warning("Using computer-use-2024-10-22 beta for claude-3-5 models")
            logger.warning("Current tools: ", tools)
            self.params["beta"] = ["computer-use-2024-10-22"]
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
