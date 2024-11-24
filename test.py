import requests
import concurrent.futures


code = """#include<stdio.h>
int main(){

printf("mohamed");
return 0;}
"""
language = "cpp"

# Define the function to send a single request
def send_request():
    url = 'http://localhost:5000/run_code'
    payload = {
        'code': code,
        'language': language
    }
    response = requests.post(url, json=payload,timeout=20)
    
    # Parse and extract the output
    result = response.json()
    output = result.get('output')
    return output

# Use ThreadPoolExecutor to send 50 requests concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    # Send 50 requests
    futures = [executor.submit(send_request) for _ in range(50)]

    # Wait for all futures to complete and print results
    for future in concurrent.futures.as_completed(futures):
        try:
            output = future.result()
            print(output)
        except Exception as e:
            print(f"Request failed: {e}")
