import re
from statistics import mean
import uuid
import inspect

def render(template_string, variables):
    placeholders = re.findall(r"{([^{}]+)}", template_string)

    result = template_string
    for placeholder in placeholders:
        if placeholder in variables:
            result = result.replace(
                "{" + placeholder + "}", str(variables[placeholder])
            )

    return result.replace("{{", "{").replace("}}", "}")

def extract_prompt_from_function(prompt_function) -> str:
    """
    Extract the prompt text from a prompt function by analyzing its source code.
    
    Args:
        prompt_function: A function that generates prompts
        
    Returns:
        str: The extracted prompt text (first 50 characters for filename generation)
    """
    try:
        # Get the source code of the function
        source = inspect.getsource(prompt_function)
        
        # Look for the prompt string in the function - simplified approach
        # First, try to find the prompt assignment with triple quotes
        prompt_match = re.search(r'prompt\s*=\s*f?"""(.*?)"""', source, re.DOTALL)
        if prompt_match:
            prompt_text = prompt_match.group(1).strip()
            # Remove common template variables and get meaningful text
            cleaned = re.sub(r'\{[^}]+\}', '', prompt_text)  # Remove {variable} placeholders
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()   # Normalize whitespace
            
            # If we got meaningful text, return it
            if cleaned and len(cleaned) > 5:
                return cleaned[:50]  # Return first 50 characters
        
        # Try single quotes if triple quotes didn't work
        prompt_match = re.search(r'prompt\s*=\s*f?"(.*?)"', source, re.DOTALL)
        if prompt_match:
            prompt_text = prompt_match.group(1).strip()
            cleaned = re.sub(r'\{[^}]+\}', '', prompt_text)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            if cleaned and len(cleaned) > 5:
                return cleaned[:50]
        
        # Try without f-string prefix (regular string)
        prompt_match = re.search(r'prompt\s*=\s*"""(.*?)"""', source, re.DOTALL)
        if prompt_match:
            prompt_text = prompt_match.group(1).strip()
            cleaned = re.sub(r'\{[^}]+\}', '', prompt_text)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            if cleaned and len(cleaned) > 5:
                return cleaned[:50]
        
        # If no meaningful text found, try to extract from function name or docstring
        if prompt_function.__doc__:
            doc_text = prompt_function.__doc__.strip()
            cleaned_doc = re.sub(r'\s+', ' ', doc_text).strip()
            if cleaned_doc and len(cleaned_doc) > 5:
                return cleaned_doc[:50]
        
        # Fallback: extract function name
        return prompt_function.__name__[:20]
        
    except Exception as e:
        # Fallback to function name if extraction fails
        return prompt_function.__name__[:20]

def generate_filename_from_prompt(prompt: str, extension: str = "json") -> str:
    """
    Generate a filename from the first 10 characters of a prompt combined with a UUID.
    
    Args:
        prompt (str): The input prompt
        extension (str): File extension (default: "json")
    
    Returns:
        str: Generated filename in format: first_15_chars_uuid.extension
    """
    # Clean the prompt: remove special characters and convert to lowercase
    cleaned_prompt = re.sub(r'[^a-zA-Z0-9\s]', '', prompt.lower())
    
    # Get meaningful text (at least 3 characters, up to 15)
    meaningful_text = cleaned_prompt.strip()
    if len(meaningful_text) < 3:
        meaningful_text = "prompt"  # Fallback if no meaningful text
    
    # Take first 15 characters, but don't pad with 'x'
    first_chars = meaningful_text[:15]
    
    # Generate UUID (version 4 - random)
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for shorter filename
    
    # Combine and create filename
    filename = f"{first_chars}_{unique_id}.{extension}"
    
    return filename

def generate_filename_from_prompt_function(prompt_function, extension: str = "json") -> str:
    """
    Generate a filename from a prompt function by extracting the prompt text.
    
    Args:
        prompt_function: A function that generates prompts
        extension (str): File extension (default: "json")
    
    Returns:
        str: Generated filename in format: prompt_prefix_uuid.extension
    """
    # Extract prompt text from the function
    prompt_text = extract_prompt_from_function(prompt_function)
    
    # Generate filename using the existing function
    return generate_filename_from_prompt(prompt_text, extension)

def generate_prompt_evaluation_report(evaluation_results):
    total_tests = len(evaluation_results)
    scores = [result["score"] for result in evaluation_results["results"]]
    avg_score = mean(scores) if scores else 0
    max_possible_score = 10
    pass_rate = (
        100 * len([s for s in scores if s >= 7]) / total_tests
        if total_tests
        else 0
    )

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Prompt Evaluation Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            .header {{
                background-color: #f0f0f0;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .summary-stats {{
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 10px;
            }}
            .stat-box {{
                background-color: #fff;
                border-radius: 5px;
                padding: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                flex-basis: 30%;
                min-width: 200px;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                margin-top: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th {{
                background-color: #4a4a4a;
                color: white;
                text-align: left;
                padding: 12px;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
                vertical-align: top;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .output-cell {{
                white-space: pre-wrap;
            }}
            .score {{
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 3px;
                display: inline-block;
            }}
            .score-high {{
                background-color: #c8e6c9;
                color: #2e7d32;
            }}
            .score-medium {{
                background-color: #fff9c4;
                color: #f57f17;
            }}
            .score-low {{
                background-color: #ffcdd2;
                color: #c62828;
            }}
            .generated-output {{
                overflow: auto;
                white-space: pre-wrap;
            }}

            .generated-output pre {{
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin: 0;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.4;
                color: #333;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
                overflow-x: auto;
                white-space: pre-wrap; 
                word-wrap: break-word; 
            }}

            td {{
                width: 20%;
            }}
            .score-col {{
                width: 80px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Prompt Evaluation Report</h1>
            <div class="summary-stats">
                <div class="stat-box">
                    <div>Total Test Cases</div>
                    <div class="stat-value">{total_tests}</div>
                </div>
                <div class="stat-box">
                    <div>Average Score</div>
                    <div class="stat-value">{avg_score:.1f} / {max_possible_score}</div>
                </div>
                <div class="stat-box">
                    <div>Pass Rate (≥7)</div>
                    <div class="stat-value">{pass_rate:.1f}%</div>
                </div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Scenario</th>
                    <th>Prompt Inputs</th>
                    <th>Solution Criteria</th>
                    <th>Generated Output</th>
                    <th>Score</th>
                    <th>Reasoning</th>
                </tr>
            </thead>
            <tbody>
    """

    for result in evaluation_results["results"]:
        prompt_inputs_html = "<br>".join(
            [
                f"<strong>{key}:</strong> {value}"
                for key, value in result["test_case"]["prompt_inputs"].items()
            ]
        )

        criteria_string = "<br>• ".join(
            result["test_case"]["solution_criteria"]
        )

        score = result["score"]
        if score >= 8:
            score_class = "score-high"
        elif score <= 5:
            score_class = "score-low"
        else:
            score_class = "score-medium"

        html += f"""
            <tr>
                <td>{result["test_case"]["scenario"]}</td>
                <td class="prompt-inputs">{prompt_inputs_html}</td>
                <td class="criteria">• {criteria_string}</td>
                <td class="generated-output"><pre>{result["generated_output"]}</pre></td>
                <td class="score-col"><span class="score {score_class}">{score}</span></td>
                <td class="reasoning">{result["reasoning"]}</td>
            </tr>
        """

    html += """
            </tbody>
        </table>
    </body>
    </html>
    """

    return html