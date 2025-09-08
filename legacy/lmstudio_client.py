"""LM Studio client for connecting to local server and listing models."""
import json
from typing import Dict, Any, Optional

import requests


def connect_to_lmstudio(base_url: str = "http://localhost:1234") -> Optional[Dict[str, Any]]:
    """
    Connect to LM Studio server and get available models

    Args:
        base_url: Base URL of the LM Studio server

    Returns:
        Dictionary with models information or None if connection fails
    """
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=10)
        response.raise_for_status()

        data = response.json()
        print("Connection successful!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")

        return data

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to LM Studio server")
        print("Make sure LM Studio is running on http://localhost:1234")
        return None

    except requests.exceptions.Timeout:
        print("Error: Connection timeout")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None


def list_models(data: Dict[str, Any]) -> None:
    """
    Print available models in a formatted way

    Args:
        data: Models data from the API response
    """
    if not data or 'data' not in data:
        print("No models data available")
        return

    models = data['data']
    print(f"\nAvailable models ({len(models)}):")
    print("-" * 50)

    for i, model in enumerate(models, 1):
        print(f"{i}. ID: {model.get('id', 'N/A')}")
        print(f"   Object: {model.get('object', 'N/A')}")
        if 'owned_by' in model:
            print(f"   Owned by: {model['owned_by']}")
        print()


if __name__ == "__main__":
    print("Connecting to LM Studio server...")
    print("=" * 50)

    response_data = connect_to_lmstudio()

    if response_data:
        list_models(response_data)
    else:
        print("\nTroubleshooting tips:")
        print("1. Start LM Studio application")
        print("2. Load a model in LM Studio")
        print("3. Make sure the server is running on port 1234")
        print("4. Check if any firewall is blocking the connection")