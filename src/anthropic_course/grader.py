import ast
import re
import json

from loguru import logger

from anthropic_course.conversation import Conversation

class Grader:
    
    def __init__(self, eval_prompt:str):
        self.eval_prompt = eval_prompt
    
    def grade_by_model(self, test_case, output):
        try:
            eval_prompt = self.eval_prompt.format(task=test_case["task"], solution=output, solution_criteria=test_case["solution_criteria"])
        except KeyError as e:
            logger.warning(f"KeyError: {e}. Using basic eval prompt")
            eval_prompt = self.eval_prompt.format(task=test_case["task"], solution=output)
        conversation = Conversation(max_tokens=1000)
        eval_text = conversation.chat(role="user", text=eval_prompt, prefill_text="```json", stop_sequences=["```"])
        return json.loads(eval_text)
    
    def validate_json(self, text):
        try:
            json.loads(text.strip())
            return 10
        except json.JSONDecodeError:
            return 0

    def validate_python(self, text):
        try:
            ast.parse(text.strip())
            return 10
        except SyntaxError:
            return 0

    def validate_regex(self, text):
        try:
            re.compile(text.strip())
            return 10
        except re.error:
            return 0


    def grade_syntax(self, test_case, response):
        format = test_case["format"]
        match format:
            case "json":
                return self.validate_json(response)
            case "python":
                return self.validate_python(response)
            case "regex":
                return self.validate_regex(response)
