"""
test_enhanced_workout_processor.py

Tests for the workout processor Lambda function using shared fixtures.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

import pytest
import boto3
import os
import pandas as pd  # Added pandas import
from src.workout_processor import (
    WorkoutProcessor,
    handler,
    DataValidationError  # Added for error testing
)
from src.storage import StorageHandler
from io import BytesIO

@pytest.fixture
def sample_old_workout_data():
    """Create sample old workout data for testing."""
    return pd.DataFrame({
        'Date Submitted': ['2024-02-01'],
        'Workout Date': ['2024-02-01'],
        'Activity Type': ['Running'],
        'Calories Burned (kcal)': [400],
        'Distance (mi)': [5.0],
        'Workout Time (seconds)': [1800],
        'Link': ['http://www.mapmyfitness.com/workout/7434147697']
    })

@pytest.fixture
def mock_s3_client(mocker, sample_workout_data):
    """Create a mocked S3 client."""
    mock_client = mocker.patch('boto3.client')
    mock_s3 = mock_client.return_value
    mock_s3.head_object.return_value = {}
    
    csv_content = sample_workout_data.to_csv(index=False).encode('utf-8')
    def mock_get_object(**kwargs):
        return {'Body': BytesIO(csv_content)}
    mock_s3.get_object.side_effect = mock_get_object
    
    return mock_s3

@pytest.fixture
def mock_storage_handler(sample_workout_data, sample_old_workout_data):
    """Create a mock storage handler that returns proper workout data."""
    
    class TestStorageHandler(StorageHandler):

        def version_existing_file(self, key):
            return 'archive/old_file.csv'
        
        def read_file(self, key):
            if 'archive' in key:
                return sample_old_workout_data.copy()
            return sample_workout_data.copy()
            
        def write_file(self, key, data):
            pass
    
    return TestStorageHandler

def test_process_file_with_new_records(sample_workout_data, sample_old_workout_data, monkeypatch, mock_s3_client, mock_storage_handler):
    """Test processing file with new records."""
    
    monkeypatch.setenv('STORAGE_TYPE', 's3')
    monkeypatch.setenv('S3_BUCKET', 'test-bucket')
    
    from src import workout_processor

    TestStorageHandler = mock_storage_handler  # Capture the fixture value (the class)
    monkeypatch.setattr(workout_processor, 'get_storage_handler', lambda: TestStorageHandler())
    
    processor = WorkoutProcessor()
    new_count, new_ids = processor.process_file('test.csv')
    
    assert new_count == 1
    assert '7434147698' in new_ids

def test_handler_success(s3_event, aws_credentials, mock_context, monkeypatch, mock_s3_client, mock_storage_handler):
    """Test successful Lambda handler execution"""
    monkeypatch.setenv('STORAGE_TYPE', 's3')
    monkeypatch.setenv('S3_BUCKET', 'test-bucket')

    from src import workout_processor

    TestStorageHandler = mock_storage_handler  # Capture the fixture value (the class)
    monkeypatch.setattr(workout_processor, 'get_storage_handler', lambda: TestStorageHandler())
    
    response = handler(s3_event, mock_context)
    
    assert response['statusCode'] == 200
    assert 'Successfully processed' in response['body']

def test_handler_error(s3_event, aws_credentials, mock_context, monkeypatch, mock_s3_client):

    """Test Lambda handler error handling"""
    class ErrorStorageHandler(StorageHandler):
        def version_existing_file(self, key):
            raise DataValidationError("Test error")  # Changed to DataValidationError
            
        def read_file(self, key):
            raise DataValidationError("Test error")  # Changed to DataValidationError
            
        def write_file(self, key, data):
            raise DataValidationError("Test error")  # Changed to DataValidationError
    
    # Set up the environment but with an error-raising storage handler
    monkeypatch.setenv('STORAGE_TYPE', 's3')
    monkeypatch.setenv('S3_BUCKET', 'test-bucket')
    
    from src import workout_processor
    monkeypatch.setattr(workout_processor, 'get_storage_handler', lambda: ErrorStorageHandler())
    
    # This should now properly trigger error handling
    response = handler(s3_event, mock_context)
    
    assert response['statusCode'] == 400
    assert 'error' in response['body']

if __name__ == '__main__':
    pytest.main(['-v'])
