import re
from statistics import mean
import uuid
import json

from loguru import logger

from anthropic_course import dataset_generator
from anthropic_course.conversation import Conversation
from anthropic_course.dataset_generator import DatasetGenerator
from anthropic_course.grader import Grader

def generate_filename_from_prompt(prompt: str, extension: str = "json") -> str:
    """
    Generate a filename from the first 10 characters of a prompt combined with a UUID.
    
    Args:
        prompt (str): The input prompt
        extension (str): File extension (default: "json")
    
    Returns:
        str: Generated filename in format: first_10_chars_uuid.extension
    """
    # Clean the prompt: remove special characters and convert to lowercase
    cleaned_prompt = re.sub(r'[^a-zA-Z0-9\s]', '', prompt.lower())
    
    # Get first 10 characters, pad with 'x' if shorter
    first_10 = cleaned_prompt[:10].strip()
    if len(first_10) < 10:
        first_10 = first_10.ljust(10, 'x')
    
    # Generate UUID (version 4 - random)
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for shorter filename
    
    # Combine and create filename
    filename = f"{first_10}_{unique_id}.{extension}"
    
    return filename

class EvalPipeline:

    def __init__(self, dataset_generator:DatasetGenerator, grader:Grader, prompt:str):
        self.dataset_generator = dataset_generator
        self.dataset = None
        self.prompt = prompt
        self.conversation = Conversation(max_tokens=1000)
        self.graded_filename = generate_filename_from_prompt(prompt)
        self.grader = grader
        
    def load_dataset(self, dataset_file:str):
        with open(dataset_file, "r") as f:
            return json.load(f)

    def run_prompt(self, test_case, prefill_text:str = "```code", stop_sequences:list[str] = ["```"]):
        """Merges the prompt and test case input, then returns the result"""
        return self.conversation.chat(role="user", text=self.prompt.format(task=test_case["task"]), prefill_text=prefill_text, stop_sequences=stop_sequences)


    def run_test_case(self, test_case) -> dict:
        """Calls run_prompt, then grades the result"""
        
        logger.info(f"Running test case: {test_case}")
        output = self.run_prompt(test_case)
        
        # Grade the output
        model_grade = self.grader.grade_by_model(test_case, output)
        syntax_grade = self.grader.grade_syntax(test_case, output)
        
        # Calculate the final score
        final_score = (model_grade["score"] + syntax_grade) / 2
        
        return {
            "task": test_case["task"],
            "generated_output": output,
            "score": final_score,
            "reasoning": model_grade["reasoning"],
            "strengths": model_grade["strengths"],
            "weaknesses": model_grade["weaknesses"]
        }
    
    def run(self, dataset_file:str | None = None) -> dict:
        """Loads the dataset and calls run_test_case with each case"""
        if not dataset_file:
            if not self.dataset:
                dataset_file = self.dataset_generator.run()
                self.dataset = self.load_dataset(dataset_file)
            else:
                logger.warning("Using cached dataset")
        else:
            self.dataset = self.load_dataset(dataset_file)
        
        results = []
        for test_case in self.dataset:
            result = self.run_test_case(test_case)
            results.append(result)
    
        try:
            average_score = mean([result["score"] for result in results])
            logger.info(f"Average score: {average_score}")
        except KeyError as e:
            logger.error("Returned dictionary does not contain a 'score' key")
            raise Exception(e)
            
        eval_results = {
            "prompt": self.prompt,
            "results": results,
            "average_score": average_score
        }
    
        with open(self.graded_filename, "w") as f:
            json.dump(eval_results, f, indent=2)
        logger.info(f"Grader Results saved in {self.graded_filename}")
        return eval_results
