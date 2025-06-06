import openai
import os
import logging
from dotenv import load_dotenv
import tiktoken

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

def generate_chatgpt_response(prompt=None, conversation_history=None, model="gpt-4o", temperature=0.7, max_tokens=3000, system_prompt=None):
    """
    Generate a response from OpenAI's GPT model, handling both standalone prompts and conversation history.

    Args:
        prompt (str): A single prompt string for one-off requests.
        conversation_history (list): A list of dictionaries representing the conversation history.
        model (str): The OpenAI model to use (default: 'gpt-4').
        temperature (float): Controls randomness in output (default: 0.7).
        max_tokens (int): Max tokens to generate (default: 3000).
        system_prompt (str): Optional system-level prompt to set context.

    Returns:
        dict: The response from OpenAI's API or an error message.
    """
    try:
        if prompt and not isinstance(prompt, str):
            raise ValueError("Prompt must be a string if provided.")
        if conversation_history and not isinstance(conversation_history, list):
            raise ValueError("conversation_history must be a list of dictionaries.")

        messages = conversation_history if conversation_history else []
        if system_prompt and not any(msg.get('role') == 'system' for msg in messages):
            messages.insert(0, {"role": "system", "content": system_prompt})
        if prompt:
            messages.append({"role": "user", "content": prompt})

        messages = _truncate_messages(messages, max_tokens)

        logger.debug(f"Payload for OpenAI: {messages}")

        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        logger.info("Response successfully generated by OpenAI.")
        logger.debug(f"OpenAI response: {response}")
        return response

    except openai.OpenAIError as api_error:  
        error_message = f"OpenAI API error: {str(api_error)}"
        logger.error(error_message, exc_info=True)
        return {"status": "error", "message": error_message, "code": getattr(api_error, 'http_status', None)}
    except ValueError as ve:
        error_message = f"Validation error: {str(ve)}"
        logger.error(error_message)
        return {"status": "error", "message": error_message}
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {"status": "error", "message": error_message}


def _truncate_messages(messages, max_tokens):
    """
    Truncate messages to fit within the token limit.

    Args:
        messages (list): List of conversation messages.
        max_tokens (int): Maximum allowed tokens for the conversation.

    Returns:
        list: Truncated list of messages.
    """
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
        token_count = sum(len(encoding.encode(msg['content'])) for msg in messages)

        while token_count > max_tokens and len(messages) > 1:
            for i, msg in enumerate(messages):
                if msg["role"] != "system":  
                    removed_msg = messages.pop(i)
                    logger.warning(f"Removed message to reduce token count: {removed_msg}")
                    break
            token_count = sum(len(encoding.encode(msg['content'])) for msg in messages)

        return messages

    except Exception as e:
        logger.error(f"Error during token truncation: {e}", exc_info=True)
        raise RuntimeError("Error occurred while truncating messages to fit the token limit.")
