from aiolimiter import AsyncLimiter
from google import genai
from google.genai import types
from google.genai.types import GenerateContentResponse
from typing import Any, Dict, Optional
from company_info import GeminiChat as cigc, Prompt as cip

import json
import os
import re


class Prompt:
    def __init__(self, company_name: str = "", company_website: str = ""):
        if company_name != "":
            self.company_name = company_name
        self.company_website = company_website
    
    def comparison_prompt(self, base_data: Dict = {}, company_data: Dict = {}) -> str:
        return f"""
You are a professional business analyst specializing in mergers, acquisitions, and investment evaluations.
You are provided with detailed data about two companies — Company A (the investing company) and Company B (the potential investment target).
The data is formatted as JSON objects with the same structure.

---
### Company A Data: {base_data}
### Company B Data: {company_data}

** Your Tasks **
    - Data Integration
        - Combine the data into a unified comparative framework.
        - Identify shared attributes, metrics, and relevant key performance indicators (KPIs).
    -  Comparative Analysis
        - Highlight similarities and differences across categories such as:
            - Business model
            - Market segment
            - Financial health
            - Growth trends
            - Customer base
            - Product or service portfolio
            - Operational strengths and weaknesses
    - Investment Fit Assessment
        - Evaluate whether Company B aligns strategically and financially with Company A.
        - Identify synergies, potential conflicts, and integration challenges.
        - Provide an assessment of the risk and opportunity profile.
    - Actionable Insights & Recommendations
        - Based on the above analysis, clearly state:
            - Whether Company B is a good investment or partnership opportunity for Company A.
            - Recommended next steps or due diligence areas.
            - Any cautions or red flags.

    **OUTPUT_SCHEMA**
    ### Provide result as a structured JSON with fields:
            
    {{
        "summary": "Brief executive summary of both companies and the overall evaluation.",
        "similarities": [ "List of key similarities" ],
        "differences": [ "List of key differences" ],
        "investment_fit": {{
            "strategic_alignment": "Analysis of fit in vision, market, products, etc.",
            "financial_alignment": "Analysis of revenue models, margins, valuation, etc.",
            "risk_assessment": "Potential risks or challenges in investing in Company B."
        }}
        "recommendation": {
            "is_good_investment": true,
            "rationale": "Reasoning for the recommendation",
            "next_steps": [ "Suggested actions or further research" ]
        }
    }}
"""

    def construct_prompt(self, comparison: Dict) -> str:
        return f"""
You are a company analyst and deep-tech investment screener.
You will analyze companies for relevance to our hard-tech investment thesis and enterprise tool applicability.

Given the following information:
    - Company Name: {self.company_name}
    - Company Website: {self.company_website}

---

CRITICAL DECISION FLAGS (MUST FOLLOW)
1. Investment vs Tool Decision Tree
    - Set relevance=FALSE if company:
        - Does not advance physical or deep-tech systems in mobility, energy, sustainability, or materials.
        - Is primarily a software-only tool, AI platform, cybersecurity system, or enterprise SaaS (even if valuable).
        - Involves pharma, biotech, core IT infrastructure, finance, research and development, agricultural tech, high-performance computing, food tech, or property tech, mineral exploration and oil and gas industry (gas and liquid separation at high temperature).
        - Plastic related technology (e.g., Citroniq)
        - Concrete (e.g., Carbon negative Solution)
        - Building related (e.g., CleanFiber)
        - Carbon sequestration technology that buries CO2 (e.g., Carbon Sequestration). We would like to reuse the carbon
        - Cascade Biocatalysts
        - Channing Street Copper - Home appliance is not really a thing for Honda
        - Cirkla - fresh food packaging is not really relevant for Honda

    - Set relevance=TOOL only if:
        - The company may be useful as a tool, integration, or database solution for enterprise operations (e.g., Genloop, Bonfy.ai, Cogent Security).

2. Investment Thesis Relevance (Set relevance=INVESTMENT)
    - Only if the company advances breakthrough hard-tech in:
        - Mobility: micro/urban/off-grid, EV platforms, autonomous nav, energy-efficient transport.
        - Sustainability: next-gen batteries, circular economy tech, hydrogen, low-energy systems.
        - Moonshots: new materials, computing, sensors, energy systems, fusion, satellites, etc.
        - Manufacturing Tech

    ** NOTE**
        - For any AI fabless chip design with lower-power and high-performance claims, it should be "INVESTMENT"
        - Any energy/power supply, storage technologies, and cooling systems technologies for datacenters should just stay as "INVESTMENT"
        - while home charging infrastructure is "INVESTMENT" and we will then look at the uniqueness score to decide

3. Master Essence Check
    - Must be "scaling breakthrough physical technology for a sustainable world."
    - If it's SaaS-only, AI-only, enterprise ops only, or analytics only, it is not in scope.

4. Relevance = "FUTURE" includes the following
    - Quantum-related technology
    - Space-related technology (e.g., CisLunnar)

5. Relevance = "ADJACENT"
    - Data Center interconnect, transmission, operations, edge, or board-level technology (e.g., Hyperlume, Cyclos Semiconductors, 639 Solar).
    - Technologies that are power grid-focused, AND related to Transmission, distribution, and smart meters, public EV Charging infrastructure related.
    - Drone technologies
    - Flight control and navigation
    - Textile-related (e.g., Bloom Labs)
    - Any vehicle retrofitting technology (e.g., Blue Dot Motorworks)
    - Waste-water processing
    - Forestry and wildfire control (Burnbot)
    - Agriculture (e.g, Applied Carbon)
    - Semiconductor manufacturing, material and process technologies (e.g., Cactus Materials)
    - PFAS related technology (ClarosTech)

---

EXCLUSIONS (Hard Rules)
❌ AI platforms, LLM tools, developer tooling = only tools, not investment
❌ Cybersecurity = tool only, not investment
❌ Enterprise SaaS, e-commerce ops, finance AI, medtech, biotech = always out of scope
❌ Climate fintech, SaaS billing for energy = too abstract, no breakthrough tech, always out of scope

---

EDGE CASE HANDLING
- If out of scope for investment but may be useful for our business:
- Set relevance=TOOL, and short reason in "explanation"

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
   - uniqueness ≥8 → must highlight “breakthrough / first-of-kind / novel”
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

**Be very strict with the uniqueness scoring. If it doesn't fulfil all the requirements, don't rank high.
**Relevance can only have the following values:
    - ADJACENT
    - FALSE
    - FUTURE
    - INVESTMENT
    - TOOL

---

**COMPUTATION**
combined_score = round( uniqueness_score*0.5 + effectiveness_score*0.3 + market_diff_score*0.2 )

---

**OUTPUT_SCHEMA**
### Provide result as a JSON with fields:
1. company_name
2. relevance
3. explanation
4. uniqueness_score
5. uniqueness_why
6. effectiveness_score
7. effectiveness_why
8. market_diff_score
9. combined_score
10. confidence
11. brief_description
12. wow_one_liner
13. founders
14. technologies
15. applications
16. products
17. customer_engagements
18. hq_location
19. current_funding_information
20. core_technology_used
21. known_development_stage
22. action
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

async def get_company_data(name: str, api_key: str) -> Dict:
    prompt = cip().construct_prompt(name)
    chat = cigc(
        api_key=api_key,
        prompt=prompt
    )

    resp = await chat.send_request()
    return chat.extract_json_from_markdown(resp)

async def run_enrichment(logger, data: Dict[str, Any], limiter: Optional[AsyncLimiter] = None, base_data: Dict = {}) -> Optional[Dict[str, Any]]:
    gemini_api_key = os.environ.get("GEMINI_KEY")
    extracted_data = None

    if not gemini_api_key:
        logger.error("Error: GEMINI_KEY environment variable not set.")
        return

    name: str = data.get("name") or ""
    website: str = data.get("website") or ""

    try:
        company_data = get_company_data(name, gemini_api_key)
        prompt = Prompt(company_name=name, company_website=website)
        comparison = prompt.comparison_prompt(base_data=base_data, company_data=company_data)
        gemini_enchriment = GeminiChat(
            api_key=gemini_api_key,
            prompt=prompt.construct_prompt(comparison=comparison)
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
