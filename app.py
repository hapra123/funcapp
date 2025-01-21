import gradio as gr
import pymssql
from azure.storage.blob import BlobServiceClient
import os as os
import time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Azure Blob Storage connection string
connection_string =os.getenv("DATABASE_CONNECTION_STRING")

container_name = "conversations"

conn = pymssql.connect(
    server=os.getenv("SERVER"),        # Correct usage of os.getenv
    database=os.getenv("DATABASE"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD")
)

# Function to simulate writing to database with a countdown timer
def upload_to_azure(file):
    try:
        # Connect to the Blob service
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get the container client
        container_client = blob_service_client.get_container_client(container_name)
        
        # Get the file name from file path
        file_name = os.path.basename(file.name)
        
        # Create a blob client
        blob_client = container_client.get_blob_client(file_name)
        
        # Upload the file
        with open(file.name, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)  # overwrite=True allows to overwrite existing blobs
        
        # Simulate writing to the database with a 10-second countdown
        for i in range(5, 0, -1):
            time.sleep(1)  # Wait for 1 second
            print(f"Writing to database in {i} seconds...")
        
        # Read the file content to display
        with open(file.name, "r") as f:
            file_content = f.read()
        
        return f"File '{file_name}' uploaded successfully to the 'conversations' container!", file_content

    except Exception as e:
        return "Server is down. Please try again later.", str(e)

# Function to query the first 5 rows from the database
def query_first_10_rows():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 3 * FROM dbo.patient_records ORDER BY updated_at DESC")  # Query for latest 5 rows based on updated_at
        rows = cursor.fetchall()
        cursor.close()
        
        # Format the result with row number and gap
        result = "\n\n".join([f"Row {i+1}: {str(row)}" for i, row in enumerate(rows)])
        return result

    except Exception as e:
        return "Server is down. Please try again later.", str(e)


# Function to query the latest row from the database with updated timestamp
def query_latest_row():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 * FROM dbo.patient_records ORDER BY updated_at DESC")  # Query for latest updated row
        row = cursor.fetchone()
        cursor.close()

        # Check if row is returned and format the timestamp
        if row:
            updated_at = row[-1]  # Assuming 'updated_at' is the last column in the result
            formatted_timestamp = updated_at # Format the datetime for display
            latest_row = str(row)
            return formatted_timestamp
        else:
            return "No data found", "N/A"

    except Exception as e:
        return "Server is down. Please try again later.", str(e)

# Function to get the count of items in the database
def get_database_count():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dbo.patient_records")  # Query to get the count of records
        count = cursor.fetchone()[0]  # Get the count from the result
        cursor.close()
        return f"Total Records: {count}"

    except Exception as e:
        return "Server is down. Please try again later.", str(e)

# Gradio interface
def create_gradio_interface():
    with gr.Blocks(css="footer {visibility: hidden;}") as demo:
        gr.Markdown("<center><h1>Medical Entity Extraction</h1></center>")
        with gr.Row():
            gr.Markdown("<center><h1>[Connected to Hardik's Azure Env]</h1></center>")
       
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Upload a Text File to Azure Blob Storage")
                upload_file_btn = gr.File(label="Choose Text File", type="filepath")  # Change to 'filepath'
                upload_result = gr.Textbox(label="Upload Result", interactive=False)
                upload_content = gr.Textbox(label="File Content", interactive=False, lines=10)
                upload_button = gr.Button("Upload to Azure Blob")
                upload_button.click(upload_to_azure, inputs=upload_file_btn, outputs=[upload_result, upload_content])
        
            with gr.Column():
                gr.Markdown("### Query Database")

                latest_row_btn = gr.Button("Show Latest Row from DB")
                latest_updated_time_result = gr.Textbox(label="Latest Updated Row", interactive=False)
                latest_row_btn.click(query_latest_row, outputs=[latest_updated_time_result])

                total_record_count = gr.Textbox(label="Total Records in DB", interactive=False)
                get_count_btn = gr.Button("Get Total Records Count")
                get_count_btn.click(get_database_count, outputs=total_record_count)

                first_10_btn = gr.Button("Show First 3 Rows from DB")
                first_10_result = gr.Textbox(label="First 3 Rows", interactive=False, lines=10)
                first_10_btn.click(query_first_10_rows, outputs=first_10_result)

                # Show total record count
                
    return demo

# Launch the Gradio app
app = create_gradio_interface()
app.launch()
