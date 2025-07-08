from langgraph.graph import RunnableConfig
from typing import Optional
from pydantic import BaseModel, ValidationError


class NormalizedConfig(BaseModel):
    user_email: str

def get_runtime_source(state, config) -> str:
    if config.configurable:
        return "studio_or_cli"
    elif "__copilot_context__" in state:
        return "copilotkit"
    return "unknown"

def extract_normalized_config(state: dict, config: RunnableConfig) -> NormalizedConfig:
    """
    Extracts the normalized configuration from the state and config.
    
    How to use: user_config = extract_normalized_config(state, config)
    
    """

    if config and config.configurable:
        try:
            return NormalizedConfig(**config.configurable)
        except ValidationError as e:
            raise ValueError(f"Invalid config from RunnableConfig: {e}")

    copilot_ctx = state.get("__copilot_context__", {}).get("configuration", {})
    if copilot_ctx:
        try:
            return NormalizedConfig(**copilot_ctx)
        except ValidationError as e:
            raise ValueError(f"Invalid config from Copilot context: {e}")

    raise ValueError("Missing user_email: No configuration provided.")

