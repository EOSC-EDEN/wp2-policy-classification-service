# server/controllers/policy_detector.py

import requests
from flask import current_app

def detect_policy(body):
    """
    OpenAPI entrypoint
    body: dict with either url or text
    """

    url = body.get("url")
    text = body.get("text")

    if url and text:
        return {"error": "Provide only one of url or text"}, 400

    if url:
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            text = res.text
        except requests.RequestException as e:
            return {"error": f"Failed to fetch URL: {str(e)}"}, 400

    if not text:
        return {"error": "Either url or text must be provided"}, 400

    p = current_app.detector
    classification = p.classify(text)

    return classification