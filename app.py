from flask import Flask, jsonify, request
from parser import stream_and_parse_file

app = Flask(__name__)

INPUT_FILE = "legacy_claims.txt"
DEAD_LETTER_FILE = "dead_letter_queue.txt"

@app.route('/api/v1/claims', methods=['GET'])
def get_modernized_claims():
    """
    REST API Endpoint that triggers the mainframe data pipeline
    and streams the clean JSON payloads back to the client.
    """
    try:
        clean_records = []
        
        # Consume our streaming generator from parser.py
        for record in stream_and_parse_file(INPUT_FILE, DEAD_LETTER_FILE):
            clean_records.append(record)
            
        # Return the clean array as a web-standard JSON response
        return jsonify({
            "status": "success",
            "total_records_processed": len(clean_records),
            "data": clean_records
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Pipeline execution failed: {str(e)}"
        }), 500

if __name__ == "__main__":
    # Run the web server locally on port 5000
    print("--- Starting Modernized API Gateway Layer ---")
    app.run(host="0.0.0.0", port=5000, debug=True)