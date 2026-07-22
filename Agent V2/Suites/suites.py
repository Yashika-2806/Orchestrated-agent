
import os
import csv
import zipfile
import shutil

# ── Config ──────────────────────────────────────────
RESUME_FOLDER = "resumes"         
OUTPUT_FOLDER = "test_suites"
CSV_FILES = {
    "year2": "year2_data.csv",
    "year3": "year3_data.csv",
    "year4": "year4_data.csv",
}
# ────────────────────────────────────────────────────

def validate_row(row, i):
    errors = []
    if not row.get("roll_number"):
        errors.append("missing roll_number")
    if not row.get("name"):
        errors.append("missing name")
    if not row.get("gpa"):
        errors.append("missing gpa")
    if not row.get("linkedin"):
        errors.append("missing linkedin (required)")
    if not row.get("github"):
        errors.append("missing github (required)")
    if errors:
        print(f"  ⚠️  Row {i+1} ({row.get('roll_number','?')}): {', '.join(errors)}")
    return len(errors) == 0

def gpa_category(gpa):
    try:
        g = float(gpa)
        if g >= 8.5: return "High"
        if g >= 7.0: return "Mid"
        if g >= 5.5: return "Low"
        return "Very Low"
    except:
        return "Unknown"

def process_suite(label, csv_file):
    if not os.path.exists(csv_file):
        print(f"  ❌ {csv_file} not found — skipping.")
        return

    print(f"\n── Processing {label} from {csv_file} ──")

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("  ❌ CSV is empty.")
        return

    print(f"  Found {len(rows)} rows")

    # validate
    valid_rows = []
    for i, row in enumerate(rows):
        if validate_row(row, i):
            valid_rows.append(row)

    print(f"  ✅ {len(valid_rows)} valid rows")

  
    cats = {"High": 0, "Mid": 0, "Low": 0, "Very Low": 0}
    for row in valid_rows:
        cats[gpa_category(row.get("gpa","0"))] += 1
    print(f"  GPA spread — High(8.5+): {cats['High']}  Mid(7-8.5): {cats['Mid']}  Low(5.5-7): {cats['Low']}  Very Low: {cats['Very Low']}")

    
    with_lc = sum(1 for r in valid_rows if r.get("leetcode","").strip())
    with_cf = sum(1 for r in valid_rows if r.get("codeforces","").strip())
    print(f"  Coding platforms — LeetCode: {with_lc}/{len(valid_rows)}  Codeforces: {with_cf}/{len(valid_rows)}")

    zip_path = os.path.join(OUTPUT_FOLDER, f"{label}_resumes.zip")
    missing_pdfs = []
    added = 0

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for row in valid_rows:
            roll = row["roll_number"].strip()
            pdf_name = f"{roll}.pdf"
            pdf_path = os.path.join(RESUME_FOLDER, pdf_name)
            if os.path.exists(pdf_path):
                zf.write(pdf_path, pdf_name)
                added += 1
            else:
                missing_pdfs.append(pdf_name)

    print(f"  📦 ZIP: {zip_path}  ({added} PDFs added)")
    if missing_pdfs:
        print(f"  ⚠️  Missing PDFs (not found in resumes/ folder):")
        for m in missing_pdfs:
            print(f"       {m}")

    # write final CSV with gpa_category added
    final_csv = os.path.join(OUTPUT_FOLDER, f"{label}_final.csv")
    fieldnames = list(valid_rows[0].keys()) + ["gpa_category", "pdf_in_zip"]
    with open(final_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in valid_rows:
            roll = row["roll_number"].strip()
            row["gpa_category"] = gpa_category(row.get("gpa","0"))
            row["pdf_in_zip"] = "Yes" if f"{roll}.pdf" not in missing_pdfs else "No"
            writer.writerow(row)

    print(f"  📋 CSV:  {final_csv}")

def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(RESUME_FOLDER, exist_ok=True)

    for label, csv_file in CSV_FILES.items():
        process_suite(label, csv_file)

    print("\n✅ Done! Check test_suites/ folder.")

if __name__ == "__main__":
    main()
