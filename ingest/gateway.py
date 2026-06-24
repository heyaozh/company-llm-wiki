"""Company model gateway — OpenAI-compatible endpoint.

The firm exposes Gemini behind an internal OpenAI-compatible gateway
(base_url + API key) with corporate TLS interception. All model calls go
through this client. Configure via environment variables:

    GATEWAY_BASE_URL   e.g. https://company.com/api
    GATEWAY_API_KEY    your internal key (NEVER commit it)
    GATEWAY_CA_BUNDLE  (optional) path to the corporate root CA .pem — preferred.
                       If unset, TLS verification is disabled (quick unblock only).
"""
from __future__ import annotations

import os

import httpx
from openai import OpenAI


def chat_client() -> OpenAI:
    base_url = os.environ["GATEWAY_BASE_URL"]
    api_key = os.environ["GATEWAY_API_KEY"]
    ca = os.environ.get("GATEWAY_CA_BUNDLE")
    verify = ca if ca else False  # set GATEWAY_CA_BUNDLE for proper TLS; False = quick unblock
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        http_client=httpx.Client(verify=verify, timeout=120),
    )
