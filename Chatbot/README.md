# AI Budget Travel Assistant

A smart chatbot that helps you plan your trips while staying within your budget. This AI-powered assistant uses Google's Gemini model to provide personalized travel recommendations, budget-friendly accommodations, transportation options, and local attractions.

## Features

- Interactive web-based chat interface
- Budget-aware travel recommendations using Gemini AI
- Customizable travel preferences
- Real-time AI responses
- Modern and responsive UI with Tailwind CSS

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
4. Run the Flask application:
   ```bash
   python app.py
   ```
5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Set your travel preferences in the sidebar:
   - Budget (USD)
   - Travel style (Backpacker, Budget, Comfort, Luxury)
   - Trip duration (days)

2. Start chatting with the AI assistant about your travel plans
3. Ask questions about:
   - Destination recommendations
   - Budget accommodations
   - Transportation options
   - Local attractions
   - Food recommendations
   - Money-saving tips

## Requirements

- Python 3.7+
- Google API key for Gemini
- Internet connection

## Note

Make sure to keep your Google API key secure and never share it publicly. 