#!/usr/bin/env python3
"""
Script to generate JWT tokens with organization_id for testing multi-tenant functionality.
"""

import jwt
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to find app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


def create_token(
    organization_id: str, user_id: str = "api_user", expires_minutes: int = 480
) -> str:
    """
    Create a JWT token with organization_id claim.

    Args:
        organization_id: The organization ID for multi-tenant isolation
        user_id: The user ID (default: api_user)
        expires_minutes: Token expiration time in minutes (default: 8 hours)

    Returns:
        JWT token string
    """
    payload = {
        "sub": user_id,
        "organization_id": organization_id,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def main():
    """Generate tokens for different organizations."""
    organizations = ["org1", "org2", "org3", "default"]

    print("Generated JWT tokens for multi-tenant testing:")
    print("=" * 60)

    for org_id in organizations:
        token = create_token(organization_id=org_id)
        print(f"\nOrganization: {org_id}")
        print(f"Token: {token}")
        print(f"Usage: Authorization: Bearer {token}")

    print("\n" + "=" * 60)
    print("Note: These tokens are for testing purposes only.")
    print("In production, use proper OAuth2 or signed JWT tokens.")


if __name__ == "__main__":
    main()
