import requests
import concurrent.futures

# Example function code for C++
code = """
const readline = require('readline');

// Define the function to concatenate two strings
function andFunction(a, b) {
    return a + b;  // Concatenate the two strings
}

// Create readline interface to read input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Read inputs from stdin (formatted as "a,b")
process.stdin.once('data', (input) => {
    const inputStr = input.toString().trim(); // Get the input string
    const [a, b] = inputStr.split(',');  // Split the input at the comma

    // Check if the input format is correct
    if (a === undefined || b === undefined) {
        console.error("Invalid input format. Expected two strings separated by a comma.");
        rl.close();
        return;
    }

    // Call the function
    const result = andFunction(a, b);

    // Print the result
    console.log(result);

    // Close the readline interface
    rl.close();
});
"""

# Language
language = "javascript"

# Test cases
test_cases = [
    {"inputs": "apple,banana", "expected_output": "applebanana"},
    {"inputs": "20,20", "expected_output": "2020"},
]

# Define the function to send a single request
def send_request(test_case):
    url = 'http://localhost:8000/run-code'  # Ensure this is the correct endpoint
    payload = {
        'code': code,
        'language': language,
        'stdin': str(test_case['inputs'])  # Pass inputs as JSON string
    }
    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_data = response.json()

        # Extract and validate results
        actual_output = response_data.get("stdout", "").strip()
        is_correct = actual_output == str(test_case['expected_output'])
        return {
            "inputs": test_case["inputs"],
            "expected_output": test_case["expected_output"],
            "actual_output": actual_output,
            "is_correct": is_correct,
            "stderr": response_data.get("stderr", "").strip(),
        }
    except requests.exceptions.HTTPError as http_err:
        return {
            "inputs": test_case["inputs"],
            "expected_output": test_case["expected_output"],
            "error": f"HTTP error occurred: {http_err}"
        }
    except Exception as e:
        return {
            "inputs": test_case["inputs"],
            "expected_output": test_case["expected_output"],
            "error": str(e)
        }

# Use concurrent execution to send multiple requests
def run_tests():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(send_request, test_cases))

    # Print the results
    for result in results:
        print(result)

# Run the tests
if __name__ == "__main__":
    run_tests()
