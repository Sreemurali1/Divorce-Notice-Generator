import os
import django
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

# --- Django setup ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # Replace with your project name
django.setup()

client = Client()

# --- Upload and Extract Questions ---
print("\n== Uploading PDF and extracting questions ==")
with open(r"C:\Users\Sree\OneDrive\Documents\docs-generated_919299d370c47bddc093ac4a641966ed.pdf", "rb") as f:
    file_data = SimpleUploadedFile("sample.pdf", f.read(), content_type="application/pdf")
    response = client.post("/upload/", {"files": [file_data]})
    print("Response:", response.status_code, response.json())

    if response.status_code == 200 and isinstance(response.json(), list):
        session_id = response.json()[0]["session_id"]
        current_question = response.json()[0]["current_question"]
    else:
        print("Upload failed.")
        exit()

# --- Answer a Question ---
print("\n== Answering a question ==")
response = client.post("/answer/", {
    "session_id": session_id,
    "answer": "John Doe"
})
print("Response:", response.status_code, response.json())

# --- Repeat answering until completed if needed
# (Repeat /answer/ call manually if your flow expects multiple questions)

# --- Generate Filled Text ---
print("\n== Generating final filled text ==")
response = client.post("/generate_filled_text/", {
    "session_id": session_id
})
print("Response:", response.status_code, response.json())
