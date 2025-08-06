from anthropic import NOT_GIVEN, Anthropic, NotGiven
import loguru

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

    def _add_message(self, role:str, text:str | None):
        if not text:
            logger.warning("No text provided for message")        
        match (role):
            case "user":
                new_message = {"role": "user", "content": text if text else ""}
            case "assistant":
                new_message = {"role": "assistant", "content": text if text else ""}
            case _:
                raise ValueError(f"Invalid role: {role}")
        self.messages.append(new_message)

    def chat(self, role:str = "user", text:str | None = None, prefill_text:str | None = None, temperature:float = 0.0, streaming:bool = True, stop_sequences:list[str] = []):
        self._add_message(role, text)
        self.params["system"] = self.system_msg
        self.params["messages"] = self.messages
        self.params["temperature"] = temperature
        self.params["stop_sequences"] = stop_sequences
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
        message_content = message.content[0].text
        self._add_message("assistant", message_content)
        return message_content
    
    def __str__(self):
        return "\n".join([f"{message['role']}: {message['content']}\n" for message in self.messages])
