from aiolimiter import AsyncLimiter
from google import genai
from google.genai import types
from typing import Any, Dict, Optional
import json
import os
import re


class Prompt:
    def __init__(self, company_name: str = None, company_website: str = None):
        self.company_name = company_name
        self.company_website = company_website
    
    def construct_prompt(self) -> str:
        return f"""
You are a company analyst and technical investment screener.  
Your role is to evaluate early and growth-stage startups or technologies that may align with our investment thesis.  

**INVESTMENT THESIS**
We invest in companies advancing:
 * Mobility: novel ways of moving people/goods (personal, shared, micro, rural, off-grid, autonomous, low-infrastructure).  
 * Sustainability: alternative propulsion (electric, solar, hydrogen), energy storage, circular economy, low-energy manufacturing.  
 * Moonshots: highly ambitious, transformational, technologically hard-to-build solutions (breakthroughs > incremental).  

**MASTER ESSENCE**
Scaling breakthrough technology for a sustainable world.  

**OTHER ESSENCES (reference set of aligned companies):**
 - Tozero Solutions: Sustainable lithium-ion battery circular economy  
 - Reverion: Climate-positive energy generation from biogas  
 - Silc: Democratizing alternative asset investments  
 - nT-Tao Compact Fusion Power: Compact, scalable fusion reactors  
 - Ineratec: Modular Power-to-X for defossilization  
 - Seurat: Scalable metal additive manufacturing  
 - Sono Charge Energy: Acoustic wave battery performance  
 - Drivemode: Safer in-car user experience  
 - SoundHound AI: Conversational voice intelligence  
 - SES AI: AI-powered lithium-metal EV batteries  
 - helm.ai: AI software for autonomous driving  
 - Emulsion Flow Tech: Advanced rare metal recycling  
 - Princeton Nuenergy: Direct, cost-efficient battery recycling  

**EXCLUSIONS**
Do NOT evaluate companies primarily focused on:
 - Cybersecurity (unless tagged as database tool, not investment)  
 - Core IT infrastructure, SaaS logistics, warehousing, storage, or pharma  
 - Healthcare/medtech, biotech, fintech, big power plants, or grids  

**EXCEPTION**  
AI/cybersecurity → evaluate **only as tools for database**, not as investment opportunities.  

---

Given the following information:
Company Name: {self.company_name}  
Company Website: {self.company_website}  

**CRITICAL**
Only evaluate companies that directly advance mobility, propulsion, battery systems, charging infrastructure, hydrogen production, navigation/positioning, materials innovation, or related sustainable technologies.  
If company is outside scope, set `in_scope=false` and explain WHY in ≤25 words.  

---

**SCORING RUBRIC (0-10 integers)**  
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
3. uniqueness_score  
4. uniqueness_why  
5. effectiveness_score  
6. effectiveness_why  
7. market_diff_score  
8. combined_score  
9. confidence  
10. brief_description  
11. wow_one_liner  
12. founders  
13. technologies  
14. applications  
15. products  
16. customer_engagements  
17. hq_location  
18. current_funding_information  
19. core_technology_used  
20. known_development_stage  
21. action  
"""


class GeminiChat:
    __model_name: str = "gemini-2.5-pro"

    def __init__(self, api_key: str, prompt: Prompt):
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


def extract_json_from_markdown(completion: Dict[str, Any]) -> Dict[str, Any]:
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

async def run_enrichment(logger, data: Dict[str, Any], limiter: Optional[AsyncLimiter] = None) -> Optional[Dict[str, Any]]:
    gemini_api_key = os.environ.get("GEMINI_KEY")
    extracted_data = None

    if not gemini_api_key:
        logger.error("Error: GEMINI_KEY environment variable not set.")
        return

    name = data.get("name") or None
    website = data.get("website") or None

    try:
        prompt = Prompt(company_name=name, company_website=website)
        gemini_enchriment = GeminiChat(api_key=gemini_api_key, prompt=prompt.construct_prompt())
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
