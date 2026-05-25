import json

COPYBOOK_LAYOUT = {
    "claim_id": (0, 11),
    "member_name": (11, 29),
    "date_of_service": (29, 37),
    "amount_raw": (37, 45),
    "status": (46, 55)
}

def stream_and_parse_file(file_path, dlq_path):
    """
    Streams a file line-by-line, parses layout fields, handles implicit decimals,
    and isolates corrupt data into a Dead-Letter Queue (DLQ) file.
    """
    with open(file_path, "r") as file, open(dlq_path, "w") as dlq_file:
        for line_number, line in enumerate(file, 1):
            if not line.strip():
                continue
                
            parsed_record = {}
            
            # Slice raw data strings
            for field, (start, end) in COPYBOOK_LAYOUT.items():
                parsed_record[field] = line[start:end].strip()
            
            # ENTERPRISE VALIDATION & FAULT TOLERANCE LAYER
            try:
                # 1. Convert the raw string amount into a numeric float
                # Example: "00004500" -> 4500 -> 45.00 (handling the implicit decimal V)
                raw_amount = parsed_record["amount_raw"]
                cleaned_amount = float(raw_amount) / 100.0
                
                # Update the record structure with clean types
                final_record = {
                    "claim_id": parsed_record["claim_id"],
                    "member_name": parsed_record["member_name"],
                    "date_of_service": parsed_record["date_of_service"],
                    "amount": cleaned_amount,
                    "status": parsed_record["status"]
                }
                
                yield final_record
                
            except ValueError as e:
                # Catching numeric conversion failures (e.g., if amount contains 'XX')
                print(f"[WARNING] Line {line_number} is corrupted. Isolating to DLQ.")
                
                # Write to the Dead-Letter Queue file for human auditing
                error_log = {
                    "line_number": line_number,
                    "error_reason": f"Invalid numeric format: {str(e)}",
                    "raw_data": line.strip()
                }
                dlq_file.write(json.dumps(error_log) + "\n")
                
                # Crucial: 'continue' ensures the application does NOT crash
                continue

# --- TEST EXECUTOR ---
if __name__ == "__main__":
    input_file = "legacy_claims.txt"
    dead_letter_file = "dead_letter_queue.txt"
    
    print("--- Starting Resilient Mainframe Pipeline ---\n")
    
    for record in stream_and_parse_file(input_file, dead_letter_file):
        print("Clean Record Processed:")
        print(json.dumps(record, indent=2))
        print("-" * 30)