from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Gemini with API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Initialize chat history
chat_history = []

def format_currency(amount):
    """Format amount in Indian Rupees"""
    return f"₹{amount:,}"

def format_response(text):
    """Format the AI response to be more readable and interactive"""
    # Remove asterisk symbols and replace with proper bullet points
    text = re.sub(r'\*', '•', text)
    
    # Add proper spacing after periods
    text = re.sub(r'\. ', '.\n\n', text)
    
    # Add line breaks before headings and bullet points
    text = re.sub(r'\n([A-Z][^.!?]*:)', r'\n\n\1', text)
    text = re.sub(r'\n([•\-\*])', r'\n\n\1', text)
    
    # Add line breaks before transition words
    text = re.sub(r'\n(However|Moreover|Additionally|Furthermore|In addition|Also|Besides|On the other hand|In contrast|Nevertheless|Therefore|Thus|Consequently|As a result|For example|For instance|Specifically|In particular|Notably|In fact|Indeed|To illustrate|To demonstrate|To clarify|To summarize|In conclusion|Finally|In short|In brief|To put it simply|To put it differently|In other words|That is to say|To be precise|To be exact|To be specific|To be clear|To be sure|To be certain|To be fair|To be honest|To be frank|To be direct|To be straightforward|To be blunt)', r'\n\n\1', text)
    
    # Add extra spacing between paragraphs
    text = re.sub(r'\n\n+', '\n\n', text)
    
    # Format headings with custom styling
    text = re.sub(r'([A-Z][^.!?]*:)', r'<h3 class="text-indigo-600 font-semibold text-xl mb-3 pb-2 border-b-2 border-indigo-200">\1</h3>', text)
    
    # Format bullet points with custom styling
    text = re.sub(r'([•\-\*])\s*([^\n]+)', r'<li class="flex items-start mb-2"><span class="text-indigo-500 mr-2">•</span><span>\2</span></li>', text)
    text = re.sub(r'(<li class="flex items-start mb-2">.*?</li>\n?)+', r'<ul class="list-none space-y-2 my-4">\g<0></ul>', text)
    
    # Format numbered lists
    text = re.sub(r'(\d+\.)\s*([^\n]+)', r'<li class="flex items-start mb-2"><span class="text-indigo-500 mr-2">\1</span><span>\2</span></li>', text)
    text = re.sub(r'(<li class="flex items-start mb-2">.*?</li>\n?)+', r'<ol class="list-decimal list-inside space-y-2 my-4">\g<0></ol>', text)
    
    # Format monetary values with custom styling
    text = re.sub(r'₹(\d+(?:,\d+)*(?:\.\d{2})?)', r'<span class="highlight bg-yellow-100 text-yellow-800 font-medium px-2 py-1 rounded">₹\1</span>', text)
    
    # Add emojis for common travel-related terms
    emoji_map = {
        r'\b(flight|airplane|airport)\b': '✈️',
        r'\b(hotel|accommodation|stay|resort)\b': '🏨',
        r'\b(food|restaurant|cuisine|dining)\b': '🍽️',
        r'\b(beach|sea|ocean|coast)\b': '🏖️',
        r'\b(mountain|hiking|trek)\b': '⛰️',
        r'\b(temple|church|mosque|religious)\b': '🕌',
        r'\b(museum|gallery|art)\b': '🏛️',
        r'\b(shopping|market|mall)\b': '🛍️',
        r'\b(nightlife|party|club)\b': '🌙',
        r'\b(nature|park|garden)\b': '🌳',
        r'\b(adventure|exciting|thrill)\b': '🎯',
        r'\b(relax|peaceful|tranquil)\b': '😌',
        r'\b(budget|cheap|affordable)\b': '💰',
        r'\b(luxury|expensive|premium)\b': '💎',
        r'\b(culture|traditional|heritage)\b': '🏺',
        r'\b(transport|bus|train|metro)\b': '🚌',
        r'\b(weather|sunny|rainy)\b': '☀️',
        r'\b(safety|secure|protected)\b': '🛡️',
        r'\b(booking|reservation)\b': '📅',
        r'\b(recommend|suggest|advise)\b': '💡'
    }
    
    for pattern, emoji in emoji_map.items():
        text = re.sub(pattern, f'{emoji} \\1', text, flags=re.IGNORECASE)
    
    # Add custom styling for paragraphs
    text = re.sub(r'<p>(.*?)</p>', r'<p class="text-gray-700 leading-relaxed mb-4">\1</p>', text)
    
    # Add custom styling for important information
    text = re.sub(r'<strong>(.*?)</strong>', r'<span class="font-semibold text-indigo-700">\1</span>', text)
    
    # Add custom styling for links
    text = re.sub(r'<a href="(.*?)">(.*?)</a>', r'<a href="\1" class="text-blue-600 hover:text-blue-800 underline">\2</a>', text)
    
    # Wrap the entire response in a container with custom styling
    text = f'<div class="formatted-response space-y-4">{text}</div>'
    
    return text

def get_ai_response(user_input, budget, travel_style, trip_duration):
    """Get response from Google's Gemini model"""
    try:
        # Format budget in Indian Rupees
        formatted_budget = format_currency(budget)
        
        # Create a context-aware prompt
        prompt = f"""You are a budget travel assistant specializing in Indian travel. 
        The user's preferences are:
        - Budget: {formatted_budget}
        - Travel Style: {travel_style}
        - Trip Duration: {trip_duration} days

        Please provide a detailed response with:
        1. Clear headings for each section
        2. Bullet points for lists
        3. Specific budget breakdowns
        4. Local tips and recommendations
        5. Safety considerations
        6. Best time to visit
        7. Must-try local experiences

        Format your response to be engaging and easy to read.
        Use Indian Rupees (₹) for all monetary values.
        Include specific examples and personal touches.
        Make recommendations based on the user's budget and preferences.

        User's question: {user_input}"""

        response = model.generate_content(prompt)
        formatted_response = format_response(response.text)
        
        # Add the conversation to chat history
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": formatted_response})
        
        # Store the latest preferences in session
        session['latest_preferences'] = {
            'budget': formatted_budget,
            'travel_style': travel_style,
            'trip_duration': trip_duration,
            'generation_date': datetime.now().strftime("%B %d, %Y %I:%M %p")
        }
        
        return formatted_response
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    # Clear session data when returning to home
    session.clear()
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    budget = data.get('budget', 100000)  # Default to 100,000 INR
    travel_style = data.get('travel_style', 'Budget')
    trip_duration = data.get('trip_duration', 7)

    # Get AI response
    ai_response = get_ai_response(user_message, budget, travel_style, trip_duration)

    return jsonify({
        "response": ai_response,
        "has_response": True
    })

@app.route('/response')
def view_response():
    # Get the latest preferences from session
    preferences = session.get('latest_preferences', {
        'budget': format_currency(100000),
        'travel_style': 'Budget',
        'trip_duration': 7,
        'generation_date': datetime.now().strftime("%B %d, %Y %I:%M %p")
    })
    
    return render_template('response.html',
                         chat_history=chat_history,
                         budget=preferences['budget'],
                         travel_style=preferences['travel_style'],
                         trip_duration=preferences['trip_duration'],
                         generation_date=preferences['generation_date'])

if __name__ == '__main__':
    app.run(debug=True) 