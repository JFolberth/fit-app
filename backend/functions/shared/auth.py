"""
Utility for extracting authenticated user identity from Azure Static Web Apps
EasyAuth headers (X-MS-CLIENT-PRINCIPAL).

When SWA is configured with Azure AD authentication, it forwards user identity
as a Base64-encoded JSON payload in the X-MS-CLIENT-PRINCIPAL header.
"""

import base64
import json
import logging
from typing import Optional

import azure.functions as func

logger = logging.getLogger(__name__)


class UserIdentity:
    """Represents an authenticated user extracted from SWA EasyAuth headers."""

    def __init__(self, user_id: str, user_name: str, identity_provider: str):
        self.user_id = user_id
        self.user_name = user_name
        self.identity_provider = identity_provider

    def __repr__(self) -> str:
        return f"UserIdentity(user_id={self.user_id!r}, user_name={self.user_name!r})"


def get_user_identity(req: func.HttpRequest) -> Optional[UserIdentity]:
    """
    Extract authenticated user identity from the SWA EasyAuth header.

    Azure Static Web Apps forwards the X-MS-CLIENT-PRINCIPAL header which
    contains a Base64-encoded JSON object with:
    - identityProvider: "aad"
    - userId: unique user object ID
    - userDetails: user email or display name
    - userRoles: ["authenticated", "anonymous", ...]
    - claims: [{"typ": "...", "val": "..."}]

    Returns:
        UserIdentity if authenticated, None otherwise.
    """
    principal_header = req.headers.get("X-MS-CLIENT-PRINCIPAL")
    if not principal_header:
        logger.warning("No X-MS-CLIENT-PRINCIPAL header found")
        return None

    try:
        decoded = base64.b64decode(principal_header)
        principal = json.loads(decoded)
    except (ValueError, json.JSONDecodeError) as e:
        logger.error(f"Failed to decode X-MS-CLIENT-PRINCIPAL: {e}")
        return None

    user_id = principal.get("userId")
    user_name = principal.get("userDetails", "")
    identity_provider = principal.get("identityProvider", "unknown")

    if not user_id:
        logger.warning("X-MS-CLIENT-PRINCIPAL missing userId")
        return None

    return UserIdentity(
        user_id=user_id,
        user_name=user_name,
        identity_provider=identity_provider,
    )
