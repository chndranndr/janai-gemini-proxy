"""
Main FastAPI proxy application for Google AI Studio with comprehensive logging
"""

import json
import time
import os
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

from config.settings import config
from config.constants import DEFAULT_MODEL
from ai.client import initialize_google_ai_client, get_google_ai_client
from tunnel.manager import tunnel_manager
from content.lorebook import lorebook_manager
from content.text_processing import (
    clean_response_text, ensure_markdown_formatting,
    check_forbidden_words, replace_forbidden_words,
    format_for_janitor_response, format_for_streaming_chunk
)
from content.jailbreak import get_jailbreak_text, get_medieval_text, get_thinking_message, get_ooc_template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('proxy.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize lorebook
    lorebook_manager.load_lorebook()

    return app

app = create_app()

from dotenv import load_dotenv

load_dotenv()
# Initialize Google AI client with environment variable
api_key = os.getenv("GOOGLE_AI_API_KEY", "")
if api_key:
    try:
        initialize_google_ai_client(api_key)
        logger.info("Google AI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Google AI client: {e}")
else:
    logger.error("GOOGLE_AI_API_KEY not found in environment variables")

@app.post('/v1/chat/completions')
async def chat_completions(request: Request):
    """Handle chat completion requests with detailed logging"""
    logger.info("=" * 80)
    logger.info("Received chat completion request")

    try:
        # Log request details
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request headers: {dict(request.headers)}")

        # Parse request data
        request_data = await request.json()
        if not request_data:
            logger.error("Invalid JSON in request")
            return JSONResponse(content={"error": {"message": "Invalid JSON"}}, status_code=400)

        logger.info(f"Request data: {json.dumps(request_data, indent=2)}")

        messages = request_data.get("messages", [])
        model = request_data.get("model", config.get("model", DEFAULT_MODEL))
        temperature = request_data.get("temperature")
        stream = request_data.get("stream", False)

        logger.info(f"Model: {model}")
        logger.info(f"Temperature: {temperature}")
        logger.info(f"Stream: {stream}")
        logger.info(f"Messages count: {len(messages)}")

        if not messages:
            logger.error("No messages provided in request")
            return JSONResponse(content={"error": {"message": "Messages are required"}}, status_code=400)

        # Process messages
        logger.info("Processing messages...")
        processed_messages = process_messages(messages)
        logger.info(f"Processed messages: {json.dumps(processed_messages, indent=2)}")

        # Get Google AI client
        try:
            client = get_google_ai_client()
            logger.info("Google AI client retrieved successfully")
        except Exception as e:
            logger.error(f"Failed to get Google AI client: {e}")
            return JSONResponse(content={"error": {"message": f"Google AI client error: {str(e)}"}}, status_code=500)

        # Generate response
        logger.info("Generating response...")
        if stream:
            logger.info("Handling streaming response")
            return await handle_streaming_response(client, model, processed_messages, temperature)
        else:
            logger.info("Handling standard response")
            return await handle_standard_response(client, model, processed_messages, temperature)

    except Exception as e:
        logger.error(f"Error in chat_completions: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": {"message": str(e)}}, status_code=500)

def process_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Process messages with content enhancements"""
    logger.debug(f"Processing {len(messages)} messages")
    processed = []

    for i, message in enumerate(messages):
        role = message.get("role", "user")
        content = message.get("content", "")

        logger.debug(f"Message {i}: role={role}, content_length={len(content)}")

        # Apply content processing
        if role == "user":
            content = process_user_content(content)
        elif role == "system":
            content = process_system_content(content)

        processed.append({"role": role, "content": content})

    logger.debug(f"Processed messages: {len(processed)}")
    return processed

def process_user_content(content: str) -> str:
    """Process user content with enhancements"""
    logger.debug("Processing user content")

    # Inject lorebook context
    if config.get("enable_lorebook", False):
        logger.debug("Injecting lorebook context")
        content = lorebook_manager.inject_context(content)

    return content

def process_system_content(content: str) -> str:
    """Process system content with jailbreak and enhancements"""
    logger.debug("Processing system content")
    enhancements = []

    # Add jailbreak text
    if config.get("enable_jailbreak", False):
        bypass_level = config.get("bypass_level", "none")
        jailbreak_text = get_jailbreak_text(bypass_level)
        if jailbreak_text:
            enhancements.append(jailbreak_text)
            logger.debug(f"Added jailbreak text: {bypass_level}")

    # Add medieval mode
    if config.get("enable_medieval_mode", False):
        medieval_text = get_medieval_text()
        enhancements.append(medieval_text)
        logger.debug("Added medieval mode text")

    # Add OOC injection
    if config.get("enable_ooc_injection", False):
        custom_ooc = config.get("custom_ooc_text")
        if custom_ooc:
            enhancements.append(custom_ooc)
            logger.debug("Added custom OOC text")
        else:
            ooc_template = get_ooc_template()
            enhancements.append(ooc_template)
            logger.debug("Added default OOC template")

    # Add force thinking
    if config.get("enable_force_thinking", False):
        thinking_message = get_thinking_message()
        enhancements.append(thinking_message)
        logger.debug("Added thinking message")

    # Combine enhancements with original content
    if enhancements:
        final_content = "\n\n".join(enhancements) + "\n\n" + content
        logger.debug(f"Combined {len(enhancements)} enhancements with original content")
        return final_content

    return content

async def handle_standard_response(client, model: str, messages: List[Dict[str, str]], temperature: float) -> Response:
    """Handle standard (non-streaming) response with logging"""
    logger.info("Handling standard response")

    try:
        logger.info(f"Calling Google AI with model: {model}")
        response = client.generate_content(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=False
        )

        content = response.text or ""
        logger.info(f"Received response, content length: {len(content)}")

        # Apply post-processing
        logger.info("Applying post-processing...")
        content = apply_post_processing(content)

        # Format for Janitor.ai
        formatted_response = format_for_janitor_response(content, model)
        logger.info("Response formatted successfully")

        return JSONResponse(content=formatted_response)

    except Exception as e:
        logger.error(f"Error in handle_standard_response: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": {"message": str(e)}}, status_code=500)

async def handle_streaming_response(client, model: str, messages: List[Dict[str, str]], temperature: float) -> Response:
    """Handle streaming response with logging"""
    logger.info("Handling streaming response")

    async def generate():
        try:
            logger.info(f"Starting streaming response with model: {model}")
            response = client.generate_content(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            chunk_count = 0
            for chunk in response:
                content = chunk.text or ""
                if content:
                    chunk_count += 1
                    logger.debug(f"Streaming chunk {chunk_count}, length: {len(content)}")
                    yield format_for_streaming_chunk(content)

            logger.info(f"Streaming completed, {chunk_count} chunks sent")
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'error': {'message': str(e)}})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )

def apply_post_processing(content: str) -> str:
    """Apply post-processing to response content with logging"""
    if not content:
        logger.warning("Empty content received for post-processing")
        return ""

    logger.debug(f"Post-processing content, length: {len(content)}")

    # Clean response text
    prefill_text = config.get("custom_prefill_text", "")
    content = clean_response_text(content, prefill_text)

    # Check and replace forbidden words
    if config.get("enable_forbidden_words", False):
        forbidden_words_str = config.get("forbidden_words", "")
        if forbidden_words_str:
            forbidden_words = [word.strip() for word in forbidden_words_str.split(",")]
            has_forbidden, _ = check_forbidden_words(content, forbidden_words)
            if has_forbidden:
                logger.debug(f"Replacing forbidden words: {forbidden_words}")
                content = replace_forbidden_words(content, forbidden_words)

    # Ensure markdown formatting
    if config.get("enable_markdown_check", False):
        logger.debug("Ensuring markdown formatting")
        content = ensure_markdown_formatting(content)

    logger.debug(f"Post-processing completed, final length: {len(content)}")
    return content

@app.get('/health')
async def health_check():
    """Health check endpoint with logging"""
    logger.info("Health check requested")
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": time.time()
    })

@app.get('/config')
async def get_config():
    """Get current configuration (safe values only) with logging"""
    logger.info("Configuration requested")
    safe_config = {
        "model": config.get("model"),
        "enable_jailbreak": config.get("enable_jailbreak"),
        "enable_ooc_injection": config.get("enable_ooc_injection"),
        "enable_markdown_check": config.get("enable_markdown_check"),
        "enable_force_thinking": config.get("enable_force_thinking"),
        "enable_medieval_mode": config.get("enable_medieval_mode"),
        "enable_better_spice": config.get("enable_better_spice"),
        "enable_autoplot": config.get("enable_autoplot"),
        "enable_crazy_mode": config.get("enable_crazy_mode"),
        "enable_lorebook": config.get("enable_lorebook"),
        "tunnel_provider": config.get("tunnel_provider")
    }
    logger.info(f"Returning configuration: {json.dumps(safe_config, indent=2)}")
    return JSONResponse(content=safe_config)
