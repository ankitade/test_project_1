#!/usr/bin/env python3
"""A client helper to send authenticated requests to the internal Cloud Run service."""

import argparse
import sys
import google.auth
import google.auth.transport.requests
import google.oauth2.id_token
import requests


def get_id_token(audience: str) -> str:
    """Fetch an OIDC ID token for the target audience (Cloud Run URL)."""
    try:
        auth_req = google.auth.transport.requests.Request()
        # Fetching the ID token using application default credentials (ADC)
        return google.oauth2.id_token.fetch_id_token(auth_req, audience=audience)
    except Exception as e:
        print(f"Error fetching ID token: {e}", file=sys.stderr)
        print("Make sure you have run 'gcloud auth application-default login'.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Call the Vertex AI Gemini Server.")
    parser.add_argument(
        "--url",
        # default="https://vertex-ai-gemini-server-299930857189.us-central1.run.app",
        default="https://vertex-ai-gemini-server-k7ap2ftbxa-uc.a.run.app",
        help="The URL of the deployed Cloud Run service (defaults to https://vertex-ai-gemini-server-k7ap2ftbxa-uc.a.run.app)"
    )
    parser.add_argument(
        "--prompt",
        help="The prompt to send to the generator. If not provided, performs a health check."
    )

    args = parser.parse_args()
    service_url = args.url.rstrip("/")

    # Fetch OIDC ID token to authenticate with Cloud Run
    print("Fetching ID token...")
    token = get_id_token(service_url)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if args.prompt:
        # Call /generate endpoint
        generate_url = f"{service_url}/generate"
        print(f"Sending prompt to {generate_url}...")
        try:
            response = requests.post(
                generate_url,
                headers=headers,
                json={"prompt": args.prompt}
            )
            response.raise_for_status()
            print("\nResponse:")
            print(response.json().get("response", "No response content found."))
        except Exception as e:
            print(f"Request failed: {e}", file=sys.stderr)
            if 'response' in locals() and response.text:
                print(f"Server response: {response.text}", file=sys.stderr)
    else:
        # Call root endpoint (health check)
        print(f"Performing health check on {service_url}...")
        try:
            response = requests.get(service_url, headers=headers)
            response.raise_for_status()
            print("\nStatus:")
            print(response.json())
        except Exception as e:
            print(f"Request failed: {e}", file=sys.stderr)
            if 'response' in locals() and response.text:
                print(f"Server response:\n{response.text}", file=sys.stderr)


if __name__ == "__main__":
    main()
