
import json

file_path = r"c:\Users\abhis\OneDrive\Desktop\abhigit\Toeho-AI\Basics\2.Scrape_data_to_csv.ipynb"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb.get('cells', [])
    print(f"Total cells: {len(cells)}")

    # Check cells 28 to 32 (indices 27 to 31)
    for i in range(27, 33):
        if i < len(cells):
            cell = cells[i]
            cell_type = cell.get('cell_type', 'unknown')
            source_lines = cell.get('source', [])
            source_text = "".join(source_lines)
            print(f"\n--- Cell {i + 1} ({cell_type}) ---")
            print(f"Content:\n{source_text}")
            print(f"Repr: {repr(source_text)}")
            print("-----------------------")

except Exception as e:
    print(f"Error: {e}")
