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
    pull_parser = ET.XMLPullParser(["start", "end"])
    stream_parser = StreamParser()

    for chunk in file.chunks():
        # Look for events in the read chunk
        pull_parser.feed(chunk)
        # Iterate through events found
        for event, element in pull_parser.read_events():
            stream_parser.build(event, element)
    result = stream_parser.stack
    return result


class StreamParser():
    def __init__(self):
        self.stack = []

    def build(self, event, element):
        if event == "start":
            self.stack.append({"tag": element.tag, "value": element.text.strip()})
        else:
            top_item = self.stack.pop()
            if top_item["tag"] == element.tag:
                try:
                    previous_item = self.stack.pop()
                    if type(previous_item["value"]) is list:
                        previous_item["value"].append(top_item)
                    else:
                        previous_item["value"] = [top_item]
                    self.stack.append(previous_item)
                except IndexError:
                    logger.warning("Reached EOF of the XML file. File parsed")
                    self.stack = top_item
            else:
                logger.warning("Malformed XML")
