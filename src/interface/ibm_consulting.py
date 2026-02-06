"""
Minimal IBM Consulting Advantage client wrapper.

This module provides a lightweight client class `IBMConsultingClient` that
wraps configuration and exposes `call_assistant` for strategies or services
to call Advantage assistants/plugins. The implementation here is minimal and
returns a mocked response when no real endpoint/credentials are provided.
"""
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class IBMConsultingClient:
    """Client wrapper for IBM Consulting Advantage (watsonx powered).

    Usage:
        client = IBMConsultingClient.from_config(config_dict)
        resp = client.call_assistant(plugin_id, prompt)
    """

    def __init__(self, api_endpoint: str, api_key: Optional[str], api_secret: Optional[str],
                 cline_plugin_id: Optional[str] = None, roo_plugin_id: Optional[str] = None,
                 enabled: bool = False):
        self.api_endpoint = api_endpoint
        self.api_key = api_key or os.getenv("IBM_ADVANTAGE_KEY")
        self.api_secret = api_secret or os.getenv("IBM_ADVANTAGE_SECRET")
        self.cline_plugin_id = cline_plugin_id
        self.roo_plugin_id = roo_plugin_id
        self.enabled = enabled

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]):
        ibm = cfg.get("ibm_consulting", {}) if cfg else {}
        return cls(
            api_endpoint=ibm.get("api_endpoint", ""),
            api_key=ibm.get("api_key", None),
            api_secret=ibm.get("api_secret", None),
            cline_plugin_id=ibm.get("cline_plugin_id"),
            roo_plugin_id=ibm.get("roo_plugin_id"),
            enabled=bool(ibm.get("enabled", False)),
        )

    def call_assistant(self, plugin_id: str, prompt: str, params: Optional[Dict] = None) -> Dict:
        """Call the specified assistant/plugin with `prompt`.

        This function currently does a lightweight check for credentials and
        returns a mocked response if the client is not enabled or credentials
        are missing. Replace the mocked section with real HTTP requests to
        your Advantage endpoint when ready.
        """
        params = params or {}

        if not self.enabled:
            logger.info("IBM Consulting Advantage disabled; returning mock response")
            return {
                "plugin_id": plugin_id,
                "input": prompt,
                "result": f"(mock) assistant response for plugin {plugin_id}",
            }

        if not (self.api_key and self.api_secret):
            logger.warning("IBM Advantage enabled but credentials missing; returning mock response")
            return {
                "plugin_id": plugin_id,
                "input": prompt,
                "result": f"(mock) assistant response (no creds) for plugin {plugin_id}",
            }

        # TODO: Implement real call to Advantage API. Example steps:
        # 1. Build request payload including plugin_id and prompt
        # 2. Sign/authenticate request using api_key/api_secret or OAuth
        # 3. POST to self.api_endpoint and parse response
        # For now, return a placeholder structure.
        logger.info("(placeholder) would call IBM Advantage endpoint %s with plugin %s", self.api_endpoint, plugin_id)
        return {
            "plugin_id": plugin_id,
            "input": prompt,
            "result": f"(placeholder) sent to {self.api_endpoint} for plugin {plugin_id}",
        }


__all__ = ["IBMConsultingClient"]
