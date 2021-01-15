from django.http import JsonResponse
from django.shortcuts import render


def upload_page(request):
    if request.method == 'POST':
        file = request.FILES["file"].read().decode("utf-8")
        return JsonResponse({"content": file})
    return render(request, "upload_page.html")
