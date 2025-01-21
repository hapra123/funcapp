from flask import Flask, render_template, request, redirect, url_for
import pymssql
from azure.storage.blob import BlobServiceClient
import os
import time
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# Azure Blob Storage connection string and container
connection_string = os.getenv("DATABASE_CONNECTION_STRING")
container_name = "conversations"

# Function to establish a database connection 12
def get_db_connection():
    try:
        return pymssql.connect(
            server=os.getenv("SERVER"),
            database=os.getenv("DATABASE"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD")
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Function to upload a file to Azure Blob Storage
def upload_to_azure(file):
    try:
        if not file:
            return "No file selected. Please upload a valid file.", "N/A"

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        file_name = os.path.basename(file.filename)
        blob_client = container_client.get_blob_client(file_name)

        # Upload the file
        file.save(file_name)
        with open(file_name, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        # Simulate a countdown
        

        # Read file content to display
        with open(file_name, "r") as f:
            file_content = f.read()

        return f"File '{file_name}' uploaded successfully to the 'conversations' container!", file_content

    except Exception as e:
        return "Server is down. Please try again later.", str(e)

# Function to query the first 3 rows from the database
def query_first_3_rows():
    try:
        conn = get_db_connection()
        if not conn:
            return "Server is down. Database connection failed.", "N/A"
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 * FROM dbo.patient_records ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        result = "\n\n".join([f"Added Row: {str(row)}" for i, row in enumerate(rows)])
        return result
    except Exception as e:
        return "Server is down. Please try again later.", str(e)

# Function to query the latest row from the database
def query_latest_row():
    try:
        conn = get_db_connection()
        if not conn:
            return "Server is down. Database connection failed."
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 * FROM dbo.patient_records ORDER BY updated_at DESC")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            updated_at = row[-1]
            return f"Latest Updated Time: {updated_at}"
        else:
            return "No data found"
    except Exception as e:
        return "Server is down. Please try again later.", str(e)

# Function to get the total record count
def get_database_count():
    try:
        conn = get_db_connection()
        if not conn:
            return "Server is down. Database connection failed."
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dbo.patient_records")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return f"Total Records: {count}"
    except Exception as e:
        return "Server is down. Please try again later.", str(e)

# Flask app
flask_app = Flask(__name__) # Add a secret key for form handling

# Flask route to render the UI
@flask_app.route("/", methods=["GET", "POST"])
def index():
    upload_result = None
    upload_content = None
    latest_updated_time = None
    total_record_count = None
    first_3_result = None

    if request.method == "POST":
        if "upload" in request.form:
            file = request.files["file"]
            upload_result, upload_content = upload_to_azure(file)
        elif "query_latest_row" in request.form:
            latest_updated_time = query_latest_row()
        elif "get_count" in request.form:
            total_record_count = get_database_count()
        elif "first_3_rows" in request.form:
            first_3_result = query_first_3_rows()

    return render_template("index.html",
                           upload_result=upload_result,
                           upload_content=upload_content,
                           latest_updated_time=latest_updated_time,
                           total_record_count=total_record_count,
                           first_3_result=first_3_result)

if __name__ == "__main__":
    flask_app.run(debug=True)
