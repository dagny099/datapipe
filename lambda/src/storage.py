"""
storage.py

Abstraction layer for file storage operations.
Supports both local filesystem and S3 storage.
"""

import os
import shutil
from datetime import datetime
from abc import ABC, abstractmethod
import boto3
from botocore.exceptions import ClientError
import pandas as pd
from typing import Optional
import pymysql


class StorageError(Exception):
    """Base class for storage-related errors"""
    pass

class StorageHandler(ABC):
    """Abstract base class for storage operations"""
    
    @abstractmethod
    def version_existing_file(self, key: str) -> Optional[str]:
        """Version existing file with timestamp"""
        pass
    
    @abstractmethod
    def read_file(self, key: str) -> pd.DataFrame:
        """Read file content"""
        pass
    
    @abstractmethod
    def write_file(self, key: str, data: pd.DataFrame) -> None:
        """Write file content"""
        pass

class LocalStorageHandler(StorageHandler):
    """Handles local file storage operations"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(os.path.join(self.base_path, 'current'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'archive'), exist_ok=True)
    
    def _get_full_path(self, key: str) -> str:
        """Convert key to full file path"""
        return os.path.join(self.base_path, key)
    
    def version_existing_file(self, key: str) -> Optional[str]:
        """
        Version existing file by moving it to archive directory with timestamp.
        
        Args:
            key: Original file path relative to base_path
            
        Returns:
            Optional[str]: Path to archived file if original exists, None otherwise
        """
        current_path = self._get_full_path(os.path.join('current', key))
        if not os.path.exists(current_path):
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(key)
        archive_key = f'archive/{os.path.splitext(filename)[0]}_{timestamp}.csv'
        archive_path = self._get_full_path(archive_key)
        
        shutil.copy2(current_path, archive_path)
        return archive_key
    
    def read_file(self, key: str) -> pd.DataFrame:
        """
        Read CSV file from local storage.
        
        Args:
            key: File path relative to base_path
            
        Returns:
            DataFrame containing file contents
            
        Raises:
            StorageError: If file reading fails
        """
        try:
            full_path = self._get_full_path(key)
            return pd.read_csv(full_path)
        except Exception as e:
            raise StorageError(f"Failed to read file {key}: {str(e)}")
    
    def write_file(self, key: str, data: pd.DataFrame) -> None:
        """
        Write DataFrame to CSV file in local storage.
        
        Args:
            key: File path relative to base_path
            data: DataFrame to write
            
        Raises:
            StorageError: If file writing fails
        """
        try:
            full_path = self._get_full_path(key)
            data.to_csv(full_path, index=False)
        except Exception as e:
            raise StorageError(f"Failed to write file {key}: {str(e)}")


class RDSStorageHandler(StorageHandler):
    """Handles all data storage interactions, including RDS database connections."""

    def __init__(self, secret_name="my-rds-secret", region="us-west-2"):
        """Initialize storage handler and retrieve database credentials."""
        self.secret_name = secret_name
        self.region = region
        self.db_credentials = self.get_db_credentials()
        self.connection = self.get_db_connection()

    def get_db_credentials(self):
        """Retrieve RDS credentials from AWS Secrets Manager."""
        client = boto3.client("secretsmanager", region_name=self.region)
        try:
            response = client.get_secret_value(SecretId=self.secret_name)
            secret_dict = json.loads(response["SecretString"])
            return {
                "host": secret_dict["host"],
                "username": secret_dict["username"],
                "password": secret_dict["password"],
                "database": secret_dict["dbname"],
                "port": secret_dict.get("port", 3306)  # Default to MySQL
            }
        except Exception as e:
            print(f"❌ Error retrieving DB credentials: {e}")
            return None

    def get_db_connection(self):
        """Establish a database connection."""
        if not self.db_credentials:
            print("❌ No database credentials found.")
            return None

        try:
            conn = pymysql.connect(
                host=self.db_credentials["host"],
                user=self.db_credentials["username"],
                password=self.db_credentials["password"],
                database=self.db_credentials["database"],
                port=self.db_credentials["port"],
                connect_timeout=10
            )
            print("✅ Database connection successful.")
            return conn
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None

    def fetch_existing_workouts(self):
        """Retrieve existing workout IDs from the database."""
        if not self.connection:
            return set()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT workout_id FROM workouts;")
                existing_ids = {row[0] for row in cursor.fetchall()}  # Convert to a set
            return existing_ids
        except Exception as e:
            print(f"❌ Error fetching workouts: {e}")
            return set()

    def insert_new_workouts(self, new_workouts):
        """Insert new workout records into the database."""
        if not self.connection:
            return False

        try:
            with self.connection.cursor() as cursor:
                insert_query = """
                    INSERT INTO workouts (workout_id, user_id, activity_type, duration_minutes, calories_burned)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.executemany(insert_query, new_workouts)
            self.connection.commit()
            print("✅ Successfully inserted new workouts.")
            return True
        except Exception as e:
            print(f"❌ Error inserting workouts: {e}")
            return False



def get_storage_handler() -> StorageHandler:
    """
    Factory function to get appropriate storage handler based on environment.
    
    Returns:
        StorageHandler implementation
    """
    storage_type = os.getenv('STORAGE_TYPE', 'local').lower()
    
    storage_type = 'rds'

    if storage_type == 'local':
        base_path = os.getenv('LOCAL_STORAGE_PATH', 'local_testing')
        return LocalStorageHandler(base_path)
    elif storage_type == 'rds':
        return RDSStorageHandler()
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")
    #     bucket = os.getenv('S3_BUCKET')
    #     if not bucket:
    #         raise ValueError("S3_BUCKET environment variable must be set when using S3 storage")
    #     return S3StorageHandler(bucket)
