import json
import re

def generate_layout_from_copybook(copybook_path):
    """
    Dynamically parses a COBOL copybook file to calculate field indices.
    Automatically handles tracking the shifting character positions.
    """
    layout = {}
    current_position = 0
    
    # Regex to look for field names and their PIC lengths (e.g., CLAIM-ID and X(11))
    pattern = re.compile(r'05\s+([\w\-]+)\s+PIC\s+[X9]\((\d+)\)')
    
    with open(copybook_path, "r") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                # Convert COBOL field name to pythonic lowercase style (CLAIM-ID -> claim_id)
                field_name = match.group(1).strip().lower().replace("-", "_")
                field_length = int(match.group(2))
                
                # Calculate the start and end slicing indices automatically!
                start_idx = current_position
                end_idx = current_position + field_length
                
                layout[field_name] = (start_idx, end_idx)
                
                # Advance the pointer forward for the next field in the row
                current_position = end_idx
                
    return layout

def stream_and_parse_file(file_path, dlq_path, copybook_path):
    """
    Streams the mainframe file using a dynamically generated layout map.
    """
    # Generate the map dynamically at runtime!
    dynamic_layout = generate_layout_from_copybook(copybook_path)
    
    with open(file_path, "r") as file, open(dlq_path, "w") as dlq_file:
        for line_number, line in enumerate(file, 1):
            if not line.strip():
                continue
                
            parsed_record = {}
            
            # Slice line using our dynamically calculated positions
            for field, (start, end) in dynamic_layout.items():
                parsed_record[field] = line[start:end].strip()
            
            try:
                # 1. Parse the 9-digit string into a float and divide by 100
                raw_float = float(parsed_record["claim_amount"]) / 100.0
                
                cleaned_amount = f"{raw_float:.2f}"
                
                final_record = {
                    "claim_id": parsed_record["claim_id"],
                    "member_name": parsed_record["member_name"],
                    "date_of_service": parsed_record["date_of_service"],
                    "amount": cleaned_amount,  # Now a perfectly formatted string
                    "status": parsed_record["claim_status"]
                }
                yield final_record
                
            except ValueError as e:
                error_log = {
                    "line_number": line_number,
                    "error_reason": f"Invalid numeric format: {str(e)}",
                    "raw_data": line.strip()
                }
                dlq_file.write(json.dumps(error_log) + "\n")
                continue

# --- TEST LOCAL EXECUTOR ---
if __name__ == "__main__":
    copybook = "claims_copybook.txt"
    input_file = "legacy_claims.txt"
    dead_letter_file = "dead_letter_queue.txt"
    
    print("--- Dynamic Copybook Map Generated ---")
    print(json.dumps(generate_layout_from_copybook(copybook), indent=2))
    print("\n--- Running Dynamic Integration Pipeline ---\n")
    
    for record in stream_and_parse_file(input_file, dead_letter_file, copybook):
        print(json.dumps(record, indent=2))