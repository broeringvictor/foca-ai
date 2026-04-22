from langchain_anthropic import ChatAnthropic

from app.infrastructure.config.settings import Settings, get_settings


def get_llm_model(settings: Settings | None = None) -> ChatAnthropic:
    """Build and return the Anthropic model used by infrastructure services."""
    current_settings = settings or get_settings()
    return ChatAnthropic(
        model_name="claude-sonnet-4-6",
        stop=None,
        api_key=current_settings.ANTHROPIC_API_KEY,
        temperature=current_settings.llm.temperature,
        timeout=current_settings.llm.timeout,
        max_tokens_to_sample=current_settings.llm.max_tokens,
        max_retries=current_settings.llm.max_retries,
    )
