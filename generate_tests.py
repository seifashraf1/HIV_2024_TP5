import google.generativeai as genai
from common.llm_test_generator import LLMTestGenerator
from common.prompt_generator import PromptGenerator
from common.abstract_executor import AbstractExecutor
from file_name_check import file_name_check
from to_test.number_to_words import number_to_words
from to_test.strong_password_checker import strong_password_checker
import importlib
import inspect
from num2words import num2words
import re
import random
import string

key = "AIzaSyDgogz2-6LPY0fP4ASfeEWVKW4mteStmIM"


def generate_inital_tests_with_llm(model, function_to_test):
    # Create an LLMTestGenerator object with the generative model and the function to test
    llm_generator = LLMTestGenerator(model, function=function_to_test)

    # Create a PromptGenerator object with the function to test
    prompt_generator = PromptGenerator(function_to_test)

    # Generate a prompt for the function
    prompt = prompt_generator.generate_prompt()

    # Print the prompt
    #print(prompt)

    # Create a test function using the LLMTestGenerator
    test, test_name = llm_generator.create_test_function(prompt)

    print("Tests produced by LLM:")

    print(test)

    # Define the filename for the generated test file
    filename = "test_generated.py"

    # Write the test function to the file
    llm_generator.write_test_to_file(test, filename=filename)

    # Get the module name and function name from the filename
    module_name = filename.split(".")[0]
    function_name = test_name

    # Import the module dynamically
    module = importlib.import_module(module_name)

    # Get the function from the module
    function = getattr(module, function_name)

    executor = AbstractExecutor(function)

    # Execute the input function and get the coverage date
    coverage_data = executor._execute_input(input=function_to_test)

    # Print the coverage date
    return function, coverage_data

def convert_assertions_to_list(func):
    # Get the source code of the function
    source_code = inspect.getsource(func)

    # Split the source code by lines
    lines = source_code.split('\n')
    assertions_list = []

    # Iterate over each line in the source code
    for line in lines:
        # Check if the line contains 'assert'
        if 'assert' in line:
            # Add the line to the list
            assertions_list.append(line.strip())

    return assertions_list

def _insert_assertions(input):
    for i in range(len(input)):
        if input[i].isdigit():
            #replace with random number
            random_num = str(random.randint(0, 100))
            input = input[:i] + random_num + input[i+1:]
            break
    pattern = r'\((\d+)\)'

    matches = re.findall(pattern, input)

    if matches:
        number_in_parentheses = int(matches[0])
        for i in range(len(input)):
            if input[i] == "=":
                new_word = num2words(number_in_parentheses)
                new_word = new_word.replace("-", " ")
                new_word = new_word.title()
                input = input[:i+1] + "= " + '"' + new_word + '"'
                break

    return input

def fuzz(func):
    #loop over each line

    lines = func.split('\n')

    for line in lines:
        # Check if the line contains 'assert'
        if 'assert' in line:
            # Add the line to the list
            new_line = _insert_assertions(line.strip())
            lines.append(new_line+'\n')

    new_func = '\n'.join(lines)
    return new_func

def _insert_assertions2(input):
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(1, 10)))
    for i in range(len(input)):
        if input[i] == "(":
            input = input[:i] + "('" + random_str + "') "
            new_num = strong_password_checker(random_str)
            input += "== " + str(new_num)
            return input

def fuzz2(func):
    #this function to fuzz the assertions of the testing of the function strong_password_checker
    lines = func.split('\n')
    new_lines = []
    for line in lines:
        # Check if the line contains 'assert'
        if 'assert' in line:
            # Add the line to the list
            line = line.strip()
            new_line = _insert_assertions2(line)
            new_lines.append('    '+new_line)
    new_lines = lines + new_lines
    new_func = '\n'.join(new_lines)
    new_func = '\n'.join([line for line in new_func.strip().split('\n') if line.strip() != ''])
    return new_func

if __name__ == "__main__":
    # Configure the generative AI with the API key
    genai.configure(api_key=key)

    # Create a generative model
    model = genai.GenerativeModel('gemini-pro')

    #function_to_test = number_to_words #file_name_check
    function_to_test = strong_password_checker


    ######Generate intial tests with LLM

    test, coverage_data = generate_inital_tests_with_llm(model, function_to_test)

    initial_coverage = coverage_data

    # define the executor to be used with your test generator
    executor = AbstractExecutor(function_to_test)

    try:

        """
        TODO:
        -Insert your code here to improve the initial line and branch coverage
        -Use the "test" returned from the generate_inital_tests_with_llm function to start your generation
        -You can leverage the information about the datatype from the inputs in "test" generated by the LLM
        -You must use the "executor" to evaluate your tests and guide the generation process
        -Your test generator shoud return a list with new inputs to be evaluated
        -You goal is to keep the number of inputs as small as possible and the coverage as high as possible
        """

        test_assertions = inspect.getsource(test)
        new_func = fuzz2(test_assertions) #change to fuzz() for number_to_words
        #write new_func to a file
        with open("new_inputs.py", "w") as f:
            f.write(new_func)

        filename = "new_inputs.py"

        # Get the module name and function name from the filename
        module_name = filename.split(".")[0]
        function_name = "test_" + function_to_test.__name__

        # Import the module dynamically
        module = importlib.import_module(module_name)

        # Get the function from the module
        function = getattr(module, function_name)
        new_inputs_list = [inspect.getsource(function)]

    except Exception as e:
        print(f"Exception occured: {e}")


    coverage_data = executor._execute_input(input_list=new_inputs_list)

    print(f"Initial coverage: {initial_coverage['coverage']}")
    print(f"Final coverage: {coverage_data['coverage']}")

    line_coverage_improment = coverage_data["coverage"]["percent_covered"] - initial_coverage["coverage"]["percent_covered"]
    branch_coverage_improment = coverage_data["coverage"]["covered_branches"]/coverage_data["coverage"]["num_branches"] - initial_coverage["coverage"]["covered_branches"]/initial_coverage["coverage"]["num_branches"]
    total_tests = len(new_inputs_list)
    final_score = (line_coverage_improment + branch_coverage_improment) / total_tests
    print(f"Final score: {final_score}")