from xml.etree import ElementTree as ET

from django.http import JsonResponse
from django.shortcuts import render


def upload_page(request):
    if request.method == 'POST':
        file = request.FILES["file"].read().decode("utf-8")
        try:
            xml_content = ET.fromstring(file)
            result = traverse_recursive(xml_content)
            return JsonResponse(result)
        except ET.ParseError as pe:
            return JsonResponse({
                "Error": pe.msg,
                "Type": "Malformed XML file"
            })

    return render(request, "upload_page.html")


def traverse_recursive(node):
    if node.tag.lower() == "root" and len(node) == 0:
        return {node.tag: ""}
    if len(node) == 0:
        return {node.tag: node.text}
    children = []
    for child in node:
        children.append(traverse_recursive(child))

    if node.tag.lower() == "root":
        return {f"{node[0].tag}es": children}
    else:
        return {node.tag: children}
