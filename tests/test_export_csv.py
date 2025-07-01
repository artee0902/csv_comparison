import csv
import os
import pytest
import allure

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

@allure.step("Create CSV file: {filename}")
def create_csv(filename, rows):
    filepath = os.path.join(EXPORT_DIR, filename)
    with open(filepath, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "Name", "Price"])
        writer.writeheader()
        writer.writerows(rows)
    attach_csv(filepath)
    return filepath

@allure.step("Read CSV: {file_path}")
def read_csv(file_path):
    assert os.path.exists(file_path), f" File not found: {file_path}"
    with open(file_path, newline='') as csvfile:
        return list(csv.DictReader(csvfile))

@allure.step("Attach CSV to Allure: {file_path}")
def attach_csv(file_path):
    with open(file_path, "rb") as f:
        allure.attach(f.read(), name=os.path.basename(file_path), attachment_type=allure.attachment_type.CSV)

@allure.step("Compare CSVs: {file1} vs {file2}")
def compare_csvs(file1, file2):
    data1 = read_csv(file1)
    data2 = read_csv(file2)

    diff_rows = [row for row in data1 if row not in data2]

    allure.attach(f"{len(data1)} rows in {file1}\n{len(data2)} rows in {file2}", name="Row Count Comparison", attachment_type=allure.attachment_type.TEXT)

    if diff_rows:
        diff_text = "\n".join([str(row) for row in diff_rows])
        allure.attach(diff_text, name="Mismatched Rows", attachment_type=allure.attachment_type.TEXT)

    assert not diff_rows, "CSVs differ"

# ------------------- TESTS ------------------------

@allure.title("Step 1: Export file1.csv with 5 rows")
@allure.feature("CSV Export")
@allure.severity(allure.severity_level.NORMAL)
def test_export_csv_file1():
    rows = [
        {"ID": "1", "Name": "Apple", "Price": "100"},
        {"ID": "2", "Name": "Banana", "Price": "40"},
        {"ID": "3", "Name": "Cherry", "Price": "60"},
        {"ID": "4", "Name": "Date", "Price": "80"},
        {"ID": "5", "Name": "Elderberry", "Price": "120"},
    ]
    create_csv("file1.csv", rows)

@allure.title("Step 2: Export file2.csv with 3 rows")
@allure.feature("CSV Export")
@allure.severity(allure.severity_level.NORMAL)
def test_export_csv_file2():
    rows = [
        {"ID": "1", "Name": "Apple", "Price": "100"},
        {"ID": "2", "Name": "Banana", "Price": "40"},
        {"ID": "3", "Name": "Cherry", "Price": "60"}
    ]
    create_csv("file2.csv", rows)


@allure.title("Step 3: Compare file1.csv with file2.csv")
@allure.feature("CSV Comparison")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("Validate that both exported CSV files have matching data rows")
def test_compare_exported_csvs():
    file1 = os.path.join(EXPORT_DIR, "file1.csv")
    file2 = os.path.join(EXPORT_DIR, "file2.csv")
    compare_csvs(file1, file2)
