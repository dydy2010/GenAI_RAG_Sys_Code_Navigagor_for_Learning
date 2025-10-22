# This file contains the test questions and the ideal "ground truth" answers.
# This is template questions and answers for judging the RAG system's performance.

test_questions = [
    {
        "question": "What is the key difference between a t-test and a z-test according to the lecture slides?",
        "ground_truth": "A t-test is used when the true standard deviation of the population is unknown and must be estimated from the data, which is almost always the case in practice. A z-test, on the other hand, assumes the true standard deviation is known.",
        "ground_truth_context": ["So far: Procedure is called z-test. Tacitly assumed: Standard deviation known. In practice: Never the case... Following t-test: Does not assume true standard deviation"]
    },
    {
        "question": "Show me a simple Python example of converting temperature from Fahrenheit to Celsius.",
        "ground_truth": """You can convert from Fahrenheit to Celsius with the formula: result = int(round((degree - 32) * 5 / 9)). For example:
```python
temp = "102F"
degree = int(temp[:-1]) # 102
i_convention = temp[-1] # 'F'
if i_convention.upper() == "F":
    result = int(round((degree - 32) * 5 / 9)) # result will be 39
    o_convention = "Celsius"
```""",
        "ground_truth_context": ["if i_convention.upper() == \"F\":\n    result = int(round((degree - 32) * 5 / 9))\n    o_convention = \"Celsius\""]
    },
    {
        "question": "What is a paired sample in statistics?",
        "ground_truth": "A paired sample is when each observation in one group can be clearly assigned to a specific observation in another group, because the same experimental unit is measured twice (e.g., before and after a treatment). This means the sample sizes must be the same.",
        "ground_truth_context": ["Paired Samples: Each observation of one group can be clearly assigned to an observation of the other group. Sample size is inevitably same in both groups."]
    },
    {
        "question": "How do you define a function in Python?",
        "ground_truth": "A function is defined using the `def` keyword, followed by the function name and a list of parameters in parentheses. The function body is indented and contains the instructions to be executed.",
        "ground_truth_context": ["Function is defined with: def", "def function_name(parameter, list):"]
    },
    {
        "question": "How can I handle an IndexError in Python when accessing a list element?",
        "ground_truth": "You can handle an IndexError by using a try-except block. The code that might raise the error is placed in the `try` block, and the code to execute if the error occurs is placed in the `except IndexError` block.",
        "ground_truth_context": ["Catch the IndexError that is raised if the position p is out of index range and print the error message 'string index out of range' instead.", "except IndexError:\n           print(\"string index out of range\")"]
    },
    {
        "question": "What is the purpose of the 'finally' block in a Python try-except clause?",
        "ground_truth": "The `finally` block is optional and its code is always interpreted at the end of the try-except clause, regardless of whether an error was raised or not.",
        "ground_truth_context": ["finally: always interpreted at the end of the clause (optional if except block available)"]
    },
    {
        "question": "Can Linear Models be used to model non-linear relationships?",
        "ground_truth": "Yes, Linear Models can model non-linear relationships. This can be done by including non-linear transformations of the predictor variables, such as polynomials (e.g., x^2) or logarithms (e.g., log(x)), in the model formula. The model is still considered 'linear' because it is linear in its coefficients.",
        "ground_truth_context": ["Linear Models CAN MODEL NON-LINEAR RELATIONSHIPS.", "y = beta_0 + beta_1*x_1 + beta_2*x_1^2 + beta_3*log(x_2) + epsilon"]
    },
    {
        "question": "How do you load a CSV file into a pandas DataFrame?",
        "ground_truth": "You can load a CSV file into a pandas DataFrame using the `pd.read_csv()` function. You need to provide the path to the CSV file as an argument.",
        "ground_truth_context": ["d_trees = pd.read_csv(\"../../Datasets/TreesChamagne2017_Lab_modified.csv\", sep = ';', decimal = ',')"]
    },
    {
        "question": "What is the purpose of the `assert` statement in Python?",
        "ground_truth": "The `assert` statement is a convenient way to insert debugging assertions into a program. It checks if a condition is true, and if not, it raises an AssertionError. It is primarily used for sanity checks during development and testing.",
        "ground_truth_context": ["Assert statements are a convenient way to insert debugging assertions into a program", "asserts can be useful for sanity checks in development, testing, and debugging phase."]
    },
    {
        "question": "How do you create a boxplot for different species using seaborn?",
        "ground_truth": "You can create a boxplot using seaborn's `boxplot` function. You specify the categorical variable for the x-axis (e.g., 'species'), the numerical variable for the y-axis (e.g., 'growth_rate'), and the DataFrame containing the data.",
        "ground_truth_context": ["sns.boxplot(x = 'species', y = 'growth_rate', data = d_trees)"]
    }
]
