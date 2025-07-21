# FlightAware MCP Server

A Model Context Protocol (MCP) server that provides real-time flight information using the FlightAware AeroAPI. This server integrates with FastMCP and includes a Gradio web interface for easy testing and interaction.

## Features

- Real-time flight information retrieval using FlightAware AeroAPI
- MCP tool integration for use with AI assistants
- Gradio web interface for interactive flight search
- Environment variable configuration for API keys
- Comprehensive logging for debugging and monitoring
- Support for flight number searches with detailed information

## Prerequisites

- Python 3.13 or higher
- A FlightAware AeroAPI key (free tier available)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/goagiq/flightaware.git
   cd flightaware
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

## Configuration

1. Create a `.env` file in the project root:
   ```env
   FLIGHTAWARE_API_KEY=your_flightaware_api_key_here
   ```

2. Get your free API key from [FlightAware AeroAPI](https://flightaware.com/aeroapi/):
   - Sign up for a FlightAware account
   - Navigate to the AeroAPI section
   - Generate your API key
   - Copy your API key to the `.env` file

## Usage

### Running the MCP Server (flight-info.py)

To run the basic flight information server:

```bash
python flight-info.py
```

This starts the FastMCP server that exposes flight search functionality.

### Running the Full Application with Gradio Interface (flight-search.py)

To run the server with a web interface:

```bash
python flight-search.py
```

This will launch both the MCP server and a Gradio web interface accessible at `http://localhost:7860`.

### Using the Gradio Interface

1. Enter a flight number (e.g., "UAL123", "DAL456")
2. Click submit to get detailed flight information
3. View results including:
   - Flight number
   - Origin airport
   - Destination airport
   - Departure time
   - Arrival time

### Using as an MCP Tool

The server exposes a `search_flight` tool that can be used by MCP-compatible clients:

**Endpoint:** `/search_flight`

**Request Model:**
```python
class FlightSearchRequest(BaseModel):
    flight_number: str
```

**Response Model (Success):**
```python
class FlightInfoResponse(BaseModel):
    flight_number: str
    origin: str
    destination: str
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
```

**Response Model (Error):**
```python
class FlightSearchErrorResponse(BaseModel):
    error: str
```

### Example Usage

```python
# Using the tool directly
import httpx
import asyncio

async def search_flight_example():
    payload = {"flight_number": "UAL123"}
    url = "http://127.0.0.1:8000/search_flight"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        data = response.json()
        print(data)

# Run the example
asyncio.run(search_flight_example())
```

## API Response Examples

**Successful Flight Search:**
```json
{
  "flight_number": "UAL123",
  "origin": "SFO",
  "destination": "LAX",
  "departure_time": "2025-07-21T08:30:00Z",
  "arrival_time": "2025-07-21T10:45:00Z"
}
```

**Error Response:**
```json
{
  "error": "No flight information found"
}
```

## Supported Flight Number Formats

The API supports various flight number formats:
- Standard airline codes: "UAL123", "DAL456"
- International flights: "LH401", "BA123"
- Regional carriers: "WN1234", "NK567"

For best results, use the full flight number including the airline code.

## Error Handling

The server includes comprehensive error handling for:
- Missing API keys
- Invalid flight numbers
- Network connectivity issues
- API rate limits and quotas
- Malformed API responses

All errors are logged to both console and `app.log` file for debugging.

## Development

### Project Structure

- `flight-info.py` - Basic MCP server implementation
- `flight-search.py` - Full server with Gradio interface
- `pyproject.toml` - Project configuration and dependencies
- `app.log` - Application logs (generated at runtime)
- `.env` - Environment variables (create this file)
- `.gitignore` - Git ignore rules

### Dependencies

Key dependencies include:
- `fastmcp` - FastMCP server framework
- `httpx` - Async HTTP client for API calls
- `gradio` - Web interface for testing
- `pydantic` - Data validation and settings management
- `python-dotenv` - Environment variable management
- `mcp` - Model Context Protocol library

### Logging

The application uses comprehensive logging with:
- File logging to `app.log`
- Console output for real-time monitoring
- Different log levels (INFO, ERROR, DEBUG)
- Detailed API request/response logging

### API Integration

The server integrates with FlightAware's AeroAPI:
- Base URL: `https://aeroapi.flightaware.com/aeroapi/flights/`
- Authentication: API key via `x-apikey` header
- Response format: JSON with flight details

## Troubleshooting

### Common Issues

1. **"API key is missing" error**
   - Verify your API key is correct in the `.env` file
   - Ensure you've signed up for FlightAware AeroAPI

2. **"No flight information found" error**
   - Check that the flight number is valid and current
   - Verify the flight is in FlightAware's database
   - Try different flight number formats

3. **Network connection errors**
   - Check your internet connection
   - Verify FlightAware API is accessible
   - Check for firewall restrictions

4. **Gradio interface not accessible**
   - Ensure the server is running on the correct port
   - Check for port conflicts
   - Try accessing via `http://localhost:7860`

### Debug Mode

To enable detailed debugging:
1. Modify the logging level in the Python files:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```
2. Check the `app.log` file for detailed request/response logs

### API Rate Limits

FlightAware AeroAPI has the following limits:
- Free tier: Limited requests per month
- Rate limiting: Requests per minute restrictions
- Commercial plans available for higher usage

Monitor your usage through the FlightAware dashboard.

## Environment Setup

### For Google Colab

The code includes commented lines for Google Colab integration:
```python
# from google.colab import userdata
# api_key = userdata.get('FLIGHTAWARE_API_KEY')
```

Uncomment these lines and comment out the `os.getenv()` line when running in Colab.

### For Local Development

Use the `.env` file approach as described in the Configuration section.

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues and enhancement requests!

## Support

For FlightAware AeroAPI support, visit [FlightAware's documentation](https://flightaware.com/aeroapi/portal/documentation).

For project-specific issues, please create an issue in this repository.