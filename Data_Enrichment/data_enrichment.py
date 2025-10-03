from aiolimiter import AsyncLimiter
from fake_useragent import UserAgent
from Models.models import InputModel, GoogleResponseModel
from pathlib import Path
from typing import Dict, Optional, Any
import aiohttp
import asyncio
import csv
import json
import os
import re


class Prompt:
    def __init__(self, company_name: str = None, company_website: str = None):
        self.company_name = company_name
        self.company_website = company_website
    
    def construct_prompt(self) -> str:
        return f"""
You are a technical investment screener evaluating early and growth-stage startups or technologies aligned with the following criteria:
 * Mobility: novel ways of helping people move around (including personal, shared, micro, urban, rural, off-grid, autonomous, or low-infrastructure transport)
 * Sustainability: alternative energy sources for mobility (e.g. electric, solar, hydrogen), efficient energy storage, battery tech, sustainable materials, circular economy approaches in mobility (re-use, recycling, low-energy manufacturing)
 * Solutions that are *highly ambitious*, potentially transformational, and technologically hard to build (moonshots preferred over incremental improvements).

 **Excluded areas:** Do NOT include anything primarily related to cyber security, core IT infrastructure, big power plants, power grid, fintech, healthcare/medtech, logistics SaaS, or biotech.

Given the following information:
Company Name: {self.company_name}
Company Website: {self.company_website}

**CRITICAL**
Only evaluate companies that directly advance human mobility, vehicle/drone/robot navigation, propulsion, battery systems, charging infrastructure, positioning, hydrogen production for mobility, or other technologies that materially improve how people/goods move.
If company is outside scope, set in_scope=false and explain WHY in ≤25 words.

**SCORING RUBRIC (0-10 integers)**
 * Uniqueness (50%) = How novel & hard-to-reproduce the core tech is.
   ** 0 = commodity / generic IT / no IP.
   ** ≤3 if notes mention “too many players,” “no unique tech,” “business model only,” or “crowded space.”
   ** ≤4 if notes say “used to be unique but now crowded,” “unclear advantage,” “not sure.”
   ** ≥8 if notes say “no one else,” “first-of-kind,” “very daring,” “never been done,” or “fundamentally new principle (physics/chemistry).”
 * Effectiveness (30%) = Evidence the tech works.
   ** 0 = none.
   ** ≤4 if only R&D or vague pilots.
   ** ≥7 if multiple independent validations, OEM partnerships, or large-scale deployments.
 * Market Differentiation / Saturation (20%)
   ** ≤2 if feedback says “too many players” or “highly crowded.”
   ** ≥7 if market niche is rare with clear moat or IP.

**Guardrails**
 * WOW Line
   ** If uniqueness_score ≤ 4, set wow_one_liner = "None". Do not generate hype.
   ** If uniqueness_score ≥ 8, wow line must highlight “breakthrough / first-of-kind / never done.”
 * Crowded Domains Cap
   ** Autonomous driving full-stack → uniqueness ≤ 3.
   ** EV charging platforms (including fleet optimization) → uniqueness ≤ 3.
   ** Warehouse robotics, Driver Monitoring Systems (DMS), water-from-air → uniqueness ≤ 3.
 * Negative Overrides
   ** If notes mention “unclear advantage,” “not sure,” “many startups” → uniqueness ≤ 4.
   ** If notes mention “similar players,” “too many,” “all doing the same,” “crowded” → uniqueness ≤ 3.
 * Confidence Scaling
   ** If feedback is vague/uncertain → confidence="Low" and default scores ≤ 4.
   ** Otherwise use Medium or High.
 * Output Discipline
   ** Use integers only for scores.
   ** Keep every text field ≤30 words.
   ** Do not output any fields beyond schema.

**COMPUTATION**
 * combined_score = round( uniqueness_score*0.5 + effectiveness_score*0.3 + market_diff_score*0.2 )

**OUTPUT_SCHEMA**
### Provide a full enrichment with the following structure:
1. company_name
2. in_scope
3. uniqueness_score
4. uniqueness_why
5. effectiveness_score
6. effectiveness_why
7. market_diff_score
8. combined_score
9. confidence
10. brief_description
11. wow_one_liner
12. founders: Who they are, backgrounds, any relevant credentials
13. technologies: Core technical components, IP, or breakthrough approaches used
14. applications: Where and how it's being applied
15. products: What they've built so far, product status
16. customer_engagements: Any known pilots, trials, customers, or adoption
17. hq_location: Country, state/province, city
18. current_funding_information: Last known round, amount, date, valuation (if available)
19. core_technology_used: List 2-5 phrases (e.g. "solid-state batteries", "electric propulsion", "hydrogen fuel cells")
20. known_development_stage
21. action
### The response should be a json.
"""

 
class PerplexityChat:
    def __init__(self, api_key: str, prompt: Prompt):
        self.prompt = prompt.construct_prompt()
        self.api_key = api_key
        if not self.api_key:
            raise EnvironmentError("PERPLEXITY_API_KEY environment variable not set")
        try:
            self.ua = UserAgent().random
        except Exception:
            self.ua = "Mozilla/5.0 (compatible; PerplexityBot/1.0)"

    async def send_request(self, session: aiohttp.ClientSession, timeout: float = 500.0) -> tuple[str, int]:
        if not self.prompt:
            return "Invalid prompt", 500

        body = {
            "model": "sonar-reasoning",
            "messages": [
                {"role": "user", "content": self.prompt}
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "schema": GoogleResponseModel.model_json_schema()
                }
            },
            "temperature": 0.01
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": self.ua
        }

        try:
            async with session.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status == 200:
                    try:
                        result = await resp.json()
                        content = result.get("choices", [{}])[0].get("message", {}).get("content", {})
                        return content, 200
                    except Exception:
                        return "Malformed response", 502
                else:
                    error_text = await resp.text()
                    return f"Error {resp.status}: {error_text}", resp.status

        except aiohttp.ClientError as e:
            return f"HTTP Client Error: {str(e)}", 503
        except asyncio.TimeoutError:
            return "Request timed out", 504
        except Exception as e:
            return f"Unexpected Error: {str(e)}", 500


    def extract_json_from_markdown_reasoning(self, response: str) -> Dict[str, Any]:
        marker = "</think>"
        idx = response.rfind(marker)
        
        if idx == -1:
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                raise ValueError("No </think> marker found and content is not valid JSON") from e

        json_str = response[idx + len(marker):].strip()

        if json_str.startswith("```json"):
            json_str = json_str[len("```json"):].strip()
        if json_str.startswith("```"):
            json_str = json_str[3:].strip()
        if json_str.endswith("```"):
            json_str = json_str[:-3].strip()
        
        try:
            parsed_json = json.loads(json_str)
            return parsed_json
        except json.JSONDecodeError as e:
            raise ValueError("Failed to parse valid JSON from response content") from e


    def extract_json_from_markdown(self, completion: Dict[str, Any]) -> Dict[str, Any]:
        try:
            raw_content = completion.strip()

            if raw_content.startswith("```"):
                lines = raw_content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_content = "\n".join(lines).strip()

            start = raw_content.find("{")
            end = raw_content.rfind("}")
            json_candidate = None
            if start != -1 and end != -1 and start < end:
                json_candidate = raw_content[start:end+1].strip()
            
            if json_candidate:
                try:
                    parsed_json = json.loads(json_candidate)
                except json.JSONDecodeError:
                    match = re.search(r"({.*})", raw_content, re.DOTALL)
                    if match:
                        json_candidate = match.group(1).strip()
                        parsed_json = json.loads(json_candidate)
                    else:
                        raise ValueError("No valid JSON object found via regex.")
            else:
                match = re.search(r"({.*})", raw_content, re.DOTALL)
                if match:
                    json_candidate = match.group(1).strip()
                    parsed_json = json.loads(json_candidate)
                else:
                    raise ValueError("No JSON object found in content.")
            return parsed_json
        except Exception as e:
            raise ValueError(f"Error extracting valid JSON from content: {e}")


async def data_enrichment(data: Dict[str, Any], limiter: Optional[AsyncLimiter] = None, key: str = None):
    perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY") or key
    if not perplexity_api_key:
        print("Error: PERPLEXITY_API_KEY environment variable not set.")
        return
    
    company_name = data.get("company_name")
    company_website = data.get("company_website")

    prompt_obj = Prompt(company_name=company_name, company_website=company_website)
    perplexity_chat = PerplexityChat(api_key=perplexity_api_key, prompt=prompt_obj)
    async with aiohttp.ClientSession() as session:
        if limiter:
            async with limiter:
                content, status = await perplexity_chat.send_request(session)
        else:
                content, status = await perplexity_chat.send_request(session)

        if content and content.strip().startswith("{"):
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                print("JSON decoding failed:", e)
        else:
            try:
                return perplexity_chat.extract_json_from_markdown_reasoning(content)
            except Exception as e:
                print(e)
                print("Received empty or invalid response:", repr(content))

def append_to_json_file(new_data, filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_data.append(new_data)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

def read_csv_to_dicts(file_path):
    companies = []
    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get("Companies") or None
            website = row.get("Company Website") or None
            companies.append({"name": name, "website": website})
    return companies

async def run_enrichment(file_path):
    data = read_csv_to_dicts(file_path=file_path)
    key = "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"

    for dp in data:
        name = dp.get("name") or None
        website = dp.get("website") or None
        input_dp = InputModel(
            company_name=name,
            company_website=website
        )

        de = await data_enrichment(data=input_dp.model_dump(), key=key)
        de["Name"] = name
        de["Website"] = website
        append_to_json_file(de, "perplexity_enriched_data_v2_tab_2.json")
        print("Done")

async def main(file_path):
    data = read_csv_to_dicts(file_path=file_path)
    key = "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"

    for dp in data:
        name = dp.get("name") or None
        website = dp.get("website") or None
        input_dp = InputModel(
            company_name=name,
            company_website=website
        )

        de = await data_enrichment(data=input_dp.model_dump(), key=key)
        de["Name"] = name
        de["Website"] = website
        append_to_json_file(de, "perplexity_enriched_data_v2_tab_2.json")
        print("Done")


if __name__ == "__main__":
    path = Path("TB test Run 2_Tab 2.csv")
    asyncio.run(main(path))
