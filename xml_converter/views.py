from xml.etree import ElementTree as ET

from django.http import JsonResponse
from django.shortcuts import render


def upload_page(request):
    if request.method == 'POST':
        file = request.FILES["file"].read().decode("utf-8")
        result = traverse_recursive(ET.fromstring(file))
        return JsonResponse(result)
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
