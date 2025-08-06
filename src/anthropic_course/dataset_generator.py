import json

from loguru import logger

from anthropic_course.conversation import Conversation


class DatasetGenerator:
          
    def __init__(self, prompt:str, filename:str = "dataset.json"):
        self.filename = filename
        self.conversation = Conversation(max_tokens=1000)
        self.prompt = prompt

    def run(self) -> str:
        message = self.conversation.chat(role="user", text=self.prompt, prefill_text="```json", stop_sequences=["```"])
        logger.debug(message)
        json_message = json.loads(message)
        logger.info(json_message)
        with open(self.filename, "w") as f:
            json.dump(json_message, f, indent=2)
            logger.info(f"Generated dataset saved in {self.filename}")
        return self.filename
