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
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse




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

@csrf_exempt
@login_required
def generate_legal_doc_wordfile(request):
    if request.method == "POST":
        try:
            import tempfile

            # Extract form data
            who_is_filing = request.POST.get("who_is_filing")
            husband_name = request.POST.get("husband_name")
            husband_address = request.POST.get("husband_address")
            wife_name = request.POST.get("wife_name")
            wife_address = request.POST.get("wife_address")
            reason = request.POST.get("reason")
            marriage_date = request.POST.get("marriage_date")
            marriage_dt = datetime.strptime(marriage_date, '%d-%m-%Y').date() if marriage_date else None

            # Get advocate info
            advocate = Advocate.objects.get(user=request.user)
            advocate_details = (
                f"From:\nAdvocate {advocate.name}\n"
                f"Enrollment Number: {advocate.enrollment_number}\n"
                f"Address: {advocate.address}\n"
            )

            prompt_query = (
                f"{who_is_filing} is filing for divorce. "
                f"Husband: {husband_name}, Address: {husband_address}. "
                f"Wife: {wife_name}, Address: {wife_address}. "
                f"Ground for divorce: {reason}. "
                f"Marriage Date: {marriage_dt}."
            )

            prompts = [
                {
                    "name": "divorce_notice_1.docx",
                    "style": (
                        "You are a legal assistant. Draft a formal and direct divorce notice.\n"
                        "Follow strict legal structure, tone should be professional and to the point."
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
                        "- End the letter with a 'Sincerely' section that includes the Advocate’s Name, Enrollment Number, and Address."
                    )
                },
                {
                    "name": "divorce_notice_2.docx",
                    "style": (
                        "You are a legal assistant. Draft a narrative, diplomatic divorce notice.\n"
                        "Tone should be respectful and empathetic, while maintaining legal clarity."
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
                        "- End the letter with a 'Sincerely' section that includes the Advocate’s Name, Enrollment Number, and Address."
                    )
                }
            ]

            # Create client record
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

            file_urls = []

            for index, prompt in enumerate(prompts):
                messages = [
                    {"role": "system", "content": prompt["style"]},
                    {"role": "user", "content": f"{advocate_details}\n{prompt_query}"}
                ]

                completion = groq_client.chat.completions.create(
                    model='llama3-70b-8192',
                    messages=messages
                )

                content = completion.choices[0].message.content

                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                    tmp_path = tmp.name

                generate_wordpad(tmp_path, content)

                # Save to FileField
                with open(tmp_path, "rb") as f:
                    if index == 0:
                        client.document_version_1.save(prompt["name"], File(f))
                        file_urls.append(client.document_version_1.url)
                    else:
                        client.document_version_2.save(prompt["name"], File(f))
                        file_urls.append(client.document_version_2.url)

                os.remove(tmp_path)

            return JsonResponse({
                "status": "success",
                "document1": file_urls[0],
                "document2": file_urls[1]
            })

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







