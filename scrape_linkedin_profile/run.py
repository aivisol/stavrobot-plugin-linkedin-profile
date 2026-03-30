#!/usr/bin/env -S uv run
# /// script
# dependencies = ["httpx"]
# ///

import json
import sys
import time

import httpx

ACTOR_ID = "dev_fusion~Linkedin-Profile-Scraper"
POLL_INTERVAL = 5  # seconds between status checks
MAX_WAIT = 280     # seconds — stay under the 5-minute async timeout


def main():
    input_data = json.loads(sys.stdin.read())
    raw = input_data.get("profile_urls", "")

    # Accept either a JSON array string or a single URL string
    if isinstance(raw, list):
        profile_urls = raw
    else:
        raw = raw.strip()
        try:
            profile_urls = json.loads(raw)
            if not isinstance(profile_urls, list):
                profile_urls = [raw]
        except (json.JSONDecodeError, ValueError):
            profile_urls = [raw] if raw else []

    if not profile_urls:
        print(json.dumps({"error": "profile_urls is required and must not be empty"}))
        sys.exit(1)

    with open("../config.json") as f:
        config = json.load(f)

    api_key = config.get("apify_api_key", "").strip()
    if not api_key:
        print(json.dumps({"error": "apify_api_key is not configured"}))
        sys.exit(1)

    # Launch the Apify actor run
    launch_resp = httpx.post(
        f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs",
        params={"token": api_key},
        json={"profileUrls": profile_urls},
        timeout=30,
    )
    launch_resp.raise_for_status()
    run_data = launch_resp.json()["data"]
    run_id = run_data["id"]
    dataset_id = run_data["defaultDatasetId"]

    # Poll until the run reaches a terminal state
    elapsed = 0
    while elapsed < MAX_WAIT:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        status_resp = httpx.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}",
            params={"token": api_key},
            timeout=30,
        )
        status_resp.raise_for_status()
        status = status_resp.json()["data"]["status"]

        if status == "SUCCEEDED":
            break
        elif status in ("FAILED", "ABORTED", "TIMED-OUT"):
            print(
                json.dumps({"error": f"Apify actor run {status.lower()}", "run_id": run_id}),
                file=sys.stderr,
            )
            sys.exit(1)
        # RUNNING / READY — keep polling

    else:
        print(
            json.dumps({"error": "Timed out waiting for Apify actor run to complete", "run_id": run_id}),
            file=sys.stderr,
        )
        sys.exit(1)

    # Fetch results from the default dataset
    dataset_resp = httpx.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        params={"token": api_key, "format": "json"},
        timeout=30,
    )
    dataset_resp.raise_for_status()
    results = dataset_resp.json()

    print(json.dumps(results))


if __name__ == "__main__":
    main()
