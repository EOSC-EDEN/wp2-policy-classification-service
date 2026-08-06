# server/controllers/policy_detector.py

import requests
from flask import current_app
from io import BytesIO
from pdfminer.high_level import extract_text
from is_antibot import is_antibot

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
            content_type = res.headers.get("Content-Type")
            antibot_result = is_antibot(
                headers=res.headers,
                body=res.text,
                status_code=res.status_code,
            )
            if antibot_result.detected:
                return {"error": f"Antibot software detected, could not access content : {str(content_type)}"}, 400
            if 'html' in content_type:
                text = res.text
            elif 'pdf' in content_type:
                pdf_bytes = res.content
                text = extract_text(BytesIO(pdf_bytes))
            else:
                return {"error": f"Unsupported content type: {str(content_type)}"}, 400

        except requests.RequestException as e:
            return {"error": f"Failed to fetch URL: {str(e)}"}, 400

    if not text:
        return {"error": "Either url or text must be provided"}, 400

    p = current_app.detector
    classification = p.classify(text)
    result = {"input":url or str(text[:100])+"...","result": classification}

    return result