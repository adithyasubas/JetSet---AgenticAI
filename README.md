# AI Travel Planner

A multi-agent AI system that helps users plan their trips by gathering real-time data about weather, events, and places to create personalized travel itineraries.

## Features

- **Interactive Web Interface**: Built with Streamlit for an easy-to-use experience
- **AI-Powered Planning**: Uses OpenAI's GPT-4 to generate personalized travel plans
- **Real-Time Weather Data**: Fetches up-to-date weather forecasts for your travel dates
- **Local Events**: Finds interesting events and activities at your destination
- **Customizable Itineraries**: Tailored to your interests, budget, and travel style

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- OpenWeatherMap API key
- Ticketmaster API key (optional, for local events)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-travel-planner
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your API keys:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file and replace the placeholder values with your actual API keys.

## Usage

1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

3. Fill in your travel details:
   - Destination (city and country)
   - Travel dates
   - Number of travelers
   - Interests (e.g., food, nature, museums)
   - Budget level

4. Click "Plan My Trip!" and wait for your personalized itinerary to be generated.

## Project Structure

```
ai-travel-planner/
├── agents/                    # AI agent implementations
│   ├── __init__.py
│   ├── base_agent.py         # Base class for all agents
│   ├── planner_agent.py      # Creates the initial travel plan
│   ├── weather_agent.py      # Fetches weather forecasts
│   ├── event_agent.py        # Finds local events
│   └── summary_agent.py      # Compiles the final itinerary
├── data/                     # Data storage (if needed)
├── utils/                    # Utility functions
├── .env.example              # Example environment variables
├── app.py                    # Main Streamlit application
├── README.md                 # This file
└── requirements.txt          # Python dependencies
```

## Configuration

You can customize the application by modifying the following environment variables in your `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENWEATHER_API_KEY`: Your OpenWeatherMap API key (required)
- `TICKETMASTER_API_KEY`: Your Ticketmaster API key (optional)
- `DEBUG`: Set to `True` for development, `False` for production
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## API Keys

1. **OpenAI API Key**:
   - Sign up at [OpenAI](https://platform.openai.com/signup)
   - Create an API key in the [API Keys](https://platform.openai.com/account/api-keys) section

2. **OpenWeatherMap API Key**:
   - Sign up at [OpenWeatherMap](https://home.openweathermap.org/users/sign_up)
   - Get your API key from [API keys](https://home.openweathermap.org/api_keys)

3. **Ticketmaster API Key (optional)**:
   - Sign up at [Ticketmaster Developer Portal](https://developer.ticketmaster.com/)
   - Create an application and get your API key

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/)
- Weather data provided by [OpenWeatherMap](https://openweathermap.org/)
- Event data provided by [Ticketmaster](https://developer.ticketmaster.com/)