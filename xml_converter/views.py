from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime
from xml.etree import ElementTree as ET
import logging


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


class StreamParser:
    def __init__(self):
        """
        Constructor: Initializes the main stack needed to build the JSON
        """
        self.stack = []
        self.logger = logging.getLogger(__name__)

    def build(self, event, element):
        """
        Incrementally build a Dictionary from an XML file that is read chunk by chunk
        @param event: Event type [start, end]
        @param element: Contains XML Tag name and the text it holds
        """
        if event == "start":
            self.stack.append({"tag": element.tag, "value": element.text})
        else:
            leaf_node = self.stack.pop()
            if leaf_node["tag"] == element.tag:
                try:
                    parent_node = self.stack.pop()
                    if type(parent_node["value"]) is list:
                        parent_node["value"].append(leaf_node)
                    else:
                        parent_node["value"] = [leaf_node]
                    self.stack.append(parent_node)
                except IndexError:
                    self.logger.warning("Reached EOF of the XML file. File parsed")
                    self.stack = leaf_node
            else:
                self.logger.warning("Malformed XML")
