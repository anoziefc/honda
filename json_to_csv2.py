import json
import csv
import re


def remove_citations(text: str) -> str:
    return re.sub(r' \[\d+(?:, \d+)*\]', '', text)

with open("data/gemini_enriched_data_essence.json", "r", encoding="utf-8") as f:
    data = json.load(f)

new_data = []
for item in data:
    new_item = {}
    for key, value in item.items():
        if isinstance(value, str):
            new_item[key] = remove_citations(value)
        else:
            new_item[key] = value
    new_data.append(new_item)

csv_file = "GEDET1.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=[
        "Company Name",
        "In Scope?",
        "Uniqueness Score",
        "Uniqueness Why?",
        "Function/Effectiveness score",
        "Effectiveness Why?",
        "Market Difference Score",
        "Combined Score",
        "Confidence Level",
        "Brief Description",
        "Wow!",
        "Founders",
        "Technologies",
        "Applications",
        "Products",
        "Customer Engagements",
        "HQ",
        "Funding Information",
        "Core Technology",
        "Development Stage",
        "Action"
    ])

    writer.writeheader()

    for item in new_data:
        row = {
            "Company Name": item["company_name"],
            "In Scope?": item["in_scope"],
            "Uniqueness Score": item["uniqueness_score"],
            "Uniqueness Why?": item["uniqueness_why"],
            "Function/Effectiveness score": item["effectiveness_score"],
            "Effectiveness Why?": item["effectiveness_why"],
            "Market Difference Score": item["market_diff_score"],
            "Combined Score": item["combined_score"],
            "Confidence Level": item["confidence"],
            "Brief Description": item["brief_description"],
            "Wow!": item["wow_one_liner"],
            "Founders": item["founders"],
            "Technologies": item["technologies"],
            "Applications": item["applications"],
            "Products": item["products"],
            "Customer Engagements": item["customer_engagements"],
            "HQ": item["hq_location"],
            "Funding Information": item["current_funding_information"],
            "Core Technology": item["core_technology_used"],
            "Development Stage": item["known_development_stage"],
            "Action": item["action"]
        }

        writer.writerow(row)

print(f"✅ CSV file written to: {csv_file}")
