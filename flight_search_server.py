#!/usr/bin/env python3
"""
Simple Flight Search MCP Server
By Random Robbie
"""

import json
import sys
import asyncio
import requests
from typing import Dict, Any, List, Optional
import argparse
from datetime import datetime
import logging

# Set up logging to stderr so it doesn't interfere with JSON-RPC
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger(__name__)


class FlightSearchServer:
    def __init__(self, serp_api_key: str):
        self.serp_api_key = serp_api_key
        
    def search_flights(self, origin: str, destination: str, outbound_date: str, return_date: str = None) -> Dict[str, Any]:
        """Search for flights using SerpAPI Google Flights"""
        
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": outbound_date,
            "currency": "USD",
            "api_key": self.serp_api_key
        }
        
        # Fix: Handle one-way vs round trip properly
        if return_date:
            params["return_date"] = return_date
            params["type"] = "1"  # Round trip
        else:
            params["type"] = "2"  # One way
            
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "error" in data:
                return {
                    "status": "error",
                    "message": f"SerpAPI error: {data['error']}"
                }
            
            # Extract flight information
            flights = []
            best_flights = data.get("best_flights", [])
            
            for flight in best_flights[:5]:  # Top 5 flights
                flight_info = {
                    "price": flight.get("price", "N/A"),
                    "departure_time": flight.get("flights", [{}])[0].get("departure_airport", {}).get("time"),
                    "arrival_time": flight.get("flights", [{}])[0].get("arrival_airport", {}).get("time"),
                    "airline": flight.get("flights", [{}])[0].get("airline"),
                    "duration": flight.get("total_duration"),
                    "stops": len(flight.get("flights", [])) - 1
                }
                flights.append(flight_info)
                
            return {
                "status": "success",
                "origin": origin,
                "destination": destination,
                "outbound_date": outbound_date,
                "return_date": return_date,
                "trip_type": "round_trip" if return_date else "one_way",
                "flights": flights
            }
            
        except requests.RequestException as e:
            return {
                "status": "error",
                "message": f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error processing flight data: {str(e)}"
            }

    async def handle_call_tool(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls"""
        request_id = request.get("id")
        if request_id is None:
            request_id = "unknown"
            
        try:
            tool_name = request["params"]["name"]
            arguments = request["params"].get("arguments", {})
            
            if tool_name == "search_flights":
                result = self.search_flights(
                    origin=arguments.get("origin", ""),
                    destination=arguments.get("destination", ""),
                    outbound_date=arguments.get("outbound_date", ""),
                    return_date=arguments.get("return_date")
                )
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            elif tool_name == "server_status":
                return {
                    "jsonrpc": "2.0", 
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "Flight search server is running"
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id, 
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in handle_call_tool: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    async def handle_list_tools(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """List available tools"""
        request_id = request.get("id")
        if request_id is None:
            request_id = "unknown"
            
        tools = [
            {
                "name": "search_flights",
                "description": "Search for flights between airports",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "Origin airport code (e.g., JFK, LAX)"
                        },
                        "destination": {
                            "type": "string", 
                            "description": "Destination airport code (e.g., JFK, LAX)"
                        },
                        "outbound_date": {
                            "type": "string",
                            "description": "Departure date (YYYY-MM-DD)"
                        },
                        "return_date": {
                            "type": "string",
                            "description": "Return date for round trip (YYYY-MM-DD)"
                        }
                    },
                    "required": ["origin", "destination", "outbound_date"]
                }
            },
            {
                "name": "server_status",
                "description": "Check if the flight search server is running",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }

    async def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization"""
        request_id = request.get("id")
        if request_id is None:
            request_id = "unknown"
            
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "flight-search-server",
                    "version": "1.0.2"
                }
            }
        }

    async def handle_ping(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping requests"""
        request_id = request.get("id")
        if request_id is None:
            request_id = "unknown"
            
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {}
        }

    def send_response(self, response: Dict[str, Any]):
        """Send a JSON-RPC response"""
        try:
            response_json = json.dumps(response)
            print(response_json, flush=True)
            logger.debug(f"Sent response: {response_json}")
        except Exception as e:
            logger.error(f"Error sending response: {e}")

    async def run_stdio(self):
        """Run server using stdio transport"""
        logger.info("Starting flight search MCP server...")
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    logger.info("EOF received, shutting down")
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                logger.debug(f"Received: {line}")
                request = json.loads(line)
                
                # Handle different request types
                method = request.get("method")
                request_id = request.get("id", "unknown")
                
                logger.debug(f"Processing method: {method}, id: {request_id}")
                
                if method == "initialize":
                    response = await self.handle_initialize(request)
                elif method == "tools/list":
                    response = await self.handle_list_tools(request)
                elif method == "tools/call":
                    response = await self.handle_call_tool(request)
                elif method == "ping":
                    response = await self.handle_ping(request)
                elif method == "notifications/initialized":
                    # This is a notification, no response needed
                    logger.debug("Received initialized notification")
                    continue
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                
                self.send_response(response)
                
            except EOFError:
                logger.info("EOF received, shutting down")
                break
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                self.send_response(error_response)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                self.send_response(error_response)


def main():
    parser = argparse.ArgumentParser(description="Flight Search MCP Server")
    parser.add_argument("--connection_type", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--port", type=int, default=3001)
    args = parser.parse_args()
    
    # Get API key from environment
    import os
    serp_api_key = os.getenv("SERP_API_KEY")
    if not serp_api_key:
        logger.error("SERP_API_KEY environment variable not set")
        sys.exit(1)
    
    server = FlightSearchServer(serp_api_key)
    
    if args.connection_type == "stdio":
        try:
            asyncio.run(server.run_stdio())
        except KeyboardInterrupt:
            logger.info("Server interrupted")
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)
    else:
        logger.error("HTTP server not implemented yet. Use stdio mode.")
        sys.exit(1)


if __name__ == "__main__":
    main()
