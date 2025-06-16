# Module: get_data.py

# Import Neccessary Libraries
from .models import Advocate
from django.http import JsonResponse

def post_advocate_details(request):
    if request.method == "POST":
        try:
            # If it's a form submission (POST form), use request.POST instead
            advocate = Advocate.objects.create(
                name=request.POST.get("name", ""),
                enrollment_number=request.POST.get("enrollment_number", ""),
                address=request.POST.get("address", ""),
                phone=request.POST.get("phone", ""),
                email=request.POST.get("email", "")
            )
            return JsonResponse({"message": "Advocate details saved successfully.", "id": advocate.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)
