from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field
from typing import Tuple
import re
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import requests
import os

# Date parsing utilities
def parse_date_with_reference(date_str: str, reference_date: date = None) -> date:
    """Parse a date string that might be missing year information.
    
    Args:
        date_str: Date string in formats like 'December 23', 'Dec 23', '12/23'
        reference_date: Reference date to determine the year (defaults to today)
        
    Returns:
        A date object with the correct year
    """
    if reference_date is None:
        reference_date = date.today()
        
    # Try different date formats
    formats = [
        (r'(?P<month>\w+)\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?', '%B %d'),  # December 23
        (r'(?P<month>\w+)\s+(?P<day>\d{1,2})', '%B %d'),                    # December 23rd
        (r'(?P<month>\d{1,2})/(?P<day>\d{1,2})', '%m/%d'),                   # 12/23
    ]
    
    for pattern, date_format in formats:
        match = re.match(pattern, date_str, re.IGNORECASE)
        if match:
            try:
                # Parse the date with the current year
                parsed_date = datetime.strptime(f"{match.group('month')} {match.group('day')} {reference_date.year}", 
                                             f"%B %d %Y").date()
                
                # If the date is in the past, assume it's for next year
                if parsed_date < reference_date and (reference_date.month, reference_date.day) != (12, 31):
                    parsed_date = parsed_date.replace(year=reference_date.year + 1)
                return parsed_date
            except (ValueError, AttributeError):
                continue
    
    # If no format matched, try to parse with dateutil (more lenient)
    try:
        from dateutil import parser
        parsed_date = parser.parse(date_str, default=reference_date).date()
        if parsed_date < reference_date and (reference_date.month, reference_date.day) != (12, 31):
            parsed_date = parsed_date.replace(year=reference_date.year + 1)
        return parsed_date
    except (ImportError, ValueError):
        pass
    
    # If all else fails, return the reference date
    return reference_date

# Pydantic models for type safety
class WeatherInput(BaseModel):
    location: str = Field(..., description="City and country (e.g., 'Paris,France')")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    
    class Config:
        arbitrary_types_allowed = True

class EventInput(BaseModel):
    location: str = Field(..., description="City and country (e.g., 'Paris,France')")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    category: Optional[str] = Field(None, description="Event category (e.g., 'music', 'sports')")
    
    class Config:
        arbitrary_types_allowed = True

class ItineraryDay(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    activities: List[str] = Field(..., description="List of activities for the day")
    
    class Config:
        arbitrary_types_allowed = True

class Itinerary(BaseModel):
    destination: str = Field(..., description="Travel destination")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    days: List[ItineraryDay] = Field(..., description="Daily itinerary")
    
    class Config:
        arbitrary_types_allowed = True

# Weather Tool
@tool(args_schema=WeatherInput)
async def get_weather_forecast(location: str, start_date: str, end_date: str) -> str:
    """Get weather forecast for a location and date range.
    
    Args:
        location: City and country (e.g., 'Paris,France')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    try:
        # Use Open-Meteo API
        base_url = "https://api.open-meteo.com/v1/forecast"
        
        # First get coordinates
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": location,
            "count": 1,
            "format": "json"
        }
        
        geo_response = requests.get(geo_url, params=geo_params, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data.get('results'):
            return f"Location '{location}' not found"
        
        location_data = geo_data['results'][0]
        lat = location_data['latitude']
        lon = location_data['longitude']
        
        # Get weather data
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["weathercode", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": "auto"
        }
        
        response = requests.get(base_url, params=weather_params, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        
        # Format the response
        days = []
        for i, date_str in enumerate(weather_data['daily']['time']):
            days.append(
                f"{date_str}: "
                f"High: {weather_data['daily']['temperature_2m_max'][i]}°C, "
                f"Low: {weather_data['daily']['temperature_2m_min'][i]}°C, "
                f"Precipitation: {weather_data['daily']['precipitation_sum'][i]}mm"
            )
        
        return f"Weather forecast for {location}:\n" + "\n".join(days)
    
    except Exception as e:
        return f"Error getting weather data: {str(e)}"

# Event Tool (simplified version)
@tool(args_schema=EventInput)
async def find_events(location: str, date: str, category: str = None) -> str:
    """Find events in a location on a specific date.
    
    Args:
        location: City and country (e.g., 'Paris,France')
        date: Date in YYYY-MM-DD format
        category: Optional event category (e.g., 'music', 'sports')
    """
    # This is a simplified version - in a real app, you'd query an events API
    return f"""Events in {location} on {date}:
- Local festival
- Museum exhibition
- Guided city tour
- {category.capitalize() + ' event' if category else 'Local market'}"""

# Itinerary Planning Tool
@tool
async def create_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    interests: List[str],
    budget: str
) -> str:
    """Create a travel itinerary based on destination, dates, interests, and budget."""
    # In a real implementation, this would use the LLM to generate an itinerary
    return f"""
    Suggested itinerary for {destination} from {start_date} to {end_date}:
    - Day 1: Arrival and city orientation
    - Day 2: Visit main attractions
    - Day 3: Day trip to nearby locations
    - Day 4: Local experiences
    - Day 5: Departure
    
    Interests: {', '.join(interests)}
    Budget: {budget}
    """

class LangChainTravelPlanner:
    def __init__(self):
        # Initialize the language model
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Set up tools
        self.tools = [
            get_weather_forecast,
            find_events,
            create_itinerary
        ]
        
        # Define the system message
        current_date = date.today().strftime("%B %d, %Y")
        system_message = f"""You are a helpful travel assistant that helps users plan their trips. 
        You can provide weather forecasts, find events, and create detailed itineraries.
        Be friendly, informative, and provide useful recommendations.
        
        IMPORTANT DATE HANDLING INSTRUCTIONS:
        - Today is {current_date}
        - When users mention dates without a year, assume they mean the next occurrence of that date.
        - For date ranges that cross into a new year (e.g., December to January), 
          ensure the year transitions correctly.
        - Always confirm the dates you're using for planning to avoid confusion."""
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        
        # Create the agent executor without memory (we'll handle it manually)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        # Initialize chat history
        self.chat_history = []
    
    async def plan_trip(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to handle trip planning requests.
        
        Args:
            request_data: Dictionary containing 'input' and 'chat_history' keys
            
        Returns:
            Dictionary with 'success' status and 'data' or 'error' message
        """
        try:
            user_input = request_data.get("input", "")
            
            # Pre-process the input to handle dates
            current_date = date.today()
            date_patterns = [
                r'(?:from\s+|between\s+)?(?:the\s+)?(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s*,\s*\d{4})?(?:\s+to|\s*-\s*)(?:the\s+)?(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s*,\s*\d{4})?',
                r'(\d{1,2})[/-](\d{1,2})(?:[/-]\d{{2,4}})?(?:\s*to|-|through\s*)(\d{1,2})[/-](\d{1,2})(?:[/-]\d{{2,4}})?',
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    # If we find a date range, we'll let the LLM handle it with the context
                    # from the system message about current date
                    break
            
            # Update chat history
            self.chat_history.extend([
                HumanMessage(content=msg["content"]) if msg["role"] == "user" 
                else AIMessage(content=msg["content"])
                for msg in request_data.get("chat_history", [])
            ])
            
            # Format the prompt with the current chat history
            messages = self.prompt.format_messages(
                input=user_input,
                chat_history=self.chat_history,
                agent_scratchpad=[]
            )
            
            # Invoke the agent
            response = await self.agent_executor.ainvoke({"input": messages})
            
            # Add the AI's response to chat history
            if response and "output" in response:
                self.chat_history.append(AIMessage(content=response["output"]))
                return {
                    "success": True,
                    "data": response["output"]
                }
            else:
                return {
                    "success": False,
                    "error": "No valid response from the agent."
                }
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {
                "success": False,
                "error": f"Error in plan_trip: {str(e)}\n\n{error_trace}"
            }

# Example usage
async def main():
    # Initialize the planner
    planner = LangChainTravelPlanner()
    
    # Example conversation
    print("Travel Planner: Hi! I'm your travel assistant. How can I help you plan your trip?")
    print("You can ask about weather, events, or request an itinerary. Type 'quit' to exit.")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nTravel Planner: Safe travels! Have a great trip!")
                break
                
            response = await planner.plan_trip(user_input)
            if response["success"]:
                print(f"\nTravel Planner: {response['data']}")
            else:
                print(f"\nSorry, I encountered an error: {response['error']}")
        except KeyboardInterrupt:
            print("\n\nTravel Planner: Goodbye! Have a great trip!")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
