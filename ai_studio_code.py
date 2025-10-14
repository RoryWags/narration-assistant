import google.generativeai as genai
import os

# Configure the API key. It will look for GOOGLE_API_KEY environment variable by default.
# Alternatively, you can pass it directly: genai.configure(api_key="YOUR_API_KEY_HERE")
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set it to your actual API key before running the script.")
    exit()

print("Available Generative AI Models (supporting generateContent):")
print("-" * 60)

try:
    # List all models
    for m in genai.list_models():
        # Filter for models that support the 'generateContent' method
        # This is the method used for chat and text generation with Gemini models
        if "generateContent" in m.supported_generation_methods:
            print(f"Model Name: {m.name}")
            print(f"  Description: {m.description}")
            print(f"  Input Token Limit: {m.input_token_limit}")
            print(f"  Output Token Limit: {m.output_token_limit}")
            print(f"  Supported Methods: {m.supported_generation_methods}")
            print("-" * 60)

except Exception as e:
    print(f"An error occurred while listing models: {e}")
    print("Please check your API key and network connection.")