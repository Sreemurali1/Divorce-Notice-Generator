# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from groq import Groq
from dotenv import load_dotenv
import os
import json
import logging
import pdfplumber
import tempfile
from django.core.files import File

from .models import LegalSession
from .generated_word import generate_professional_pdf

logger = logging.getLogger(__name__)
load_dotenv()

# Initialize Groq client
groq_client = None
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment variables.")
    groq_client = Groq(api_key=api_key)
    logger.info("Groq client initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing Groq client: {e}")


def get_pdf_text(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


@csrf_exempt
def upload_and_extract_questions(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    if not request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    responses = []

    for file in request.FILES.getlist("files"):
        try:
            text = get_pdf_text(file)
            
            prompt = f"""
            You are a legal assistant tasked with analyzing a legal document. Your goal is to identify all unique, client-specific fields required to complete or personalize this document for legal drafting.

            Your task:
            - Carefully read the document below.
            - Identify all fields that require user input (e.g., names, dates, addresses, amounts, relationships, signatures).
            - 
            - Clearly identify the **roles** and **entities** involved (e.g., buyer, seller, husband, wife, client, witness, landlord, tenant, etc.).
            - For each required field, generate a **clear, concise, and non-redundant** question that will collect that information from the user.

            Guidelines:
            - Do NOT repeat questions that ask for the same thing in different ways.
            - Phrase each question formally and clearly, as if asked by a legal assistant.
            - Do NOT use markdown, formatting symbols (like *, _, or backticks), or any visual styling.
            - Avoid general, open-ended questions. Only ask for specific, identifiable inputs.
            - Do not add explanations or metadata. Only return the list of questions.

            Output Format:
            - A plain-text numbered list of questions, one per line.

            Document:
            {text}
            """


            messages = [
                {"role": "system", "content": "You are a legal document assistant."},
                {"role": "user", "content": prompt}
            ]

            response = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages
            )

            raw = response.choices[0].message.content.strip()
            questions = [q.strip("- ").strip() for q in raw.split("\n") if q.strip()]
            current_question = questions[0] if questions else None

            session = LegalSession.objects.create(
                filename=file.name,
                original_text=text,
                questions=questions[1:],  # Save remaining questions
                current_question=current_question,
                answers={}
            )

            responses.append({
                "session_id": str(session.session_id),
                "current_question": current_question
            })

        except Exception as e:
            logger.error(f"Failed to process file {file.name}: {e}")
            responses.append({"error": f"Error processing {file.name}: {str(e)}"})

    return JsonResponse(responses, safe=False)


@csrf_exempt
def answer_question(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    session_id = request.POST.get("session_id")
    answer = request.POST.get("answer")

    if not session_id or not answer:
        return JsonResponse({"error": "session_id and answer are required"}, status=400)

    try:
        session = LegalSession.objects.get(session_id=session_id)
    except LegalSession.DoesNotExist:
        return JsonResponse({"error": "Invalid session ID"}, status=404)

    if session.status == "completed":
        return JsonResponse({"message": "Session already completed"}, status=400)

    # Save answer
    if session.current_question:
        session.answers[session.current_question] = answer

    # Get next question
    if session.questions:
        next_question = session.questions.pop(0)
        session.current_question = next_question
        session.save()
        return JsonResponse({
            "status": "next",
            "current_question": next_question
        })

    session.current_question = None
    session.status = "completed"
    session.save()
    return JsonResponse({
        "status": "completed",
        "message": "All questions answered. Ready to generate filled text.",
        "generate": True
    })


@csrf_exempt
def generate_filled_text(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    session_id = request.POST.get("session_id")
    if not session_id:
        return JsonResponse({"error": "session_id is required"}, status=400)

    try:
        session = LegalSession.objects.get(session_id=session_id)
    except LegalSession.DoesNotExist:
        return JsonResponse({"error": "Invalid session ID"}, status=404)

    if session.status != "completed":
        return JsonResponse({"error": "All questions must be answered before generating the document"}, status=400)

    prompt = f"""
    Fill the following legal document with the user-provided answers.
    Replace placeholders or missing client-specific fields with provided data.
    Do not include any explanation or commentary—only the filled document.

    --- Document ---
    {session.original_text}

    --- Answers ---
    {json.dumps(session.answers, indent=2)}
    """

    messages = [
        {"role": "system", "content": "You are a legal assistant."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages
        )
        final_text = response.choices[0].message.content.strip()
        session.filled_text = final_text
        session.save()

        file_urls = []

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name

        generate_professional_pdf(tmp_path, final_text)

        with open(tmp_path, "rb") as f:
            session.document.save(f"filled_{session.session_id}.pdf", File(f))
            file_urls.append(session.document.url)

        os.remove(tmp_path)

        return JsonResponse({
            "status": "success",
            "filled_text": final_text,
            "document_url": file_urls[0]
        })


    except Exception as e:
        return JsonResponse({"error": f"Failed to generate document: {str(e)}"}, status=500)
