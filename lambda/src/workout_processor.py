"""
workout_processor.py

Lambda function for processing workout data files with:
- Structured error handling
- File versioning
- Improved data validation
- Detailed logging

Supports both local testing and S3 deployment.
"""

import json
import time
import logging
from typing import Dict, Any, Tuple, List, Set
from datetime import datetime
import re
import os
import pandas as pd
import boto3
import json
# from storage import get_storage_handler, StorageError
from data_cleaning import clean_data
import pymysql
import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_db_credentials():
    """Retrieve RDS credentials from environment variables."""
    return {
        "host": os.getenv("DB_HOST"),
        "username": os.getenv("DB_USERNAME"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": int(os.getenv("DB_PORT", 3306)),  # Default to MySQL port 3306
    }

def get_db_connection():
    """Establish a database connection using environment variables."""
    credentials = get_db_credentials()

    if not credentials["host"]:
        logger.error("❌ No database credentials found in environment variables.")
        return None

    try:
        connection = pymysql.connect(
            host=credentials["host"],
            user=credentials["username"],
            password=credentials["password"],
            database=credentials["database"],
            port=credentials["port"],
            connect_timeout=10
        )
        logger.info("✅ Database connection successful.")
        return connection
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None

def fetch_existing_workouts():
    """Retrieve existing workout IDs from the RDS database."""
    connection = get_db_connection()
    if not connection:
        logger.error("❌ Could not establish database connection.")
        return set()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT workout_id FROM workout_summary;")
            existing_ids = {row[0] for row in cursor.fetchall()}  # Convert to a set
        logger.info(f"✅ Retrieved {len(existing_ids)} existing workouts.")
        return existing_ids
    except Exception as e:
        logger.error(f"❌ Error fetching workouts: {e}")
        return set()
    finally:
        connection.close()

def verify_s3_connectivity():
    """Verify S3 connectivity through VPC endpoint"""
    try:
        start_time = time.time()
        logger.info("Starting S3 connectivity test...")

        # Get VPC endpoint details
        ec2 = boto3.client('ec2')
        endpoints = ec2.describe_vpc_endpoints(
            Filters=[{
                'Name': 'service-name',
                'Values': ['com.amazonaws.us-west-2.s3']
            }]
        )['VpcEndpoints']

        if not endpoints:
            logger.error("No S3 VPC endpoints found!")
            return False

        # Log endpoint details
        for endpoint in endpoints:
            logger.info(f"Endpoint ID: {endpoint['VpcEndpointId']}")
            logger.info(f"State: {endpoint['State']}")
            logger.info(f"Route Table IDs: {endpoint['RouteTableIds']}")

        # Test S3 operation
        try:
            logger.info("Testing S3 list_buckets operation...")
            self.s3_client.list_buckets()
            logger.info(f"S3 connectivity test successful! Time: {time.time() - start_time:.2f}s")
            return True
        except Exception as e:
            logger.error(f"S3 operation failed: {str(e)}")
            return False

    except Exception as e:
        logger.error(f"Error verifying S3 connectivity: {str(e)}")
        return False
    

class WorkoutProcessingError(Exception):
    """Base class for workout processing errors"""
    pass

class DataValidationError(WorkoutProcessingError):
    """Raised when data validation fails"""
    pass

class WorkoutDataValidator:
    """Validates workout data structure and content"""
    
    REQUIRED_COLUMNS = {
        'Date Submitted',
        'Workout Date',
        'Activity Type',
        'Calories Burned (kcal)',
        'Distance (mi)',
        'Workout Time (seconds)',
        'Link'
    }
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> None:
        """Validate DataFrame structure and content"""
        # Check required columns
        missing_cols = WorkoutDataValidator.REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            raise DataValidationError(f"Missing required columns: {missing_cols}")
        
        # Check for empty DataFrame
        if df.empty:
            raise DataValidationError("DataFrame is empty")
        
        # Validate Link format (should contain workout ID)
        invalid_links = df[~df['Link'].str.contains(r'/workout/\d+', na=False)]
        if not invalid_links.empty:
            logger.warning(f"Found {len(invalid_links)} rows with invalid workout links")
            logger.debug(f"Invalid links: {invalid_links['Link'].tolist()}")

class WorkoutProcessor:
    """Processes workout data and identifies new records"""
    
    def __init__(self):
        """Initialize processor with storage handler"""
        self.s3_client = boto3.client('s3')
        self.rds_client = boto3.client('rds-data')
        self.bucket = os.getenv("S3_BUCKET")
        # Verify S3 connectivity on initialization
        if not verify_s3_connectivity():
            logger.warning("⚠️ S3 connectivity check failed - VPC endpoint may not be working")
        else:
            logger.info("✅ S3 connectivity verified through VPC endpoint")



    def extract_s3_data(self, event: Dict) -> List[Dict]:
        """Extract and process data from S3 event"""
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        logger.info(f"Attempting to read from bucket: {bucket}, key: {key}")

        logger.info(f"Lambda VPC Config: {os.environ.get('AWS_LAMBDA_VPC_CONFIG', 'Not in VPC')}")
        logger.info(f"Lambda Subnet IDs: {os.environ.get('AWS_LAMBDA_SUBNET_IDS', 'No subnets')}")            
        
        # Test S3 permissions explicitly
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
            logger.info("Successfully verified S3 object exists")
        except Exception as e:
            logger.error(f"S3 permission/access error: {str(e)}")
            raise
                
        try:
            logger.info("Getting object from S3...")
            # Add this logging before the get_object call
            response = self.s3_client.get_object(Bucket=bucket, Key=key)

            logger.info("Reading CSV data...")
            df = pd.read_csv(response['Body'])
            logger.info(f"Successfully read CSV with {len(df)} rows")
    
            logger.info("Validating DataFrame...")
            WorkoutDataValidator.validate_dataframe(df)
            logger.info("DataFrame validation successful")
            
            logger.info("Cleaning workout data...")  # Add logging for cleaning
            df = clean_data(df)

            # Extract workout IDs from Links
            logger.info("Extracting workout IDs...")
            df['workout_id'] = df['Link'].apply(self.extract_workout_id)
            
            records = df.to_dict('records')
            logger.info(f"Converted DataFrame to {len(records)} records")
            
            return records
        except Exception as e:
            logger.error(f"Error extracting S3 data: {e}")
            raise

    def extract_workout_id(self, url: str) -> str:
        """Extract workout ID from URL"""
        if pd.isna(url):
            return None
        match = re.search(r'/workout/(\d+)', url)
        return match.group(1) if match else None
        
    def insert_new_workouts(self, workouts: List[Dict]) -> bool:
        """Insert new workouts into RDS"""
        logger.info(f"Attempting to Insert {len(workouts)} new workouts into RDS")
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                for workout in workouts:
                    cursor.execute("""
                        INSERT INTO workout_summary (
                            workout_id, workout_date, activity_type,
                            kcal_burned, distance_mi, duration_sec
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        workout['workout_id'],
                        workout['Workout Date'],
                        workout['Activity Type'],
                        workout['Calories Burned (kcal)'],
                        workout['Distance (mi)'],
                        workout['Workout Time (seconds)']
                    ))
            conn.commit()
            logger.info(f"Successfully inserted {len(workouts)} new workouts")
            return True
        except Exception as e:
            logger.error(f"Error inserting workouts: {e}")
            return False
        finally:
            conn.close()


def send_sns_notification(topic_arn: str, new_records: int, file_key: str) -> None:
    """Send SNS notification about processing results"""
    try:
        import boto3
        sns_client = boto3.client('sns')
        message = {
            'file_processed': file_key,
            'new_records': new_records,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message, indent=2),
            Subject=f'Workout Processing Complete: {new_records} new records'
        )
    except Exception as e:
        logger.error(f"Failed to send SNS notification: {str(e)}")
        # Don't raise - notification failure shouldn't fail the whole process


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for processing workout files"""
    logger.info("START OF LAMBDA HANDLER LOGIC")
    logger.info(f"Received event: {json.dumps(event)}")
    logger.info(f"Context: {context}")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    logger.info(f"Processing file: s3://{bucket}/{key}")

    try:
        # Validate event
        if "Records" not in event or not isinstance(event["Records"], list) or len(event["Records"]) == 0:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Event does not contain valid 'Records'"
                })
            }

        # Initialize processor
        logger.info(f"Initializing WorkoutProcessor")
        processor = WorkoutProcessor()

        # Get existing workout IDs from RDS
        logger.info(f"Fetching existing workouts from RDS")
        existing_workouts = fetch_existing_workouts()
        logger.info(f"Existing workout IDs: {len(existing_workouts)}")

        # Extract and process data
        logger.info(f"Extracting data from S3")
        s3_data = processor.extract_s3_data(event)
        logger.info(f"Extracted {len(s3_data)} records from S3")

        # Identify new workouts
        new_workouts = [row for row in s3_data if row['workout_id'] not in existing_workouts]
        logger.info(f"New workouts: {len(new_workouts)}")           

        if not new_workouts:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "No new workouts found."
                })
            }

        # Insert new workouts
        if len(new_workouts) > 0:
            logger.info(f"Inserting new workouts into RDS")
            success = processor.insert_new_workouts(new_workouts)
            # Send notification if configured
            if success:
                send_sns_notification(os.getenv("SNS_TOPIC_ARN"), len(new_workouts), key)
            
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Successfully processed {len(new_workouts)} new workouts",
                "file_processed": event["Records"][0]["s3"]["object"]["key"],
                "new_workout_ids": [w['workout_id'] for w in new_workouts]
            }, ensure_ascii=False)  # Add ensure_ascii=False for proper encoding
        }
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": error_msg
            }, ensure_ascii=False)
        }

logger.info("END OF LAMBDA HANDLER LOGIC")