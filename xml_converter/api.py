from xml.etree import ElementTree as ET

from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class ConverterViewSet(ViewSet):
    # Note this is not a restful API
    # We still use DRF to assess how well you know the framework
    parser_classes = [MultiPartParser]

    @action(methods=["POST"], detail=False, url_path="convert")
    def convert(self, request, **kwargs):
        file = request.FILES["file"].read().decode("utf-8")
        return Response(self.traverse_recursive(ET.fromstring(file)), content_type="application/json")

    def traverse_recursive(self, node):
        if node.tag.lower() == "root" and len(node) == 0:
            return {node.tag: ""}
        if len(node) == 0:
            return {node.tag: node.text}
        children = []
        for child in node:
            children.append(self.traverse_recursive(child))

        if node.tag.lower() == "root":
            return {f"{node[0].tag}es": children}
        else:
            return {node.tag: children}
