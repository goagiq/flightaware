import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import httpx
import asyncio
import logging
from typing import Optional
import gradio as gr

# to use Google Colab Secrets
# from google.colab import userdata

# Configure logging to write to a file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# FlightAware API base URL and headers
FLIGHTAWARE_BASE_URL = "https://aeroapi.flightaware.com/aeroapi/flights/"

class FlightSearchRequest(BaseModel):
    flight_number: str

class FlightInfoResponse(BaseModel):
    flight_number: str
    origin: str
    destination: str
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None

class FlightSearchErrorResponse(BaseModel):
    error: str

# Initialize FastMCP server
app = FastMCP()

# Break the long line into multiple lines
@app.tool("/search_flight")
async def search_flight(
    request: FlightSearchRequest
) -> FlightInfoResponse | FlightSearchErrorResponse:
    # Correct the API key retrieval and usage
    api_key = os.getenv("FLIGHTAWARE_API_KEY")
    # api_key = userdata.get('FLIGHTAWARE_API_KEY')
    if not api_key:
        logger.error("API key is missing")
        return FlightSearchErrorResponse(error="API key is missing")

    headers = {
        "x-apikey": api_key
    }

    # Correct the flight number retrieval
    flight_number = request.flight_number
    url = f"{FLIGHTAWARE_BASE_URL}{flight_number}"

    logger.info(f"Making request to {url} with headers {headers}")

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response text: {response.text}")

        if response.status_code != 200:
            logger.error(f"FlightAware API error: {response.status_code} - {response.text}")
            return FlightSearchErrorResponse(error=f"FlightAware API error: {response.status_code} - {response.text}")

        data = response.json()

        # Log the entire response data for debugging
        logger.info(f"Response JSON: {data}")

        # Check if 'flights' key exists and is not empty in the response
        if 'flights' not in data or not data['flights']:
            logger.error("No flight information found in the response")
            return FlightSearchErrorResponse(error="No flight information found")

        # Extract relevant information from the API response
        flight_info = data['flights'][0]
        flight_number = flight_info.get("ident")
        origin = flight_info.get("origin", {}).get("code")
        destination = flight_info.get("destination", {}).get("code")
        departure_time = flight_info.get("actual_departure_time", {}).get("date")
        arrival_time = flight_info.get("actual_arrival_time", {}).get("date")

        # Correct the return type for successful response
        return FlightInfoResponse(
            flight_number=flight_number,
            origin=origin,
            destination=destination,
            departure_time=departure_time,
            arrival_time=arrival_time
        )

async def gradio_search_flight(flight_number: str) -> str:
    """
    Searches for flight information using the FastMCP tool and formats the output
    for Gradio.

    Args:
        flight_number: The flight number to search for.

    Returns:
        A formatted string containing flight information or an error message.
    """
    if not flight_number:
        return "Please enter a flight number."

    payload = {"flight_number": flight_number}
    url = "http://127.0.0.1:8000/search_flight"  # Assuming FastMCP runs on default port

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()

        if "error" in data:
            return f"Error: {data['error']}"
        else:
            flight_info = data
            output_string = (
                f"Flight Number: {flight_info.get('flight_number', 'N/A')}\n"
                f"Origin: {flight_info.get('origin', 'N/A')}\n"
                f"Destination: {flight_info.get('destination', 'N/A')}\n"
                f"Departure Time: {flight_info.get('departure_time', 'N/A')}\n"
                f"Arrival Time: {flight_info.get('arrival_time', 'N/A')}"
            )
            return output_string

    except httpx.RequestError as e:
        return f"An error occurred while requesting flight information: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# Define the Gradio interface
iface = gr.Interface(
    fn=gradio_search_flight,
    inputs="text",  # Text box for flight number input
    outputs="text",  # Text box for displaying results
    title="Flight Information Search" # Add a title
)

# Launch the Gradio interface
iface.launch(share=True) # Set share=True for public URL in environments like Colab