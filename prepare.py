from pathlib import Path

import csv
import json


def prepare_file(file_path: Path, output_dir: Path, chunk_size: int = 1000):
    companies = []
    with open(file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get("Account Name") or None
            website = row.get("Website") or None
            companies.append({"name": name, "website": website})

    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(0, len(companies), chunk_size):
        chunk = companies[i:i+chunk_size]
        chunk_file = output_dir / f"companies_{i//chunk_size + 1}.json"
        with open(chunk_file, "w", encoding="utf-8") as json_file:
            json.dump(chunk, json_file, indent=4, ensure_ascii=False)


fp = Path("data/data.csv")
op = Path("data")
prepare_file()