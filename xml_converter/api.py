from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
import logging
from xml.etree import ElementTree as et


class ConverterViewSet(ViewSet):
    # Note this is not a restful API
    # We still use DRF to assess how well you know the framework
    parser_classes = [MultiPartParser]

    @action(methods=["POST"], detail=False, url_path="convert")
    def convert(self, request, **kwargs):
        file = request.FILES["file"]
        pull_parser = et.XMLPullParser(["start", "end"])
        stream_parser = StreamParser()

        for chunk in file.chunks():
            # Look for events in the read chunk
            pull_parser.feed(chunk)
            # Iterate through events found
            for event, element in pull_parser.read_events():
                stream_parser.build(event, element)
        result = stream_parser.stack
        return Response(result, content_type="application/json")


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
            self.stack.append({element.tag: element.text})
        else:
            leaf_node = self.stack.pop()
            leaf_node_tag, leaf_node_value = list(leaf_node.items()).pop()
            if leaf_node_tag == element.tag:
                try:
                    parent_node = self.stack.pop()
                    parent_node_tag, parent_node_value = list(parent_node.items()).pop()
                    if type(parent_node_value) is list:
                        parent_node_value.append(leaf_node)
                    else:
                        parent_node_value = [leaf_node]
                    self.stack.append({parent_node_tag: parent_node_value})
                except IndexError:
                    self.logger.warning("Reached EOF of the XML file. File parsed")
                    self.stack = leaf_node
            else:
                self.logger.warning("Malformed XML")
