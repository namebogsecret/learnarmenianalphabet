"""
Service for interacting with OpenAI API.

Provides functions for generating translations and answers using OpenAI models.
"""

import logging
import os
import json
import httpx
import base64
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def get_image_content(image_path: str) -> str:
    """
    Encodes an image file to base64 for API requests.
    
    Args:
        image_path: Path to the image file.
        
    Returns:
        Base64 encoded image content.
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        raise OpenAIException(f"Error encoding image: {e}")

async def get_completion_with_image(
    prompt: str,
    image_path: str,
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """
    Get a completion from OpenAI API with image input.
    
    Args:
        prompt: The text prompt to send to the API.
        image_path: Path to the image file.
        model: The model to use (default: gpt-4o).
        temperature: Controls randomness (0-1).
        max_tokens: Maximum tokens in the response.
        
    Returns:
        The generated text response.
        
    Raises:
        OpenAIException: If the API call fails.
    """
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key is not set")
        raise OpenAIException("OpenAI API key is not set. Please check your .env file.")
    
    # Check if model supports image input
    if model not in ["gpt-4o"]:
        logger.warning(f"Model {model} may not support image input. Switching to gpt-4o.")
        model = "gpt-4o"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    try:
        # Encode image to base64
        image_content = await get_image_content(image_path)
        
        # Create message with image
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url", 
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_content}"
                    }
                }
            ]
        }]
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        async with httpx.AsyncClient(timeout=240.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"OpenAI API error: {response.status_code}, {error_detail}")
                raise OpenAIException(f"OpenAI API error: {response.status_code}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise OpenAIException(f"Request error: {e}")
    except Exception as e:
        logger.error(f"Error processing image or calling API: {e}")
        raise OpenAIException(f"Error: {e}")

async def handle_response(response):
    """
    Processes a successful response from the API.
    
    Args:
        response: Response from OpenAI API.
        
    Returns:
        Extracted useful part of the response or error message.
    """
    if 'error' in response:
        return await handle_error(response['error'])
    else:
        # Extract and return the useful part of the response
        try:
            return response['choices'][0]['message']['content']
        except (IndexError, KeyError):
            return "Error in API response structure."

async def handle_error(error_info):
    """
    Processes errors, returning an informative message.
    
    Args:
        error_info: Error information from API.
        
    Returns:
        Formatted error message.
    """
    error_message = error_info.get('message', 'Unknown error.')
    error_type = error_info.get('type', 'Unknown error type.')
    return f"Error: {error_message} Error type: {error_type}"

class OpenAIException(Exception):
    """Exception raised for OpenAI API errors."""
    pass

async def get_completion(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """
    Get a completion from OpenAI API.
    
    Args:
        prompt: The prompt to send to the API.
        model: The model to use (default: gpt-3.5-turbo).
        temperature: Controls randomness (0-1).
        max_tokens: Maximum tokens in the response.
        
    Returns:
        The generated text response.
        
    Raises:
        OpenAIException: If the API call fails.
    """
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key is not set")
        raise OpenAIException("OpenAI API key is not set. Please check your .env file.")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"OpenAI API error: {response.status_code}, {error_detail}")
                raise OpenAIException(f"OpenAI API error: {response.status_code}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise OpenAIException(f"Request error: {e}")

async def translate_with_openai(
    text: str,
    source_lang: str = "Russian",
    target_lang: str = "Armenian",
    model: str = "gpt-3.5-turbo"
) -> str:
    """
    Translate text using OpenAI.
    
    Args:
        text: Text to translate.
        source_lang: Source language (default: Russian).
        target_lang: Target language (default: Armenian).
        model: OpenAI model to use.
        
    Returns:
        Translated text.
        
    Raises:
        OpenAIException: If the translation fails.
    """
    prompt = f"Translate this from {source_lang} to {target_lang}. Return only the translation, no additional text: {text}"
    
    try:
        translation = await get_completion(prompt, model=model, temperature=0.3)
        
        # Remove any quotation marks that might be in the response
        translation = translation.strip('"\'')
        
        return translation
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise OpenAIException(f"Translation error: {e}")

async def get_armenian_translation(word: str) -> str:
    """
    Get Armenian translation for a specific word.
    
    Args:
        word: Word to translate.
        
    Returns:
        Armenian translation of the word.
    """
    try:
        prompt = f"Translate this Russian word to Armenian: '{word}'. Provide only the translation, no explanations or additional text."
        translation = await get_completion(prompt, temperature=0.3)
        
        # Clean up the response to get just the word
        translation = translation.strip()
        translation = translation.strip('"\'')
        translation = translation.split('\n')[0]  # Take only the first line
        
        return translation
    except Exception as e:
        logger.error(f"Error translating word '{word}': {e}")
        return word  # Return the original word if translation fails