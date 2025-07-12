from langgraph_sdk import Auth

auth = Auth()


def is_valid_key(api_key: str) -> bool:
    return api_key == "1234567890"


@auth.authenticate
async def authenticate(headers: dict) -> Auth.types.MinimalUserDict:
    api_key = headers.get("x-api-key")
    if not api_key or not is_valid_key(api_key):
        raise Auth.exceptions.HTTPException(status_code=401, detail="Invalid API key")

    return {
        "identity": "user-123",
        "is_authenticated": True,
        "permissions": ["read", "write"],
        "role": "admin",
        "org_id": "org-456",
    }
