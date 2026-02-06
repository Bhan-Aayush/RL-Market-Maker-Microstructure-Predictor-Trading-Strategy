"""Trading Interface (REST + WebSocket) package exports.

Expose the `IBMConsultingClient` so other modules can import it from
`src.interface` as needed during integration and testing.
"""

from .ibm_consulting import IBMConsultingClient

__all__ = ["IBMConsultingClient"]
