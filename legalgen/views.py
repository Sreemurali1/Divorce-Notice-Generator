# Module: views.py

# Import neccessary libraries
import os
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Advocate
from .models import Client
from .forms import SignupForm
from .generated_word import generate_wordpad
import json
from django.core.files import File
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime


# Load Enviromental Veriable
load_dotenv()

# Get Groq API Key from .env
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment variables.")
    
    groq_client = Groq(api_key=api_key)
    print("Groq client initialized successfully.")

except Exception as e:
    print(f"Error initializing Groq client: {e}")
    groq_client = None

# Generate Divorce Notice using Groq API
@csrf_exempt
@login_required
def generate_legal_doc_wordfile(request):
    if request.method == "POST":
        try:

            # Get raw data directly from POST form fields
            who_is_filing = request.POST.get("who_is_filing")
            husband_name = request.POST.get("husband_name")
            husband_address = request.POST.get("husband_address")
            wife_name = request.POST.get("wife_name")
            wife_address = request.POST.get("wife_address")
            reason = request.POST.get("reason")
            marriage_date = request.POST.get("marriage_date")  # e.g. "2025-06-16"

            # Parse marriage date to datetime.date
            marriage_dt = datetime.strptime(marriage_date, '%d-%m-%Y').date() if marriage_date else None


            # For session/debugging
            request.session["chat_history"] = str(request.POST)
            request.session["chat_history_raw"] = str(request.POST)

            advocate = Advocate.objects.get(user=request.user)

            advocate_details = (
                f"From:\n"
                f"Advocate {advocate.name}\n"
                f"Enrollment Number: {advocate.enrollment_number}\n"
                f"Address: {advocate.address}\n"
            )

            # Prepare query for LLM
            prompt_query = (
                f"This is a divorce notice. Please draft a formal legal letter based on the following details:\n"
                f"A divorce notice. Details: "
                f"{who_is_filing} is filing for divorce. "
                f"Husband: {husband_name}, Address: {husband_address}. "
                f"Wife: {wife_name}, Address: {wife_address}. "
                f"Ground for divorce: {reason}. "
                f"Marriage Date: {marriage_dt}."
            )

            messages = [
    {
        "role": "system",
        "content": (
            "You are a professional legal assistant. Draft a formal divorce notice based on the user's input.\n"
           "- Format the output as a formal legal letter.\n"
           "- Write the letter from the Advocate’s perspective, acting on behalf of their client (the Petitioner).\n"
           "- Begin with a 'From' section that includes the Advocate’s details (Full Name, Enrollment Number, and Address).\n"
           "- Include a 'To' section with the Respondent’s details (Full Name and Address).\n"
           "- Provide a clear and factual Subject stating the purpose of the letter (e.g.: 'Subject: Petition for Dissolution of Marriage').\n"
           "- Explain the grounds for divorce and state that the Petitioner requests dissolution of marriage due to these grounds.\n"
           "- Provide a deadline of 15 days for the recipient to respond in writing, failing which the Petitioner may pursue legal action in court.\n"
           "- Maintain a respectful, professional, clear, and assertive legal tone and structure.\n"
           "- Do not insert unnecessary blank lines or informal phrases; keep the letter clear, formal, and to the point.\n"
           "- End the letter with a 'Sincerely' section that includes the Advocate’s Name, Enrollment Number, and Address.\n"
        )
    },
    {
        "role": "user",
        "content": f"Create a divorce notice using the following details:\n{advocate_details}\n{prompt_query}"
    }
]


            # Get response from Groq
            completion = groq_client.chat.completions.create(
                model='llama3-70b-8192',
                messages=messages
            )

            document = completion.choices[0].message.content

            # Generate Word file
            file_name = "generated_report.docx"
            generate_wordpad(file_name, document)

            # Save to database
            advocate = Advocate.objects.get(user=request.user)

            client = Client.objects.create(
                client_name=wife_name if who_is_filing.lower() == "wife" else husband_name,
                filer=who_is_filing,
                husband_name=husband_name,
                husband_address=husband_address,
                wife_name=wife_name,
                wife_address=wife_address,
                marriage_Date=marriage_dt,
                reason=reason,
                advocate=advocate
            )

            with open(file_name, "rb") as f:
                client.document.save(file_name, File(f))

            return FileResponse(open(file_name, "rb"), as_attachment=True, filename=file_name)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return HttpResponse(f"Error: {str(e)}", status=500)

    return JsonResponse({"error": "POST request required"}, status=405)



# Load Session History
def get_chat_history(request):
    history = request.session.get("chat_history", "")
    return JsonResponse({"history": history})

# view User Information
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']

            user.set_password(password)
            user.save()

            # Now create Advocate with additional details
            Advocate.objects.create(
                user=user,
                name=f'{user.first_name} {user.last_name}',
                phone=form.cleaned_data['phone'],
                enrollment_number=form.cleaned_data['enrollment_number'], 
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address']
            )

            return redirect("advocate_login")

    else:
        form = SignupForm()
    return render(request, "Advocate/signup.html", {"form": form})


# Get username and password for user
def advocate_login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("advocate_dashboard")
        else:
            return render(request, "Advocate/login.html", {"error": "Invalid credentials"})

    return render(request, "Advocate/login.html")

# Get all objects for advocate and clients
@login_required
def advocate_dashboard_view(request):
    advocate = Advocate.objects.get(user=request.user)
    clients = Client.objects.filter(advocate=advocate)
    return render(request, "Advocate/dashboard.html", {
        "advocate": advocate,
        "clients": clients,
    })

# Save client data for Client History
@csrf_exempt
@login_required
def save_client_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            advocate = Advocate.objects.get(user=request.user)

            Client.objects.create(
                client_name = data.get("wife_name") if data.get("who_is_filing", "").lower() == "wife" else data.get("husband_name"),
                filer = data.get("who_is_filing"),
                husband_name = data.get("husband_name"),
                husband_address = data.get("husband_address"),
                wife_name = data.get("wife_name"),
                wife_address = data.get("wife_address"),
                marriage_Date = data.get("marriage_date"),
                reason = data.get("reason"),
                advocate = advocate
            )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"error": "POST request required"}, status=405)







