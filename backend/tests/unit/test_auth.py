"""Unit tests for the auth module (SWA EasyAuth user identity extraction)."""
import base64
import json

import azure.functions as func
import pytest

from shared.auth import get_user_identity, UserIdentity


def _make_principal_header(user_id="test-user-123", user_details="testuser@example.com",
                           identity_provider="aad", user_roles=None):
    """Create a Base64-encoded X-MS-CLIENT-PRINCIPAL header value."""
    principal = {
        "identityProvider": identity_provider,
        "userId": user_id,
        "userDetails": user_details,
        "userRoles": user_roles or ["authenticated", "anonymous"],
    }
    return base64.b64encode(json.dumps(principal).encode()).decode()


def _make_request(headers=None):
    """Create a minimal HttpRequest with optional headers."""
    return func.HttpRequest(
        method="GET",
        url="/api/test",
        headers=headers or {},
        body=None,
    )


class TestGetUserIdentity:
    """Tests for get_user_identity function."""

    def test_valid_principal_returns_identity(self):
        """A valid X-MS-CLIENT-PRINCIPAL header returns a UserIdentity."""
        header = _make_principal_header(
            user_id="abc-123",
            user_details="user@example.com",
            identity_provider="aad",
        )
        req = _make_request(headers={"X-MS-CLIENT-PRINCIPAL": header})
        user = get_user_identity(req)

        assert user is not None
        assert user.user_id == "abc-123"
        assert user.user_name == "user@example.com"
        assert user.identity_provider == "aad"

    def test_missing_header_returns_none(self):
        """No X-MS-CLIENT-PRINCIPAL header returns None."""
        req = _make_request()
        user = get_user_identity(req)
        assert user is None

    def test_empty_header_returns_none(self):
        """Empty X-MS-CLIENT-PRINCIPAL header returns None."""
        req = _make_request(headers={"X-MS-CLIENT-PRINCIPAL": ""})
        user = get_user_identity(req)
        assert user is None

    def test_invalid_base64_returns_none(self):
        """Invalid base64 in header returns None."""
        req = _make_request(headers={"X-MS-CLIENT-PRINCIPAL": "not-valid-base64!!!"})
        user = get_user_identity(req)
        assert user is None

    def test_invalid_json_returns_none(self):
        """Valid base64 but invalid JSON returns None."""
        header = base64.b64encode(b"not json").decode()
        req = _make_request(headers={"X-MS-CLIENT-PRINCIPAL": header})
        user = get_user_identity(req)
        assert user is None

    def test_missing_user_id_returns_none(self):
        """Principal with no userId returns None."""
        principal = {
            "identityProvider": "aad",
            "userDetails": "user@example.com",
            "userRoles": ["authenticated"],
        }
        header = base64.b64encode(json.dumps(principal).encode()).decode()
        req = _make_request(headers={"X-MS-CLIENT-PRINCIPAL": header})
        user = get_user_identity(req)
        assert user is None

    def test_empty_user_id_returns_none(self):
        """Principal with empty userId returns None."""
        header = _make_principal_header(user_id="")
        req = _make_request(headers={"X-MS-CLIENT-PRINCIPAL": header})
        user = get_user_identity(req)
        assert user is None

    def test_missing_user_details_defaults_to_empty(self):
        """Principal without userDetails defaults to empty string."""
        principal = {
            "identityProvider": "aad",
            "userId": "user-456",
            "userRoles": ["authenticated"],
        }
        header = base64.b64encode(json.dumps(principal).encode()).decode()
        req = _make_request(headers={"X-MS-CLIENT-PRINCIPAL": header})
        user = get_user_identity(req)

        assert user is not None
        assert user.user_id == "user-456"
        assert user.user_name == ""

    def test_user_identity_repr(self):
        """UserIdentity has a useful repr."""
        identity = UserIdentity(user_id="abc", user_name="user@test.com", identity_provider="aad")
        assert "abc" in repr(identity)
        assert "user@test.com" in repr(identity)
