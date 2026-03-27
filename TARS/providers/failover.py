"""Failover provider that wraps multiple providers."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from loguru import logger

from TARS.providers.base import LLMProvider, LLMResponse


class FailoverProvider(LLMProvider):
    """
    A provider that wraps multiple providers and fails over to the next one
    if the current one returns an error.
    """

    def __init__(self, providers: list[tuple[LLMProvider, str, int]]):
        """
        Args:
            providers: List of (provider_instance, model_name, context_window_tokens) pairs.
        """
        self.providers = providers
        self._generation_settings = None
        super().__init__()

    def get_default_model(self) -> str:
        return self.providers[0][1] if self.providers else "unknown"

    @property
    def generation(self):
        return self._generation_settings

    @generation.setter
    def generation(self, value):
        self._generation_settings = value
        if hasattr(self, "providers") and self.providers:
            for p, _, _ in self.providers:
                p.generation = value

    def _prune_messages(
        self, messages: list[dict[str, Any]], context_limit: int, completion_limit: int, provider_name: str
    ) -> list[dict[str, Any]]:
        """
        Keep system message and as much recent history as fits within context window minus buffer.
        """
        from TARS.utils.helpers import estimate_message_tokens
        
        # Reserve buffer for competition tokens and safety headroom
        buffer = completion_limit + 1024 
        if context_limit <= buffer:
            return messages # Too small to prune effectively
            
        system_msg = messages[0] if messages and messages[0].get("role") == "system" else None
        last_msg = messages[-1] if messages else None
        
        if not last_msg:
            return messages

        fixed_tokens = estimate_message_tokens(last_msg)
        if system_msg:
            fixed_tokens += estimate_message_tokens(system_msg)
            
        budget = context_limit - buffer - fixed_tokens
        if budget < 0:
            # Last message + system is too big? Return them and hope for the best.
            logger.warning(
                "System+User query exceeds {} budget ({} > {})", 
                provider_name, fixed_tokens, context_limit - buffer
            )
            return [system_msg, last_msg] if system_msg else [last_msg]

        # Prune the middle (history)
        history = messages[1:-1] if system_msg else messages[:-1]
        pruned_history = []
        current_tokens = 0
        
        for msg in reversed(history):
            tokens = estimate_message_tokens(msg)
            if current_tokens + tokens <= budget:
                pruned_history.insert(0, msg)
                current_tokens += tokens
            else:
                break
                
        result = []
        if system_msg:
            result.append(system_msg)
        result.extend(pruned_history)
        result.append(last_msg)
        
        if len(result) < len(messages):
            logger.info(
                "Context pruned for {}: {} turns -> {} turns (budget {} prompt tokens reserved)", 
                provider_name, len(messages), len(result), budget
            )
        return result

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        reasoning_effort: str | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Call chat() on self.providers sequentially until one succeeds."""
        last_error = None
        primary_model = self.providers[0][1] if self.providers else None
        # If no model specified or it matches the primary, allow failover to others
        is_primary_request = (model is None or model == primary_model)

        for i, (provider, default_model, context_limit) in enumerate(self.providers):
            # Use current provider's model for failover, otherwise stick to original
            target_model = default_model if is_primary_request else model
            
            # Prune context for fallback providers if it exceeds their limit
            call_messages = messages
            if i > 0:
                call_messages = self._prune_messages(messages, context_limit, max_tokens, provider.__class__.__name__)

            response = await provider.chat(
                messages=call_messages,
                tools=tools,
                model=target_model,
                max_tokens=max_tokens,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
                tool_choice=tool_choice,
            )
            if response.finish_reason != "error":
                if i > 0:
                    logger.info("Failover successful: using provider {} ({}) with model {}", i, provider.__class__.__name__, target_model)
                return response
            
            logger.warning("Provider {} ({}) failed: {}. Trying next...", i, provider.__class__.__name__, response.content)
            last_error = response
            
            # Non-primary requests should not failover to a different provider
            if not is_primary_request:
                break

        return last_error or LLMResponse(content="No providers available", finish_reason="error")

    async def chat_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        reasoning_effort: str | None = None,
        tool_choice: str | dict[str, Any] | None = None,
        on_content_delta: Callable[[str], Awaitable[None]] | None = None,
    ) -> LLMResponse:
        """Call chat_stream() on self.providers sequentially until one succeeds."""
        last_error = None
        primary_model = self.providers[0][1] if self.providers else None
        is_primary_request = (model is None or model == primary_model)

        for i, (provider, default_model, context_limit) in enumerate(self.providers):
            target_model = default_model if is_primary_request else model
            
            call_messages = messages
            if i > 0:
                call_messages = self._prune_messages(messages, context_limit, max_tokens, provider.__class__.__name__)

            response = await provider.chat_stream(
                messages=call_messages,
                tools=tools,
                model=target_model,
                max_tokens=max_tokens,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
                tool_choice=tool_choice,
                on_content_delta=on_content_delta,
            )
            if response.finish_reason != "error":
                if i > 0:
                    logger.info("Failover successful (streaming): using provider {} ({}) with model {}", i, provider.__class__.__name__, target_model)
                return response
            
            logger.warning("Provider {} ({}) failed in streaming: {}. Trying next...", i, provider.__class__.__name__, response.content)
            last_error = response
            
            if not is_primary_request:
                break

        return last_error or LLMResponse(content="No providers available", finish_reason="error")

    async def chat_with_retry(self, **kwargs) -> LLMResponse:
        """Call chat_with_retry() on self.providers sequentially until one succeeds."""
        last_error = None
        requested_model = kwargs.get("model")
        completion_limit = kwargs.get("max_tokens", 4096)
        messages = kwargs.get("messages", [])
        primary_model = self.providers[0][1] if self.providers else None
        is_primary_request = (requested_model is None or requested_model == primary_model)
        
        for i, (provider, default_model, context_limit) in enumerate(self.providers):
            target_model = default_model if is_primary_request else requested_model
            
            # Set internal model and prune messages for this attempt
            call_kwargs = dict(kwargs)
            call_kwargs["model"] = target_model
            if i > 0:
                call_kwargs["messages"] = self._prune_messages(messages, context_limit, completion_limit, provider.__class__.__name__)
            
            response = await provider.chat_with_retry(**call_kwargs)
            if response.finish_reason != "error":
                if i > 0:
                    logger.info("Failover successful (retry): using provider {} ({}) with model {}", i, provider.__class__.__name__, target_model)
                return response
            
            logger.warning("Provider {} ({}) exhausting retries. Trying next provider...", i, provider.__class__.__name__)
            last_error = response
            
            if not is_primary_request:
                break

        return last_error

    async def chat_stream_with_retry(self, **kwargs) -> LLMResponse:
        """Call chat_stream_with_retry() on self.providers sequentially until one succeeds."""
        last_error = None
        requested_model = kwargs.get("model")
        completion_limit = kwargs.get("max_tokens", 4096)
        messages = kwargs.get("messages", [])
        primary_model = self.providers[0][1] if self.providers else None
        is_primary_request = (requested_model is None or requested_model == primary_model)
        
        for i, (provider, default_model, context_limit) in enumerate(self.providers):
            target_model = default_model if is_primary_request else requested_model
            
            call_kwargs = dict(kwargs)
            call_kwargs["model"] = target_model
            if i > 0:
                call_kwargs["messages"] = self._prune_messages(messages, context_limit, completion_limit, provider.__class__.__name__)
            
            response = await provider.chat_stream_with_retry(**call_kwargs)
            if response.finish_reason != "error":
                if i > 0:
                    logger.info("Failover successful (stream-retry): using provider {} ({}) with model {}", i, provider.__class__.__name__, target_model)
                return response
            
            logger.warning("Provider {} ({}) exhausting streaming retries. Trying next provider...", i, provider.__class__.__name__)
            last_error = response
            
            if not is_primary_request:
                break

        return last_error
