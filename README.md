# linkedin-profile

Scrapes LinkedIn profiles via the [Apify](https://apify.com) `dev_fusion/Linkedin-Profile-Scraper` actor and returns structured JSON data including work history, education, skills, and contact information.

## Setup

1. Create a free Apify account at https://apify.com
2. Copy your API token from https://console.apify.com/settings/integrations
3. Set `apify_api_key` in the plugin config

## Tool: `scrape_linkedin_profile`

Accepts a list of LinkedIn profile URLs, launches the Apify actor asynchronously, polls until the run completes, and returns the full dataset as JSON.

**Parameters:**

| Name           | Type  | Description                                 |
|----------------|-------|---------------------------------------------|
| `profile_urls` | array | LinkedIn profile URLs to scrape             |

**Example input:**
```json
{
  "profile_urls": ["https://www.linkedin.com/in/namelastname/"]
}
```

**Example output:** Array of profile objects with fields like `fullName`, `headline`, `location`, `positions`, `educations`, `skills`, `certifications`, etc.

## Notes

- The tool is marked `async` — the agent will receive results as a callback once the Apify run finishes (typically 30–120 seconds per profile).
- The actor requires a valid LinkedIn session cookie configured in your Apify account or actor input; check the actor's documentation on Apify for authentication requirements.
- Polling stops after ~4.5 minutes to stay within the async tool timeout.
