import ast
import re
import json
from textwrap import dedent

from loguru import logger

from anthropic_course.conversation import Conversation
from anthropic_course.utils import render

class Grader:
    
    EVAL_TEMPLATE = """
        Your task is to evaluate the following AI-generated solution with EXTREME RIGOR.

        Original task description:
        <task_description>
        {task_description}
        </task_description>

        Original task inputs:
        <task_inputs>
        {{ {prompt_inputs} }}
        </task_inputs>

        Solution to Evaluate:
        <solution>
        {output}
        </solution>

        Criteria you should use to evaluate the solution:
        <criteria>
        {solution_criteria}
        </criteria>

        {extra_criteria_section}

        Scoring Guidelines:
        * Score 1-3: Solution fails to meet one or more MANDATORY requirements
        * Score 4-6: Solution meets all mandatory requirements but has significant deficiencies in secondary criteria
        * Score 7-8: Solution meets all mandatory requirements and most secondary criteria, with minor issues
        * Score 9-10: Solution meets all mandatory and secondary criteria

        IMPORTANT SCORING INSTRUCTIONS:
        * Grade the output based ONLY on the listed criteria. Do not add your own extra requirements.
        * If a solution meets all of the mandatory and secondary criteria give it a 10
        * Don't complain that the solution "only" meets the mandatory and secondary criteria. Solutions shouldn't go above and beyond - they should meet the exact listed criteria.
        * ANY violation of a mandatory requirement MUST result in a score of 3 or lower
        * The full 1-10 scale should be utilized - don't hesitate to give low scores when warranted

        Output Format
        Provide your evaluation as a structured JSON object with the following fields, in this specific order:
        - "strengths": An array of 1-3 key strengths
        - "weaknesses": An array of 1-3 key areas for improvement
        - "reasoning": A concise explanation of your overall assessment
        - "score": A number between 1-10

        Respond with JSON. Keep your response concise and direct.
        Example response shape:
        {{
            "strengths": string[],
            "weaknesses": string[],
            "reasoning": string,
            "score": number
        }}
        """
    
    
    def grade_by_model(self, test_case, output, extra_criteria=None):
        
        prompt_inputs = ""
        for key, value in test_case["prompt_inputs"].items():
            val = value.replace("\n", "\\n")
            prompt_inputs += f'"{key}":"{val}",\n'        
        
        extra_criteria_section = ""
        if extra_criteria:
            extra_criteria_template = """
            Mandatory Requirements - ANY VIOLATION MEANS AUTOMATIC FAILURE (score of 3 or lower):
            <extra_important_criteria>
            {extra_criteria}
            </extra_important_criteria>
            """
            extra_criteria_section = render(
                dedent(extra_criteria_template),
                {"extra_criteria": extra_criteria},
            )
            
        eval_prompt = render(
            dedent(self.EVAL_TEMPLATE),
            {
                "task_description": test_case["task_description"],
                "prompt_inputs": prompt_inputs,
                "output": output,
                "solution_criteria": "\n".join(test_case["solution_criteria"]),
                "extra_criteria_section": extra_criteria_section,
            },
        )

        conversation = Conversation(max_tokens=1000)
        eval_text = conversation.chat(role="user", text=eval_prompt, prefill_text="```json", stop_sequences=["```"], temperature=0.0)
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
