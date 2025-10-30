import json
from pathlib import Path
from typing import Any, Dict, Union
import spacy
import hashlib


nlp = spacy.load("en_core_web_sm")  # Make sure to run: python -m spacy download en_core_web_sm

def load_json(file_path: Union[str, Path]) -> Dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data: Dict, file_path: Union[str, Path]) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class SpaCyJsonAnonymizer:
    def __init__(self, irreversible: bool = False):
        self.replacements = {
            "PERSON": {},
            "ORG": {},
            "GPE": {},
            "DATE": {},
            "EMAIL": {},
            "URL": {},
            "PHONE": {}
        }
        self.counters = {k: 1 for k in self.replacements.keys()}
        self.irreversible = irreversible

    def anonymize(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: self.anonymize(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.anonymize(item) for item in data]
        elif isinstance(data, str):
            return self._anonymize_string(data)
        else:
            return data

    def _anonymize_string(self, text: str) -> str:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in self.replacements:
                text = text.replace(ent.text, self._replace(ent.label_, ent.text))
        
        text = self._replace_pattern(text, r"https?://[^\s]+", "URL")
        text = self._replace_pattern(text, r"[\w\.-]+@[\w\.-]+\.\w+", "EMAIL")
        text = self._replace_pattern(text, r"\+?\d[\d\s\-\(\)]{7,}\d", "PHONE")

        return text

    def _replace(self, category: str, original: str) -> str:
        if self.irreversible:
            hashed = hashlib.sha256(original.encode()).hexdigest()[:10]
            return f"{category}_{hashed}"
        else:
            if original not in self.replacements[category]:
                tag = f"{category}_{self.counters[category]}"
                self.replacements[category][original] = tag
                self.counters[category] += 1
            return self.replacements[category][original]

    def _replace_pattern(self, text: str, pattern: str, category: str) -> str:
        import re
        regex = re.compile(pattern)
        return regex.sub(lambda m: self._replace(category, m.group()), text)


if __name__ == "__main__":
    input_path = Path("data/honda.json")
    output_path = Path("data/new_honda_f.json")
    mapping_path = Path("data/honda_replacements_f.json")

    anonymizer = SpaCyJsonAnonymizer(irreversible=False)
    data = load_json(input_path)
    anonymized_data = anonymizer.anonymize(data)

    save_json(anonymized_data, output_path)
    save_json(anonymizer.replacements, mapping_path)

    print(f"✅ Anonymized data saved to: {output_path}")
    print(f"🔐 Mapping saved to: {mapping_path}")
