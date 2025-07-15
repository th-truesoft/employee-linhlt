#!/usr/bin/env python3
"""JWT token generation script for Employee Directory API demo"""

import jwt
import json
from datetime import datetime, timedelta

# Secret key from config (must match app/core/config.py)
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"


def create_jwt_token(
    organization_id: str, user_id: str = "demo-user", expires_in_hours: int = 24
):
    """Create JWT token with organization_id claim"""

    # JWT payload with organization context
    now = datetime.utcnow()
    payload = {
        "sub": user_id,  # subject (user id)
        "organization_id": organization_id,
        "iat": int(now.timestamp()),  # issued at (Unix timestamp)
        "exp": int(
            (now + timedelta(hours=expires_in_hours)).timestamp()
        ),  # expires (Unix timestamp)
        "token_type": "access",
    }

    # Generate JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def main():
    print("🔐 JWT Token Generator for Employee Directory API")
    print("=" * 50)

    # Create tokens for different organizations
    organizations = [
        {"id": "default", "name": "Default Organization"},
        {"id": "org1", "name": "Company A"},
        {"id": "org2", "name": "Company B"},
        {"id": "enterprise", "name": "Enterprise Corp"},
    ]

    tokens = {}

    for org in organizations:
        org_id = org["id"]
        org_name = org["name"]

        token = create_jwt_token(organization_id=org_id)
        tokens[org_id] = token

        print(f"\n📋 {org_name} (org_id: {org_id})")
        print(f"JWT Token: {token}")
        print(f"Authorization Header: Bearer {token}")

    # Save tokens to JSON file
    with open("config/jwt_tokens.json", "w") as f:
        json.dump(tokens, f, indent=2)

    print(f"\n✅ Tokens saved to config/jwt_tokens.json")

    # Verify token example
    print(f"\n🔍 Test decode token for 'default' organization:")
    try:
        decoded = jwt.decode(tokens["default"], SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {json.dumps(decoded, indent=2, default=str)}")
    except Exception as e:
        print(f"❌ Error decoding: {e}")


if __name__ == "__main__":
    main()
