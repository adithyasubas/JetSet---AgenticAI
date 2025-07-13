import os
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_planner import LangChainTravelPlanner
import asyncio

# Load environment variables
load_dotenv()

# Initialize the LangChain Travel Planner
planner = LangChainTravelPlanner()

def format_trip_request(destination, start_date, end_date, interests, budget, num_travelers):
    """Format the trip request into a natural language prompt."""
    interests_str = ", ".join(interests)
    duration = (end_date - start_date).days
    
    return f"""
    I'm planning a trip to {destination} from {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')} 
    ({duration} days). There will be {num_travelers} traveler(s).
    
    Interests: {interests_str}
    Budget: {budget}
    
    Please provide:
    1. A detailed daily itinerary
    2. Weather forecast for the travel dates
    3. Any interesting events or activities happening during my stay
    """

async def main():
    st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")
    
    st.title("✈️ AI Travel Planner")
    st.write("Plan your perfect trip with AI assistance!")
    
    # Check for required API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("❌ OpenAI API key is required. Please check your .env file and restart the application.")
        st.stop()
    
    # Initialize session state for chat history if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your AI travel assistant. Where would you like to go?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Tell me about your dream trip..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Get assistant response
            try:
                # Prepare the input for the agent
                agent_input = {
                    "input": prompt,
                    "chat_history": [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages[:-1]  # Exclude the current message
                        if msg["role"] in ["user", "assistant"]
                    ]
                }
                
                response = await planner.plan_trip(agent_input)
                if response["success"]:
                    full_response = response["data"]
                else:
                    full_response = f"I encountered an error: {response['error']}"
            except Exception as e:
                full_response = f"An error occurred: {str(e)}"
            
            # Display the response
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Run the app
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
