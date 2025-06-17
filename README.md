# Flight Search MCP Server

A reliable Model Context Protocol (MCP) server for searching flights using the SerpAPI Google Flights engine. This server provides real-time flight search capabilities for both one-way and round-trip flights.
Works well with claude ai desktop

## ✈️ Features

- **Real-time flight search** using SerpAPI Google Flights
- **One-way and round-trip** flight support
- **Multiple flight options** with pricing, timing, and airline details
- **JSON-RPC 2.0 compliant** MCP protocol implementation
- **Easy integration** with Claude and other MCP clients
- **Robust error handling** and logging

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- SerpAPI account and API key ([Get one here](https://serpapi.com/))
- MCP-compatible client (Claude, etc.)

### Installation

1. **Clone or download** the server file:
```bash
mkdir -p ~/tools/flightsearch
# Copy flight_search_server.py to ~/tools/flightsearch/
```

2. **Install dependencies**:
```bash
pip install requests
```

3. **Get your SerpAPI key**:
   - Sign up at [SerpAPI](https://serpapi.com/)
   - Get your API key from the dashboard

### Configuration

Add the following to your MCP client configuration:

```json
{
  "flightsearch": {
    "command": "python3",
    "args": [
      "/path/to/your/tools/flightsearch/flight_search_server.py",
      "--connection_type", 
      "stdio"
    ],
    "env": {
      "SERP_API_KEY": "your_serpapi_key_here"
    }
  }
}
```

**For Claude Desktop**, add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "flightsearch": {
      "command": "python3",
      "args": [
        "/Users/yourusername/tools/flightsearch/flight_search_server.py",
        "--connection_type", 
        "stdio"
      ],
      "env": {
        "SERP_API_KEY": "your_serpapi_key_here"
      }
    }
  }
}
```

## 📖 Usage

### Available Tools

#### `search_flights`
Search for flights between airports.

**Parameters:**
- `origin` (required): Origin airport code (e.g., "JFK", "LAX")
- `destination` (required): Destination airport code (e.g., "JFK", "LAX") 
- `outbound_date` (required): Departure date in YYYY-MM-DD format
- `return_date` (optional): Return date for round-trip flights in YYYY-MM-DD format

**Examples:**

```python
# One-way flight
search_flights(origin="JFK", destination="LAX", outbound_date="2025-07-01")

# Round-trip flight  
search_flights(origin="JFK", destination="LAX", outbound_date="2025-07-01", return_date="2025-07-08")
```

#### `server_status`
Check if the flight search server is running.

**Parameters:** None

### Sample Response

```json
{
  "status": "success",
  "origin": "JFK",
  "destination": "LAX", 
  "outbound_date": "2025-07-01",
  "return_date": null,
  "trip_type": "one_way",
  "flights": [
    {
      "price": 199,
      "departure_time": "2025-07-01 08:40",
      "arrival_time": "2025-07-01 11:45", 
      "airline": "Delta",
      "duration": 365,
      "stops": 0
    },
    {
      "price": 204,
      "departure_time": "2025-07-01 09:00",
      "arrival_time": "2025-07-01 12:00",
      "airline": "JetBlue", 
      "duration": 360,
      "stops": 0
    }
  ]
}
```

## 🔧 Development

### Running Tests

Test the server directly:

```bash
# Set environment variable
export SERP_API_KEY="your_api_key"

# Run the server  
python3 flight_search_server.py --connection_type stdio
```

### Protocol Testing

The server implements JSON-RPC 2.0 and supports these methods:

- `initialize` - Initialize the MCP connection
- `tools/list` - List available tools
- `tools/call` - Execute a tool
- `ping` - Health check
- `notifications/initialized` - Initialization notification

### Logging

The server logs to stderr for debugging:

```bash
# View logs while running
python3 flight_search_server.py --connection_type stdio 2>debug.log
```

## 🐛 Troubleshooting

### Common Issues

**1. "API request failed: 400 Client Error"**
- Verify your SerpAPI key is valid
- Check that airport codes are correct (use IATA codes like "JFK", "LAX")
- Ensure date format is YYYY-MM-DD

**2. "SERP_API_KEY environment variable not set"**
- Make sure the API key is properly set in your MCP configuration
- Verify the environment variable name is exactly `SERP_API_KEY`

**3. "JSON-RPC schema validation errors"**
- Restart your MCP client to reload the server
- Check that you're using the latest version of the server

**4. No flights found**
- Try different airport codes or dates
- Some routes may not be available for the selected date
- Check SerpAPI documentation for supported airports

### Debug Mode

Enable debug logging:

```python
# Add to the top of flight_search_server.py
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
```

## 📝 API Limitations

- **SerpAPI Rate Limits**: Check your SerpAPI plan for request limits
- **Flight Data**: Results depend on Google Flights data availability
- **Date Range**: Future dates only (cannot search past flights)
- **Airport Codes**: Must use valid IATA airport codes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/flight-search-mcp.git
cd flight-search-mcp

# Install dependencies
pip install requests

# Run tests
python3 test_mcp_protocol.py
python3 test_flight_search.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [SerpAPI](https://serpapi.com/) for providing the Google Flights API
- [Anthropic](https://anthropic.com/) for the MCP protocol specification
- The open-source community for inspiration and feedback

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Questions**: Check the [SerpAPI documentation](https://serpapi.com/google-flights-api)
- **MCP Protocol**: See [Anthropic's MCP documentation](https://modelcontextprotocol.io/)

---

**Made with ❤️ for the MCP community**
