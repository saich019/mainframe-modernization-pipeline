from flask import Flask, jsonify
from parser import stream_and_parse_file

app = Flask(__name__)

INPUT_FILE = "legacy_claims.txt"
DEAD_LETTER_FILE = "dead_letter_queue.txt"
COPYBOOK_FILE = "claims_copybook.txt"  

@app.route('/api/v1/claims', methods=['GET'])
def get_modernized_claims():
    """
    REST API Endpoint that triggers the dynamic mainframe data pipeline
    and streams the clean JSON payloads back to the client.
    """
    try:
        clean_records = []
        
        # Consume our dynamic generator, now passing the copybook file path
        for record in stream_and_parse_file(INPUT_FILE, DEAD_LETTER_FILE, COPYBOOK_FILE):
            clean_records.append(record)
            
        return jsonify({
            "status": "success",
            "metadata_driven": True,
            "total_records_processed": len(clean_records),
            "data": clean_records
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Pipeline execution failed: {str(e)}"
        }), 500

if __name__ == "__main__":
    print("--- Starting Dynamic API Gateway Layer ---")
    app.run(host="0.0.0.0", port=5000, debug=True)