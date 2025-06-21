# Module: views.py

# Import
import os
import tempfile
import json
from datetime import datetime
import logging

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.files import File

from .models import Advocate, Client, NDA_Details, SaleDeed, NoObjectionCertificate
from .forms import SignupForm
from .generated_word import generate_professional_pdf
from .prompts import prompt_NDA, prompt_divorce, prompt_sale_deed, prompt_noc 

from groq import Groq
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environmental variables
load_dotenv()

# Initialize Groq client
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment variables.")
    groq_client = Groq(api_key=api_key)
    logger.info("Groq client initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing Groq client: {e}")
    groq_client = None

@csrf_exempt
@login_required
def generate_legal_doc_wordfile(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    logger.debug("Received POST data: %s", request.POST)

    try:
        document_type = request.POST.get("document_type")
        if not document_type:
            return JsonResponse({"error": "document_type is missing"}, status=400)
        if document_type not in ["divorce", "nda","sale_deed", "noc","doc_draft"]:
            return JsonResponse({"error": f"Invalid document_type: {document_type}"}, status=400)

        related_instance = None
        messages = []
        advocate = Advocate.objects.get(user=request.user)

        if document_type == "divorce":
            required_fields = ["who_is_filing", "husband_name", "husband_address", "wife_name", "wife_address", "reason", "marriage_date"]
            for field in required_fields:
                if not request.POST.get(field):
                    return JsonResponse({"error": f"Missing required field: {field}"}, status=400)

            who_is_filing = request.POST.get("who_is_filing")
            husband_name = request.POST.get("husband_name")
            husband_address = request.POST.get("husband_address")
            wife_name = request.POST.get("wife_name")
            wife_address = request.POST.get("wife_address")
            reason = request.POST.get("reason")
            marriage_date = request.POST.get("marriage_date")

            try:
                marriage_dt = datetime.strptime(marriage_date, '%d-%m-%Y').date()
            except ValueError:
                return JsonResponse({"error": "Invalid marriage_date format. Use DD-MM-YYYY"}, status=400)

            related_instance = Client.objects.create(
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

            advocate_details = (
                f"From:\nAdvocate {advocate.name}\n"
                f"Address: {advocate.address}\n"
                f"Phone: {advocate.phone}\n"
                f"Mail: {advocate.email}\n"
            )

            prompt_query = (
                f"{who_is_filing} is filing for divorce. "
                f"Husband: {husband_name}, Address: {husband_address}. "
                f"Wife: {wife_name}, Address: {wife_address}. "
                f"Ground for divorce: {reason}. "
                f"Marriage Date: {marriage_dt}."
            )

            messages = [
                {"role": "system", "content": prompt_divorce[0]["style"]},
                {"role": "user", "content": f"{advocate_details}\n{prompt_query}"}
            ]
            prompt_template = prompt_divorce

        elif document_type == "nda":
            required_fields = [
                "disclosing_party_name", "disclosing_party_representative", "disclosing_party_title",
                "disclosing_party_address", "receiving_party_name", "receiving_party_representative",
                "receiving_party_title", "receiving_party_address", "effective_date", "duration",
                "definition_confidential_information", "jurisdiction", "dispute_resolution_method"
            ]
            for field in required_fields:
                if not request.POST.get(field):
                    return JsonResponse({"error": f"Missing required field: {field}"}, status=400)

            def get_bool(field): return request.POST.get(field) == "on"
            def get_int(field): return int(request.POST.get(field, 0) or 0)

            nda_fields = {
                "advocate": advocate,
                "disclosing_party_name": request.POST.get("disclosing_party_name"),
                "disclosing_party_representative": request.POST.get("disclosing_party_representative"),
                "disclosing_party_title": request.POST.get("disclosing_party_title"),
                "disclosing_party_address": request.POST.get("disclosing_party_address"),
                "receiving_party_name": request.POST.get("receiving_party_name"),
                "receiving_party_representative": request.POST.get("receiving_party_representative"),
                "receiving_party_title": request.POST.get("receiving_party_title"),
                "receiving_party_address": request.POST.get("receiving_party_address"),
                "effective_date": datetime.strptime(request.POST.get("effective_date"), '%d-%m-%Y').date()
                                  if request.POST.get("effective_date") else None,
                "duration": get_int("duration"),
                "definition_confidential_information": request.POST.get("definition_confidential_information"),
                "non_competition": get_bool("non_competition"),
                "non_competition_duration": get_int("non_competition_duration") if get_bool("non_competition") else None,
                "non_circumvention": get_bool("non_circumvention"),
                "intellectual_property_rights": request.POST.get("intellectual_property_rights"),
                "data_destruction_policy": request.POST.get("data_destruction_policy"),
                "penalties": request.POST.get("penalties"),
                "jurisdiction": request.POST.get("jurisdiction"),
                "dispute_resolution_method": request.POST.get("dispute_resolution_method"),
                "created_at": datetime.strptime(request.POST.get("created_at"), "%d-%m-%Y")

            }

            related_instance = NDA_Details.objects.create(**nda_fields)

            prompt_query = (
                f"Non-Disclosure Agreement\n"
                f"Disclosing Party: {nda_fields['disclosing_party_name']}\n"
                f"Representative: {nda_fields['disclosing_party_representative']}\n"
                f"Title: {nda_fields['disclosing_party_title']}\n"
                f"Address: {nda_fields['disclosing_party_address']}\n\n"
                f"Receiving Party: {nda_fields['receiving_party_name']}\n"
                f"Representative: {nda_fields['receiving_party_representative']}\n"
                f"Title: {nda_fields['receiving_party_title']}\n"
                f"Address: {nda_fields['receiving_party_address']}\n\n"
                f"Effective Date: {nda_fields['effective_date']}\n"
                f"Duration: {nda_fields['duration']} year(s)\n"
                f"Definition of Confidential Information: {nda_fields['definition_confidential_information']}\n"
                f"Non-Competition: {nda_fields['non_competition']}\n"
                f"Non-Competition Duration: {nda_fields['non_competition_duration']}\n"
                f"Non-Circumvention: {nda_fields['non_circumvention']}\n"
                f"Intellectual Property Rights: {nda_fields['intellectual_property_rights']}\n"
                f"Data Destruction Policy: {nda_fields['data_destruction_policy']}\n"
                f"Penalties: {nda_fields['penalties']}\n"
                f"Jurisdiction: {nda_fields['jurisdiction']}\n"
                f"Dispute Resolution Method: {nda_fields['dispute_resolution_method']}\n"
            )

            messages = [
                {"role": "system", "content": prompt_NDA[0]["style"]},
                {"role": "user", "content": prompt_query}
            ]
            prompt_template = prompt_NDA

            # ==== Sale Deed ====
        elif document_type == "sale_deed":
            required_fields = [
                "client_name", "seller_name", "seller_address", "buyer_name",
                "buyer_address", "property_address", "property_type", "property_description",
                "sale_amount", "payment_mode", "date_of_agreement", "date_of_registration",
                "witness_1", "witness_2"
            ]
            for field in required_fields:
                if not request.POST.get(field):
                    return JsonResponse({"error": f"Missing required field: {field}"}, status=400)

            sale_deed_fields = {
                "advocate": advocate,
                "client_name": request.POST.get("client_name"),
                "seller_name": request.POST.get("seller_name"),
                "seller_address": request.POST.get("seller_address"),
                "buyer_name": request.POST.get("buyer_name"),
                "buyer_address": request.POST.get("buyer_address"),
                "property_address": request.POST.get("property_address"),
                "property_type": request.POST.get("property_type"),
                "property_description": request.POST.get("property_description"),
                "sale_amount": request.POST.get("sale_amount"),
                "payment_mode": request.POST.get("payment_mode"),
                "date_of_agreement": datetime.strptime(request.POST.get("date_of_agreement"), "%d-%m-%Y"),
                "date_of_registration": datetime.strptime(request.POST.get("date_of_registration"), "%d-%m-%Y"),
                "witness_1": request.POST.get("witness_1"),
                "witness_2": request.POST.get("witness_2"),
                
            }

            related_instance = SaleDeed.objects.create(**sale_deed_fields)

            prompt_query = (
                f"Prepare a Sale Deed Agreement.\n"
                f"Seller: {sale_deed_fields['seller_name']}, Address: {sale_deed_fields['seller_address']}.\n"
                f"Buyer: {sale_deed_fields['buyer_name']}, Address: {sale_deed_fields['buyer_address']}.\n"
                f"Property Address: {sale_deed_fields['property_address']} ({sale_deed_fields['property_type']})\n"
                f"Description: {sale_deed_fields['property_description']}\n"
                f"Sale Amount: ₹{sale_deed_fields['sale_amount']}, Payment Mode: {sale_deed_fields['payment_mode']}\n"
                f"Agreement Date: {sale_deed_fields['date_of_agreement']}, Registration Date: {sale_deed_fields['date_of_registration']}\n"
                f"Witnesses: {sale_deed_fields['witness_1']} & {sale_deed_fields['witness_2']}"
            )

            messages = [
                {"role": "system", "content": prompt_sale_deed[0]["style"]},
                {"role": "user", "content": prompt_query}
            ]
            prompt_template = prompt_sale_deed

        # ==== NOC Section ====
        elif document_type == "noc":
            required_fields = [
                "client_name", "noc_type", "party_issuing", "party_receiving",
                "purpose", "date_issued", "valid_until", "remarks"
            ]
            for field in required_fields:
                if not request.POST.get(field):
                    return JsonResponse({"error": f"Missing required field: {field}"}, status=400)

            noc_fields = {
                "advocate": advocate,
                "client_name": request.POST.get("client_name"),
                "noc_type": request.POST.get("noc_type"),
                "party_issuing": request.POST.get("party_issuing"),
                "party_receiving": request.POST.get("party_receiving"),
                "purpose": request.POST.get("purpose"),
                "date_issued": datetime.strptime(request.POST.get("date_issued"), "%d-%m-%Y"),
                "valid_until": datetime.strptime(request.POST.get("valid_until"), "%d-%m-%Y"),
                "remarks": request.POST.get("remarks"),
            
            }

            related_instance = NoObjectionCertificate.objects.create(**noc_fields)

            prompt_query = (
                f"Draft a No Objection Certificate (NOC).\n"
                f"NOC Type: {noc_fields['noc_type']}\n"
                f"Issuing Party: {noc_fields['party_issuing']}\n"
                f"Receiving Party: {noc_fields['party_receiving']}\n"
                f"Purpose: {noc_fields['purpose']}\n"
                f"Issue Date: {noc_fields['date_issued']}, Valid Until: {noc_fields['valid_until']}\n"
                f"Remarks: {noc_fields['remarks']}"
            )

            messages = [
                {"role": "system", "content": prompt_noc[0]["style"]},
                {"role": "user", "content": prompt_query}
            ]
            prompt_template = prompt_noc

          

        file_urls = []

        for index, prompt in enumerate(prompt_template):
            messages[0] = {"role": "system", "content": prompt["style"]}

            if not groq_client:
                return JsonResponse({"error": "Groq client not initialized"}, status=500)

            completion = groq_client.chat.completions.create(
                model='llama3-70b-8192',
                messages=messages
            )

            content = completion.choices[0].message.content

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp_path = tmp.name

            generate_professional_pdf(tmp_path, content)

            with open(tmp_path, "rb") as f:
                if index == 0:
                    related_instance.document_version_1.save(prompt["name"], File(f))
                    file_urls.append(related_instance.document_version_1.url)
                else:
                    related_instance.document_version_2.save(prompt["name"], File(f))
                    file_urls.append(related_instance.document_version_2.url)

            os.remove(tmp_path)

        return JsonResponse({
            "status": "success",
            "document1": file_urls[0],
            "document2": file_urls[1]
        })

    except Exception as e:
        logger.error("Error in generate_legal_doc_wordfile: %s", str(e), exc_info=True)
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)


def get_chat_history(request):
    history = request.session.get("chat_history", "")
    return JsonResponse({"history": history})


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

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


def advocate_login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect("advocate_dashboard")
        return render(request, "Advocate/login.html", {"error": "Invalid credentials"})
    return render(request, "Advocate/login.html")


@login_required
def advocate_dashboard_view(request):
    advocate = Advocate.objects.get(user=request.user)

    # Fetch related models
    clients = Client.objects.filter(advocate=advocate)
    nda_list = NDA_Details.objects.filter(advocate=advocate).order_by('-created_at')
    noc_list = NoObjectionCertificate.objects.filter(advocate=advocate).order_by('-created_at')
    sale_deed_list = SaleDeed.objects.filter(advocate=advocate).order_by('-created_at')

    return render(request, "Advocate/dashboard.html", {
        "advocate": advocate,
        "clients": clients,
        "nda_list": nda_list,
        "noc_list": noc_list,
        "sale_deed": sale_deed_list

    })


@csrf_exempt
@login_required
def save_client_data(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    try:
        data = json.loads(request.body)
        advocate = Advocate.objects.get(user=request.user)

        Client.objects.create(
            client_name=data.get("wife_name") if data.get("who_is_filing", "").lower() == "wife" else data.get("husband_name"),
            filer=data.get("who_is_filing"),
            husband_name=data.get("husband_name"),
            husband_address=data.get("husband_address"),
            wife_name=data.get("wife_name"),
            wife_address=data.get("wife_address"),
            marriage_Date=data.get("marriage_date"),
            reason=data.get("reason"),
            advocate=advocate
        )
        return JsonResponse({"status": "success"})

    except Exception as e:
        logger.error("Error in save_client_data: %s", str(e), exc_info=True)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    

