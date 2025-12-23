import os
import random
import time
from pprint import pprint

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage

try:
    from .api_logger import log_chat_completion
except ImportError:
    log_chat_completion = None


def prune_non_text_content(message: dict | ChatCompletionMessage) -> dict:
    if isinstance(message, ChatCompletionMessage):
        message = message.to_dict()
    message_pruned = {}
    for key, value in message.items():
        if key != "content":
            message_pruned[key] = value
            continue
        if value is None:
            message_pruned[key] = None
        elif isinstance(value, str):
            message_pruned[key] = value
        else:
            message_pruned[key] = []
            for v in value:
                if v["type"] == "text":
                    message_pruned[key].append(v)
                else:
                    message_pruned[key].append(
                        {
                            "type": v["type"],
                            v["type"]: "[pruned]",
                        }
                    )
    return message_pruned


def complete_chat_with_retries(
    messages: list[dict],
    model: str,
    api_key: str | None = os.getenv("OPENAI_API_KEY"),
    base_url: str | None = os.getenv("OPENAI_BASE_URL"),
    client_timeout: float = 600,

    max_attempts: int = 3,
    retry_initial_delay: float = 1,
    retry_exponential_base: float = 1.5,
    retry_jitter: bool = True,
    retry_max_delay: float = 5,
    retry_global_timeout: float = 60,
    print_error=True,

    **chat_completion_kwargs,
) -> ChatCompletion:

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=client_timeout)

    num_attempts = 1
    retry_delay = retry_initial_delay
    t_start = time.time()

    while True:
        if time.time() - t_start > retry_global_timeout:
            raise TimeoutError(f"Timeout when querying {model} at {base_url}")

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                **chat_completion_kwargs,
            )

        except Exception as e:
            if print_error:
                print(f"Error when querying {model} at {base_url} (attempt {num_attempts}/{max_attempts}): {repr(e)}")
                print("Relevant messages:")
                pprint([prune_non_text_content(message) for message in messages])

            # Increment attempts
            num_attempts += 1

            # Check if max attempts has been reached
            if num_attempts > max_attempts:
                raise RuntimeError(f"Max attempts reached when querying {model} at {base_url}") from e

            # Increment the delay
            next_delay = retry_delay * retry_exponential_base * (1 + retry_jitter * random.random())
            retry_delay = min(next_delay, retry_max_delay)

            # Sleep for the delay
            time.sleep(retry_delay)
            continue

        if log_chat_completion:
            messages_to_log = [prune_non_text_content(message) for message in messages]
            log_chat_completion(messages_to_log, response, api_key, base_url)

        return response


def query_api(
    query: str | list[dict],
    model: str,
    api_key: str | None = os.getenv("OPENAI_API_KEY"),
    base_url: str | None = os.getenv("OPENAI_BASE_URL"),
    image_url: str | None = None,        # image url for image input
    image_detail: str = "auto",          # "low", "auto", or "high" for gpt models
    context: list[dict] | None = None,   # context messages for multi-round conversation
    **kwargs,
) -> tuple[list[dict], ChatCompletion]:

    if isinstance(query, str):
        query = [{"type": "text", "text": query}]

    if image_url is not None:
        query.insert(0, {
            "type": "image_url",
            "image_url": {"url": image_url, "detail": image_detail},
        })

    messages = [*context] if context else []
    messages.append({"role": "user", "content": query})

    return messages, complete_chat_with_retries(
        messages=messages,
        model=model,
        api_key=api_key,
        base_url=base_url,
        **kwargs,
    )


if __name__ == "__main__":
    _, response = query_api(
        query="What is the capital of France?",
        model="gpt-5-nano",
        n=1,
    )
    print(response)