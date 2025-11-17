# ---------------- Basic Imports ----------------
import os, sys, json          # os/sys for system operations, json for converting data
import pandas as pd           # pandas → data processing & CSV reading
import numpy as np            # numpy → numerical computations (not used yet but good to keep)
import pymongo                # pymongo → MongoDB client for database operations
import openpyxl


# ---------------- Internal Imports ----------------
from autocare_utils.exception import AutoCareException  # custom exception                     # custom logger


# ---------------- Advanced Imports ----------------
import certifi                # certifi ensures SSL certificates are valid for secure MongoDB connection
ca = certifi.where()          # 'ca' stores the path to certificate bundle


# ---------------- Load Environment Variables ----------------
from dotenv import load_dotenv   # dotenv allows loading secrets (like MongoDB URL) from .env file
load_dotenv()

# MongoDB URL from environment (never hardcode secrets)
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)  # Debugging purpose (REMOVE in production for security)


# ---------------- Main Class for Data Extraction ----------------
class DataExtract():
    """
    Class for:
    1. Reading CSV data
    2. Converting CSV → JSON records
    3. Inserting records into MongoDB
    """

    # Constructor
    def __init__(self):
        try:
            # Nothing is initialized here yet, but kept for extension (future configs, validation, etc.)
            pass
        except Exception as e:
            raise AutoCareException(e, sys)  # Raise custom exception with traceback


    # CSV → JSON Converter
    def excel_to_json_converter(self, file_path):
        """
        Reads a CSV file and converts it into a list of JSON-like records (dicts).
        Useful for direct MongoDB ingestion.
        """
        try:
            # Read CSV into pandas DataFrame
            data = pd.read_excel(file_path)

            # Reset index for clean, continuous row numbers
            data.reset_index(drop=True, inplace=True)

            # Convert DataFrame → JSON string → Python dict → list of dicts
            # .T → transpose for easier conversion, .values() → extract dict values
            records = list(json.loads(data.T.to_json()).values())

            return records

        except Exception as e:
            raise AutoCareException(e, sys)


    # Insert Data into MongoDB
    def insert_data_mongodb(self, records, database, collection):
        """
        Inserts JSON records into MongoDB collection.
        :param records: list of dicts (data)
        :param database: target DB name
        :param collection: target collection name
        """
        try:
            self.database = database
            self.collection = collection
            self.records = records

            # Connect to MongoDB using URL from .env
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)

            # Select database & collection
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]

            # Insert all records
            self.collection.insert_many(self.records)

            # Return count of inserted records
            return len(self.records)

        except Exception as e:
            raise AutoCareException(e, sys)



# ---------------- Main Script Execution ----------------
if __name__ == "__main__":
    # Input CSV file path
    FILE_PATH = "machine_learning/training/heart/data/heart_final.xlsx"
    # Target MongoDB database
    DATABASE = "Heart"
    # Target MongoDB collection
    COLLECTION = "heart_raw"

    # Create object of Data Extractor
    network_obj = DataExtract()

    # Convert CSV → JSON records
    records = network_obj.excel_to_json_converter(file_path=FILE_PATH)

    # Insert records into MongoDB
    no_of_records = network_obj.insert_data_mongodb(
        records=records,
        database=DATABASE,
        collection=COLLECTION
    )

    # Print inserted records count
    print(no_of_records)
