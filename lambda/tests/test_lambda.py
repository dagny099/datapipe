"""
test_lambda.py

Local test script for workout processor Lambda function.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

import json
import workout_processor

def test_handler():
    """Test the Lambda handler with a mock S3 event."""
    
    # Create a mock S3 event
    test_event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "test-bucket"},
                "object": {"key": "test.csv"}
            }
        }]
    }

    # Create mock context (optional for basic testing)
    class MockContext:
        def __init__(self):
            self.function_name = 'test-function'
            self.function_version = '$LATEST'
            self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test-function'
            self.memory_limit_in_mb = 128
            self.aws_request_id = 'test-request-id'
            
    mock_context = MockContext()

    # Call the handler
    print("\n🚀 Testing Lambda handler...")
    try:
        response = workout_processor.handler(test_event, mock_context)
        print("\n✅ Handler Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"\n❌ Error during execution: {str(e)}")
        raise

if __name__ == '__main__':
    test_handler()
