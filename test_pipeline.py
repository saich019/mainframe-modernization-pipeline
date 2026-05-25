import unittest
import os
from parser import stream_and_parse_file

class TestMainframePipeline(unittest.TestCase):
    def setUp(self):
        self.input_file = "legacy_claims.txt"
        self.dlq_file = "dead_letter_queue.txt"
        self.copybook_file = "claims_copybook.txt"

    def test_pipeline_execution(self):
        """Test that the dynamic pipeline correctly parses using the copybook schema."""
        records = list(stream_and_parse_file(self.input_file, self.dlq_file, self.copybook_file))
        
        # 1. Assert that we successfully processed 3 clean records
        self.assertEqual(len(records), 3)
        
        # 2. Assert that the first record was parsed accurately
        self.assertEqual(records[0]["claim_id"], "CLAIM000001")
        self.assertEqual(records[0]["amount"], "450.00")
        
        # 3. Assert that the Dead-Letter Queue file caught the corrupted row
        self.assertTrue(os.path.exists(self.dlq_file))
        with open(self.dlq_file, "r") as f:
            dlq_content = f.readlines()
        self.assertEqual(len(dlq_content), 1)

if __name__ == "__main__":
    unittest.main()