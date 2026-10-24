"""trust_services — W7 trust and advertising services (INT-035, INT-037)."""

from .int035_trust import (
    TradeLicenseClient,
    TradeLicenseVerificationRequest,
    TradeLicenseVerificationResult,
)
from .int037_ads import (
    AdCampaign,
    AdDeliveryEngine,
    AdPlacement,
)

__all__ = [
    "AdCampaign",
    "AdDeliveryEngine",
    "AdPlacement",
    "TradeLicenseClient",
    "TradeLicenseVerificationRequest",
    "TradeLicenseVerificationResult",
]
