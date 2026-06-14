#!/usr/bin/env python3
"""Helper script to create a Cloud Task targeting the internal Cloud Run service."""

import argparse
import json
import sys
from google.cloud import tasks_v2


def create_http_task(project: str, queue: str, location: str, url: str, service_account_email: str, prompt: str):
    """Create a task for a Cloud Run endpoint with OIDC authentication."""
    client = tasks_v2.CloudTasksClient()

    # Build the resource name of the parent queue
    parent = client.queue_path(project, location, queue)

    # Construct the request body
    task_payload = {"prompt": prompt}

    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(task_payload).encode("utf-8"),
            "oidc_token": {
                "service_account_email": service_account_email,
                # The audience defaults to the target URL if not specified
            },
        }
    }

    try:
        response = client.create_task(request={"parent": parent, "task": task})
        print(f"Successfully created task: {response.name}")
    except Exception as e:
        print(f"Error creating task: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Enqueues a task to run on Cloud Run.")
    parser.add_argument("--project", default="deankita-test-1", help="Google Cloud project ID")
    parser.add_argument("--queue", default="gemini-tasks", help="Cloud Tasks queue name")
    parser.add_argument("--location", default="us-central1", help="Cloud Tasks queue location")
    parser.add_argument(
        "--url",
        default="https://vertex-ai-gemini-server-299930857189.us-central1.run.app/generate",
        help="Cloud Run target endpoint URL"
    )
    parser.add_argument(
        "--service-account",
        required=True,
        help="Service Account email to use for OIDC authentication (needs run.invoker role)"
    )
    parser.add_argument(
        "--prompt",
        default="Explain quantum computing in one simple sentence.",
        help="Prompt payload to send to Cloud Run"
    )

    args = parser.parse_args()

    create_http_task(
        project=args.project,
        queue=args.queue,
        location=args.location,
        url=args.url,
        service_account_email=args.service_account,
        prompt=args.prompt
    )


if __name__ == "__main__":
    main()
