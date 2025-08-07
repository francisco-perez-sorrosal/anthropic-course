import json
import re
import concurrent.futures

from textwrap import dedent
from loguru import logger

from anthropic_course.conversation import Conversation
from anthropic_course.utils import render

class DatasetGenerator:
    
    TEST_DESIGNER_PROMPT = """
    You are a test scenario designer specialized in creating diverse, unique testing scenarios.
    """
    
    TEST_CASE_CREATOR_PROMPT = """
    You are a test case creator specializing in designing evaluation scenarios.
    """
    
    def __init__(self, task_description: str, prompt_inputs_spec: dict = {}, filename:str = "dataset.json"):
        self.filename = filename
        self.test_designer_conversation = Conversation(max_tokens=1000, system_msg=self.TEST_DESIGNER_PROMPT)
        self.test_case_creator_conversation = Conversation(max_tokens=1000, system_msg=self.TEST_CASE_CREATOR_PROMPT)
        self.task_description = task_description
        self.prompt_inputs_spec = prompt_inputs_spec


    def generate_unique_ideas(
        self, task_description, prompt_inputs_spec, num_cases
    ):
        """Generate a list of unique ideas for test cases based on the task description (goal)"""

        prompt = """
        Generate {num_cases} unique, diverse ideas for testing a prompt that accomplishes this task:
        
        <task_description>
        {task_description}
        </task_description>

        The prompt will receive the following inputs
        <prompt_inputs>
        {prompt_inputs_spec}
        </prompt_inputs>
        
        Each idea should represent a distinct scenario or example that tests different aspects of the task.
        
        Output Format:
        Provide your response as a structured JSON array where each item is a brief description of the idea.
        
        Example:
        ```json
        [
            "Testing with technical computer science terminology",
            "Testing with medical research findings",
            "Testing with complex mathematical concepts",
            ...
        ]
        ```
        
        Ensure each idea is:
        - Clearly distinct from the others
        - Relevant to the task description
        - Specific enough to guide generation of a full test case
        - Quick to solve without requiring extensive computation or multi-step processing
        - Solvable with no more than 400 tokens of output

        Remember, only generate {num_cases} unique ideas
        """

        example_prompt_inputs = ""
        for key, value in prompt_inputs_spec.items():
            val = value.replace("\n", "\\n")
            example_prompt_inputs += f'"{key}": str # {val},'

        rendered_prompt = render(
            dedent(prompt),
            {
                "task_description": task_description,
                "num_cases": num_cases,
                "prompt_inputs": example_prompt_inputs,
            },
        )

        message = self.test_designer_conversation.chat(role="user", text=rendered_prompt, prefill_text="```json", stop_sequences=["```"], temperature=1.0)
        logger.debug(message)
        return json.loads(message)

    def generate_test_case(self, task_description, idea, prompt_inputs_spec={}):
        """Generate a single test case based on the task description and a specific idea"""

        example_prompt_inputs = ""
        for key, value in prompt_inputs_spec.items():
            val = value.replace("\n", "\\n")
            example_prompt_inputs += f'"{key}": "EXAMPLE_VALUE", // {val}\n'

        allowed_keys = ", ".join(
            [f'"{key}"' for key in prompt_inputs_spec.keys()]
        )

        prompt = """
        Generate a single detailed test case for a prompt evaluation based on:
        
        <task_description>
        {task_description}
        </task_description>
        
        <specific_idea>
        {idea}
        </specific_idea>
        
        <allowed_input_keys>
        {allowed_keys}
        </allowed_input_keys>
        
        Output Format:
        ```json
        {{
            "prompt_inputs": {{
            {example_prompt_inputs}
            }},
            "solution_criteria": ["criterion 1", "criterion 2", ...] // Concise list of criteria for evaluating the solution, 1 to 4 items
        }}
        ```
        
        IMPORTANT REQUIREMENTS:
        - You MUST ONLY use these exact input keys in your prompt_inputs: {allowed_keys}        
        - Do NOT add any additional keys to prompt_inputs
        - All keys listed in allowed_input_keys must be included in your response
        - Make the test case realistic and practically useful
        - Include measurable, concise solution criteria
        - The solution criteria should ONLY address the direct requirements of the task description and the generated prompt_inputs
        - Avoid over-specifying criteria with requirements that go beyond the core task
        - Keep solution criteria simple, focused, and directly tied to the fundamental task
        - The test case should be tailored to the specific idea provided
        - Quick to solve without requiring extensive computation or multi-step processing
        - Solvable with no more than 400 tokens of output
        - DO NOT include any fields beyond those specified in the output format

        Here's an example of a sample input with an ideal output:
        <sample_input>
        <sample_task_description>
        Extract topics out of a passage of text
        </sample_task_description>
        <sample_specific_idea>
        Testing with a text that contains multiple nested topics and subtopics (e.g., a passage about renewable energy that covers solar power economics, wind turbine technology, and policy implications simultaneously)
        </sample_specific_idea>

        <sample_allowed_input_keys>
        "content"
        </sample_allowed_input_keys>
        </sample_input>
        <ideal_output>
        ```json
        {
            "prompt_inputs": {
                "content": "The transition to renewable energy encompasses numerous interdependent dimensions. Solar photovoltaic technology has seen dramatic cost reductions, with panel efficiency improving 24% since 2010 while manufacturing costs declined by 89%, making it economically competitive with fossil fuels in many markets. Concurrently, wind energy has evolved through innovative turbine designs featuring carbon-fiber composite blades and advanced control systems that increase energy capture by 35% in low-wind conditions."
            },
            "solution_criteria": [
                "Includes all topics mentioned"   
            ]
        }
        ```
        </ideal_output>
        This is ideal output because the solution criteria is concise and doesn't ask for anything outside of the scope of the task description.
        """

        rendered_prompt = render(
            dedent(prompt),
            {
                "allowed_keys": allowed_keys,
                "task_description": task_description,
                "idea": idea,
                "example_prompt_inputs": example_prompt_inputs,
            },
        )

        message = self.test_case_creator_conversation.chat(role="user", text=rendered_prompt, prefill_text="```json", stop_sequences=["```"], temperature=0.7)

        test_case = json.loads(message)
        test_case["task_description"] = task_description
        test_case["scenario"] = idea

        return test_case



    def run(self, num_cases: int = 1, max_parallel_tasks:int = 3):
        
        ideas = self.generate_unique_ideas(
            self.task_description, self.prompt_inputs_spec, num_cases
        )

        dataset = []
        completed_test_cases = 0
        total_test_cases = len(ideas)
        last_reported_percentage = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel_tasks) as executor:
            idea_future = {
                executor.submit(
                    self.generate_test_case,
                    self.task_description,
                    idea,
                    self.prompt_inputs_spec,
                ): idea
                for idea in ideas
            }
            
            for future in concurrent.futures.as_completed(idea_future):
                try:
                    result = future.result()
                    completed_test_cases += 1
                    current_percentage = int((completed_test_cases / total_test_cases) * 100)
                    milestone_percentage = (current_percentage // 20) * 20

                    if milestone_percentage > last_reported_percentage:
                        logger.info(f"Generated {completed_test_cases}/{total_test_cases} test cases")
                        last_reported_percentage = milestone_percentage

                    dataset.append(result)
                except Exception as e:
                    logger.error(f"Error generating test case: {e}")        

        with open(self.filename, "w") as f:
            json.dump(dataset, f, indent=2)
            logger.info(f"Generated dataset saved in {self.filename}")
        return self.filename
