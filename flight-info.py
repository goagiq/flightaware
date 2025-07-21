import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import httpx
import asyncio
import logging
from typing import Optional

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

# Ensure the run method returns a coroutine
if __name__ == "__main__":
    asyncio.run(app.run())  # Ensure app.run() is a coroutine