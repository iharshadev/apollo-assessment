from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime
from xml.etree import ElementTree as ET
import logging

def upload_page(request):
    if request.method == 'POST':
        try:
            # saved_filename = save_uploaded_file(request.FILES["file"])
            result = pullparse(request.FILES["file"])
            return JsonResponse(result)
        except ET.ParseError as pe:
            return JsonResponse({"Error": pe.msg})
    return render(request, "upload_page.html")

logger = logging.getLogger(__name__)

def save_uploaded_file(file):
    filename = file.name.replace(".xml", f"-{int(datetime.now().timestamp())}.xml")
    filename = f"static/uploaded-files/{filename}"
    with open(filename, "wb+") as target:
        for chunk in file.chunks():
            target.write(chunk)
    return filename


def pullparse(file):
    parser = ET.XMLPullParser(["start", "end"])
    result = []
    for chunk in file.chunks():
        # Look for events in the read chunk
        parser.feed(chunk)
        # Iterate through events found
        for event, element in parser.read_events():
            if event == "start" and element.text:
                logger.warning(f"<{element.tag}> : {element.text.strip()}")
                result.append((element.tag, element.text))
    return dict(result)
