# 🌍 AI Travel Planner with LangChain

A conversational AI travel assistant powered by LangChain and GPT-4 that helps you plan trips, check weather, and find events through natural language conversations.

## ✨ Features

- **Chat Interface**: Talk to the AI in natural language about your travel plans
- **Smart Trip Planning**: Uses LangChain agents to coordinate multiple tools
- **Weather Forecasts**: Get accurate weather predictions for any location and date range
- **Event Discovery**: Find local events and activities at your destination
- **Date-Aware**: Understands relative dates and handles year transitions (e.g., "December to January")
- **Contextual Memory**: Remembers your conversation for more natural interactions

## 🛠️ Tech Stack

- **LangChain**: AI agent framework
- **OpenAI GPT-4**: Natural language understanding and generation
- **Streamlit**: Web interface
- **Open-Meteo API**: Free weather data
- **Pydantic**: Data validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-travel-planner
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your OpenAI API key:
   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

### Running the App

Start the Streamlit application:
```bash
streamlit run ai_travel_planner/app.py
```

Then open your browser to the URL shown in the terminal (usually http://localhost:8501).

## 💬 How to Use (It's a Conversation!)

1. **Start Chatting** - Just type naturally like you're talking to a travel agent
2. **Ask About Anything** - The AI understands travel-related questions and requests
3. **Get Detailed Responses** - The AI will ask follow-up questions if needed

### Example Conversation

**You:** I'm thinking of going to Paris this December

**AI:** That sounds wonderful! I can help plan your Paris trip. When in December were you thinking of going, and how long will you be staying?

**You:** From December 20th to 27th

**AI:** Great! Let me check the weather for that time... [weather info] Would you like me to suggest some holiday events in Paris during your stay?

**You:** Yes, and I love museums

**AI:** Perfect! Here are some museum exhibitions in December... [event info] Would you like me to create a daily itinerary that includes these?

## 🧠 How the Conversation Works

The AI uses LangChain to:
1. **Understand** your messages in natural language
2. **Choose Tools** - Decides when to check weather, find events, or plan itineraries
3. **Remember Context** - Keeps track of our conversation
4. **Respond Naturally** - Like a knowledgeable travel assistant

## 📂 Project Structure

```
ai_travel_planner/
├── app.py            # Streamlit chat interface
├── langchain_planner.py  # Core LangChain agent and tools
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests or contribute to the project.
   - Interests (e.g., food, nature, museums)
   - Budget level