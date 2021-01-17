from xml.etree import ElementTree as ET

from django.http import JsonResponse
from django.shortcuts import render

from xml_converter.api import StreamParser


def upload_page(request):
    if request.method == 'POST':
        try:
            pull_parser = ET.XMLPullParser(["start", "end"])
            stream_parser = StreamParser()

            for chunk in request.FILES["file"].chunks():
                # Look for events in the read chunk
                pull_parser.feed(chunk)
                # Iterate through events found
                for event, element in pull_parser.read_events():
                    stream_parser.build(event, element)
            result = stream_parser.stack
            return JsonResponse(result)
        except ET.ParseError as pe:
            return JsonResponse({"error": "Malformed XML", "message": pe.msg, "status_code": "500"})
    return render(request, "upload_page.html")
