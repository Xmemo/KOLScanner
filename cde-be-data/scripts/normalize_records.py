import csv
import json

INPUT = "cde-be-data/sample_records.csv"
OUTPUT = "cde-be-data/processed.json"

def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def normalize(rows):
    normalized = []
    for i, r in enumerate(rows):
        normalized.append({
            "id": f"record-{i}",
            "generic_name": r.get("generic_name"),
            "manufacturer": r.get("manufacturer"),
            "acceptance_no": r.get("acceptance_no"),
            "auc_ci": [r.get("auc_ci_lower"), r.get("auc_ci_upper")],
            "cmax_ci": [r.get("cmax_ci_lower"), r.get("cmax_ci_upper")],
            "source_url": r.get("source_url")
        })
    return normalized

if __name__ == "__main__":
    rows = load_csv(INPUT)
    data = normalize(rows)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("done")
