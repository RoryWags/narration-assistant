import os
import json
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=api_key)

app = Flask(__name__)

# MODIFIED: Added book_description parameter
def analyze_narration_text_with_gemini(text, creativity_level='balanced', narrator_style='neutral storyteller', book_description=''):
    # Define instructions for the new parameters
    creativity_instructions = {
        'subtle': "You should be conservative with your annotations. Use the 'normal' type frequently and only add performance suggestions for the most impactful moments.",
        'balanced': "You should provide a healthy mix of performance suggestions and 'normal' text, ensuring a dynamic but not overly dramatic reading.",
        'dramatic': "You should be very liberal with your annotations. Use a wide variety of performance types and avoid using 'normal' unless absolutely necessary to create a highly emotive performance."
    }
    
    style_instructions = {
        'neutral storyteller': "Your suggestions should create a clear, objective, and engaging narration without a strong character bias.",
        'grave detective': "Your suggestions should evoke a sense of mystery, seriousness, and suspense. Favor 'lower-pitch', 'slow-down', and 'emphasize' to build tension.",
        'energetic youth': "Your suggestions should be full of energy and excitement. Favor 'speed-up', 'raise-pitch', and exclamation.",
        'calm mentor': "Your suggestions should create a feeling of wisdom, patience, and reassurance. Favor 'slow-down', gentle tones, and thoughtful pauses."
    }

    # NEW: Conditionally create a context string if a book description is provided
    context_prompt_section = ""
    if book_description and book_description.strip():
        context_prompt_section = f"""
    **BOOK CONTEXT:**
    Use the following book description to inform your suggestions, matching the overall tone and message:
    "{book_description}"
    """

    # MODIFIED: The prompt now includes the optional book context
    prompt = f"""
    You are a world-class, award-winning voice actor and narration director.
    Your task is to analyze a manuscript and provide creative performance suggestions as a JSON array.

    **YOUR PERSONA:**
    You must embody the persona of a **{narrator_style}**. {style_instructions.get(narrator_style, "")}

    **CREATIVITY GUIDELINE:**
    Your level of annotation activity should be **{creativity_level}**. {creativity_instructions.get(creativity_level, "")}
    {context_prompt_section}
    **CRITICAL RULE:** The concatenation of all "text" fields in your final JSON array must exactly match the original manuscript text, including all whitespace and newlines.

    **ANALYSIS INSTRUCTIONS:**
    1.  **Annotation Type**: Choose ONE from: 'speed-up', 'slow-down', 'emphasize', 'raise-pitch', 'lower-pitch', 'whisper', 'pause', 'normal'.
    2.  **Feedback**: A short, one-sentence explanation for your choice, aligned with your persona.
    3.  **Emotion Emoji**: A single emoji: , 个, 丐, 亞, ､ Use "" if no strong emotion is present.

    You MUST return your response as a valid JSON array of objects. Each object must have these exact keys: "text", "type", "feedback", and "emotion_emoji".

    Now, analyze this manuscript:
    ---
    {text}
    """

    try:
        model = genai.GenerativeModel('gemini-pro-latest')
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            temperature=0.7 
        )
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        response = model.generate_content(
            prompt, 
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        analysis_result = json.loads(response.text)
        return analysis_result

    except Exception as e:
        print(f"An error occurred with the Gemini API or JSON parsing: {e}")
        return [{ 
            "text": f"Sorry, an error occurred during AI analysis. Details: {e}", 
            "type": "normal", 
            "feedback": "There was a problem generating the performance script. Please try uploading the file again.", 
            "emotion_emoji": "个" 
        }]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    # Extract settings from the request, with defaults
    text = data['text']
    creativity = data.get('creativity_level', 'balanced')
    style = data.get('narrator_style', 'neutral storyteller')
    # MODIFIED: Get the book_description from the request
    description = data.get('book_description', '')
    
    # MODIFIED: Pass the description to the Gemini function
    analysis_result = analyze_narration_text_with_gemini(text, creativity, style, description)
    return jsonify(analysis_result)

if __name__ == '__main__':
    app.run(debug=True)