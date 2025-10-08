from aiolimiter import AsyncLimiter
from google import genai
from google.genai import types
from google.genai.types import GenerateContentResponse
from typing import Any, Dict, Optional

import json
import os
import re


class Prompt:
    def __init__(self, company_name: str = "", company_website: str = ""):
        if company_name != "":
            self.company_name = company_name
        self.company_website = company_website
    
    def construct_prompt(self) -> str:
        return f"""
You are a company analyst and deep-tech investment screener.
You will analyze companies for relevance to our hard-tech investment thesis and enterprise tool applicability.

Given the following information:
    - Company Name: {self.company_name}  
    - Company Website: {self.company_website}  

---

CRITICAL DECISION FLAGS (MUST FOLLOW)
1. Investment vs Tool Decision Tree
    - Set in_scope=FALSE and relevance=FALSE if company:
        - Does not advance physical or deep-tech systems in mobility, energy, sustainability, or materials.
        - Is primarily a software-only tool, AI platform, cybersecurity system, or enterprise SaaS (even if valuable).
        - Involves pharma, biotech, core IT infrastructure, finance, research and development, agricultural tech, high-performance computing, food tech, or property tech, mineral exploration and oil and gas industry (gas and liquid separation at high temperature).

    - Set in_scope=FALSE and relevance=TOOL only if:
        - The company may be useful as a tool, integration, or database solution for enterprise operations (e.g., Genloop, Bonfy.ai, Cogent Security).
    
    DO NOT set in_scope=TRUE unless they also match investment thesis.

2. Investment Thesis Relevance (Set in_scope=TRUE and relevance=INVESTMENT)
    - Only if the company advances breakthrough hard-tech in:
        - Mobility: micro/urban/off-grid, EV platforms, autonomous nav, energy-efficient transport.
        - Sustainability: next-gen batteries, circular economy tech, hydrogen, low-energy systems.
        - Moonshots: new materials, computing, sensors, energy systems, fusion, satellites, etc.
        - Manufacturing Tech

3. Master Essence Check
    - Must be "scaling breakthrough physical technology for a sustainable world."
    - If it's SaaS-only, AI-only, enterprise ops only, or analytics only, it is not in scope.

---

EXCLUSIONS (Hard Rules)
❌ AI platforms, LLM tools, developer tooling = only tools, not investment
❌ Cybersecurity = tool only, not investment
❌ Enterprise SaaS, e-commerce ops, finance AI, medtech, biotech = always out of scope
❌ Climate fintech, SaaS billing for energy = too abstract, no breakthrough tech, always out of scope

---

EDGE CASE HANDLING
- If out of scope for investment but may be useful for Honda:
- Set in_scope=FALSE, relevance=TOOL, and short reason in "explanation"

---

SCORING RUBRIC (0-10 integers)
 * Uniqueness (50%) = Novelty, IP strength, difficulty to reproduce  
   - 0 = commodity / generic IT  
   - ≤1 if “tool only, not investment”  
   - ≤3 if “too many players” / “business model only”  
   - ≤4 if “unclear advantage” / “used to be unique”  
   - ≥8 if “first-of-kind” / “never done before” / “fundamental science breakthrough”  
 * Effectiveness (30%) = Proof tech works  
   - 0 = none  
   - ≤4 if only R&D / vague pilots  
   - ≥7 if OEMs, scale deployments, validations  
 * Market Differentiation (20%) = Niche clarity & moat  
   - ≤2 if crowded market  
   - ≥7 if rare niche with clear moat/IP  

---

**GUARDRAILS**  
 * WOW Line:  
   - uniqueness ≤4 → wow_one_liner="None"  
   - uniqueness ≥8 → must highlight “breakthrough / first-of-kind”  
 * Crowded Domains Cap:  
   - Autonomous driving full-stack ≤3  
   - EV charging platforms ≤3  
   - Warehouse robotics, DMS, water-from-air ≤3  
 * Negative Overrides:  
   - “Unclear advantage,” “too many players” → uniqueness ≤4  
   - “Similar players,” “crowded” → uniqueness ≤3  
 * Confidence Scaling:  
   - Vague → confidence="Low", scores ≤4  
   - Otherwise = Medium/High  

---

**COMPUTATION**  
combined_score = round( uniqueness_score*0.5 + effectiveness_score*0.3 + market_diff_score*0.2 )  

---

**OUTPUT_SCHEMA**  
### Provide result as a JSON with fields:  
1. company_name  
2. in_scope
3. relevance
4. explanation  
5. uniqueness_score  
6. uniqueness_why  
7. effectiveness_score  
8. effectiveness_why  
9. market_diff_score  
10. combined_score  
11. confidence  
12. brief_description  
13. wow_one_liner  
14. founders  
15. technologies  
16. applications  
17. products  
18. customer_engagements  
19. hq_location  
20. current_funding_information  
21. core_technology_used  
22. known_development_stage  
23. action  
""".strip()


class GeminiChat:
    __model_name: str = "gemini-2.5-pro"
    
    def __init__(self, api_key: str, prompt: str):
        self.prompt: str = prompt
        self.api_key: str = api_key

        if not self.api_key:
            raise EnvironmentError("GEMINI_KEY environment variable not set")

    async def send_request(self) -> Dict[str, Any]:
        client = genai.Client(
            api_key=self.api_key
        ).aio

        try:
            grounding_tool = types.Tool(
                google_search=types.GoogleSearch()
            )
            config = types.GenerateContentConfig(
                tools=[grounding_tool]
            )

            response: GenerateContentResponse = await client.models.generate_content(
                model=self.__model_name,
                contents=self.prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            print(f"An error occurred during content generation: {e}")
            raise 


def extract_json_from_markdown(completion: Dict[str, Any]) -> Dict[str, Any]:
    try:
        raw_content: str = completion.strip()

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

async def run_enrichment(logger, data: Dict[str, Any], limiter: Optional[AsyncLimiter] = None) -> Optional[Dict[str, Any]]:
    gemini_api_key = os.environ.get("GEMINI_KEY")
    extracted_data = None

    if not gemini_api_key:
        logger.error("Error: GEMINI_KEY environment variable not set.")
        return

    name: str = data.get("name") or ""
    website: str = data.get("website") or ""

    try:
        prompt = Prompt(company_name=name, company_website=website)
        gemini_enchriment = GeminiChat(
            api_key=gemini_api_key,
            prompt=prompt.construct_prompt()
        )
        logger.info(f"Processing: {name}")

        if limiter:
            async with limiter:
                response = await gemini_enchriment.send_request()
        else:
            response = await gemini_enchriment.send_request()

        if response:
            extracted_data = extract_json_from_markdown(response)
        else:
            logger.warning(f"No result for {name}")
    except Exception as e:
        print(f"Attempt failed: {e}")
    return extracted_data
