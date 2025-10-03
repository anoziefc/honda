import json
import csv


with open("enriched_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

csv_file = "enriched_data.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=[
        "Reasons and reference to decide why this is a unique and/or high impact candidate.",
        "Uniqueness score",
        "Confidence level for Uniqueness score",
        "Function/Effectiveness score",
        "confidence level for effectiveness scoring",
        "Brief Description (1  sentence to describe what makes it  WOW (uniqueness and Impact), and its applications",

        "Founders",
        "Technologies",
        "Applications",
        "Products",
        "Customer Engagements",

        "HQ Country",
        "HQ State/Province",
        "HQ City",

        "Funding Round",
        "Funding Amount",
        "Funding Date",
        "Funding Valuation",

        "Core Technology",
        "Application Areas",
        "Development Stage"
    ])

    writer.writeheader()

    for item in data:
        row = {
            "Reasons and reference to decide why this is a unique and/or high impact candidate.": item["brief_description"],
            "Uniqueness score": item["uniqueness_score"],
            "Confidence level for Uniqueness score": item["confidence_uniqueness"],
            "Function/Effectiveness score": item["effectiveness_score"],
            "confidence level for effectiveness scoring": item["confidence_effectiveness"],
            "Brief Description (1  sentence to describe what makes it  WOW (uniqueness and Impact), and its applications": item["reasoning_for_uniqueness_or_impact"],

            "Founders": item["long_description"]["founders"],
            "Technologies": item["long_description"]["technologies"],
            "Applications": item["long_description"]["applications"],
            "Products": item["long_description"]["products"],
            "Customer Engagements": item["long_description"]["customer_engagements"],

            "HQ Country": item["hq_location"]["country"],
            "HQ State/Province": item["hq_location"]["state_or_province"],
            "HQ City": item["hq_location"]["city"],

            "Funding Round": item["funding_info"]["last_round"],
            "Funding Amount": item["funding_info"]["amount"],
            "Funding Date": item["funding_info"]["date"],
            "Funding Valuation": item["funding_info"]["valuation"],

            "Core Technology": ", ".join(item["core_technology"]),
            "Application Areas": ", ".join(item["applications"]),
            "Development Stage": item["development_stage"]
        }

        writer.writerow(row)

print(f"✅ CSV file written to: {csv_file}")
