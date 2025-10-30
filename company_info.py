from google import genai
from google.genai import types
from typing import Any, Dict

import asyncio
import json
import re


class Prompt:
    def construct_prompt(self, company_name: str) -> str:
        return f"""
** Instructions **:
You are an expert data researcher and business analyst. You can browse the web, call external tools/APIs, and gather publicly available information. Your task is to gather, summarize, and structure all available and reliable information about {company_name} in a consistent, analyzable format.

** Objectiven **:
Gather and structure all publicly available information about {company_name} into clearly defined, machine-readable sections suitable for analysis or chunking.

Use only publicly available data (from the web, financial filings, news articles, reports, etc.).
If any information is unavailable, mark the field as "N/A".

Output Format (JSON preferred, or Markdown if JSON isn't possible):
{{
  "basic_information": {{
    "company_name": "",
    "legal_name": "",
    "headquarters": "",
    "founded_date": "",
    "founders": [],
    "company_type": "",
    "ticker_symbol": "",
    "website": "",
    "industry": "",
    "business_model_summary": ""
  }},
  "executive_team": [
    {{
      "name": "",
      "role": "",
      "tenure_start": "",
      "biography_summary": ""
    }}
  ],
  "financial_overview": {{
    "revenue": "",
    "net_income": "",
    "valuation": "",
    "funding_rounds": [
      {{
        "date": "",
        "round": "",
        "amount": "",
        "lead_investors": []
      }}
    ],
    "major_investors": []
  }},
  "products_and_services": [
    {{
      "name": "",
      "category": "",
      "launch_date": "",
      "key_features": "",
      "market_position": ""
    }}
  ],
  "market_presence": {{
    "regions_operated": [],
    "major_clients_or_partners": [],
    "competitors": [],
    "market_share_estimate": ""
  }},
  "news_and_events": [
    {{
      "date": "",
      "headline": "",
      "source": "",
      "summary": ""
    }}
  ],
  "corporate_governance_and_ethics": {{
    "esg_initiatives": "",
    "legal_issues_or_controversies": "",
    "csr_programs": ""
  }},
  "technology_and_innovation": {{
    "patents": [],
    "technologies_used": [],
    "notable_research_or_innovation": ""
  }},
  "public_sentiment_summary": {{
    "social_media_sentiment": "",
    "media_sentiment": "",
    "customer_reviews_summary": ""
  }},
  "data_sources": [
    {{
      "source_name": "",
      "url": "",
      "date_accessed": ""
    }}
  ]
}}

** Additional guidelines **:
- Provide concise summaries (1-3 sentences per field) where applicable.
- Ensure data integrity and accuracy by citing credible sources.
- If the company is private or data is limited, emphasize what's missing and where estimates are derived.
- Avoid redundancy.
- Use UTC date formats (YYYY-MM-DD).
""".strip()


class GeminiChat:
    __model_name: str = "gemini-2.5-pro"

    def __init__(self, api_key: str, prompt: str):
        self.prompt = prompt
        self.api_key = api_key

        if not self.api_key:
            raise EnvironmentError("GEMINI_KEY environment variable not set")

    async def send_request(self):
        client = genai.Client(
            api_key=self.api_key
        ).aio
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
        response = await client.models.generate_content(
            model=self.__model_name,
            contents=self.prompt,
            config=config,
        )
        return response.text

    def extract_json_from_markdown(self, completion: str) -> Dict[str, Any]:
        try:
            raw_content = completion.strip()

            description = ""
            json_part = raw_content

            fence_index = raw_content.find("```")

            if fence_index != -1:
                description = raw_content[:fence_index].strip()
                json_part = raw_content[fence_index:]

            fence_match = re.search(r"```(?:json)?\s*({.*})\s*```", json_part, re.DOTALL)

            json_candidate = None
            if fence_match:
                json_candidate = fence_match.group(1).strip()
            else:
                start = json_part.find("{")
                end = json_part.rfind("}")

                if start != -1 and end != -1 and start < end:
                    json_candidate = json_part[start:end+1].strip()
                else:
                    blob_match = re.search(r"({.*})", json_part, re.DOTALL)
                    if blob_match:
                        json_candidate = blob_match.group(1).strip()

            if not json_candidate:
                raise ValueError("No valid JSON object found in the content.")

            parsed_json = json.loads(json_candidate)

            if description:
                parsed_json["description"] = description

            return parsed_json
        except json.JSONDecodeError as json_err:
            raise ValueError(f"Failed to decode JSON. Error: {json_err}. Candidate: '{json_candidate}'")
        except Exception as e:
            error_msg = f"Error extracting valid JSON from content. Error: {e}. "
            error_msg += f"Content snippet: '{completion[:100]}...'"
            raise ValueError(error_msg)


async def main():
    api_key = 'AIzaSyAHYQ3FNi3u_qfZvvg-xMQ9Saa44w5R7sM'
    prompt = Prompt().construct_prompt("Honda Xcelerator Ventures")

    chat = GeminiChat(
        api_key=api_key,
        prompt=prompt
    )

    resp = await chat.send_request()
    new_resp = chat.extract_json_from_markdown(resp)

    with open("data/honda.json", "w") as honda_file:
        json.dump(new_resp, honda_file, indent=4, ensure_ascii=False)

    return new_resp


if __name__ == "__main__":
    asyncio.run(main())
