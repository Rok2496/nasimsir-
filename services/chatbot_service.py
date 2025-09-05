import httpx
import os
from dotenv import load_dotenv
import json
import asyncio
import time

load_dotenv()

class ChatbotService:
    def __init__(self):
        # Load multiple API keys for fallback
        self.api_keys = [
            os.getenv("OPENROUTER_API_KEY_1"),
            os.getenv("OPENROUTER_API_KEY_2"),
            os.getenv("OPENROUTER_API_KEY_3")
        ]
        self.current_key_index = 0
        
        # Load multiple models for fallback with better ordering
        self.models = [
            os.getenv("OPENROUTER_MODEL_PRIMARY", "meta-llama/llama-3.3-70b-instruct:free"),
            os.getenv("OPENROUTER_MODEL_SECONDARY", "meta-llama/llama-3.1-405b-instruct:free"),
            os.getenv("OPENROUTER_MODEL_FALLBACK", "google/gemma-2-9b-it:free")
        ]
        self.current_model_index = 0
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Print debug information
        print(f"OpenRouter API Keys loaded: {len([key for key in self.api_keys if key])}")
        print(f"OpenRouter Models: {self.models}")
        
        # System prompt for the chatbot
        self.system_prompt = """[SYSTEM INSTRUCTIONS - FOLLOW EXACTLY]
You are a sales assistant for SmartTech, specializing exclusively in the RK3588 Interactive Smart Board.

When asked about the product or specifications, respond ONLY with this exact format:
---
Product: SmartTech Interactive Smart Board RK3588
Model: RK3588
OS: Android 12
RAM: 16GB
Storage: 256GB
Camera: 48MP AI camera with facial recognition
Microphones: 8 microphones array
Audio: 2.1 channel audio system
Security: NFC support, Fingerprint scanner
Sizes: 65", 75", 86", 98", 100", 105", 110"
Use Cases: Classrooms, offices, meeting rooms
---

When asked about pricing: "Contact 01678-134547 for pricing"
When asked about ordering or purchasing: "Contact 01678-134547 to place an order"
When asked to buy: "Contact 01678-134547 to place an order"

DO NOT mention any other products.
DO NOT provide generic information.
DO NOT make up specifications.
DO NOT deviate from the specified format.

Be helpful, friendly, and professional.
Always encourage interested customers to contact 01678-134547."""

    def _get_current_api_key(self):
        """Get the current API key, rotating through available keys"""
        # Filter out any None keys
        valid_keys = [key for key in self.api_keys if key]
        if not valid_keys:
            return None
        return valid_keys[self.current_key_index % len(valid_keys)]

    def _rotate_api_key(self):
        """Rotate to the next API key"""
        valid_keys = [key for key in self.api_keys if key]
        if valid_keys:
            self.current_key_index = (self.current_key_index + 1) % len(valid_keys)
            print(f"Rotating to API key {self.current_key_index + 1}")

    def _get_current_model(self):
        """Get the current model"""
        return self.models[self.current_model_index % len(self.models)]

    def _rotate_model(self):
        """Rotate to the next model"""
        self.current_model_index = (self.current_model_index + 1) % len(self.models)
        print(f"Rotating to model {self.current_model_index + 1}: {self._get_current_model()}")

    async def _make_request_with_retry(self, client, headers, payload, max_retries=3):
        """Make request with exponential backoff retry logic, key rotation, and model fallback"""
        # Try each API key in rotation
        valid_keys = [key for key in self.api_keys if key]
        if not valid_keys:
            raise Exception("No valid API keys available")
        
        # Keep track of models we've tried to prevent infinite loops
        tried_models = set()
        
        # Try each model in rotation
        for model_index in range(len(self.models) * 2):  # Try each model at most twice
            current_model = self._get_current_model()
            
            # If we've already tried this model, move to next one
            if current_model in tried_models:
                self._rotate_model()
                continue
            
            tried_models.add(current_model)
            payload["model"] = current_model
            print(f"Trying model: {current_model}")
            
            # Reset key index for each new model
            original_key_index = self.current_key_index
            
            for key_index in range(len(valid_keys) * 2):  # Try each key at most twice
                current_key = self._get_current_api_key()
                headers["Authorization"] = f"Bearer {current_key}"
                
                for attempt in range(max_retries + 1):
                    try:
                        response = await client.post(
                            self.base_url,
                            headers=headers,
                            json=payload,
                            timeout=30.0
                        )
                        
                        # Handle different response codes
                        if response.status_code == 429:
                            # Check if it's a rate limit error from the provider
                            try:
                                error_data = response.json()
                                if "rate-limited" in str(error_data).lower():
                                    print(f"Model {current_model} is rate-limited. Trying next model.")
                                    self._rotate_model()
                                    break  # Break inner loop to try next model
                            except:
                                pass
                            
                            if attempt < max_retries:
                                wait_time = (2 ** attempt) + (0.1 * attempt)  # Exponential backoff
                                print(f"Rate limited with key {self.current_key_index + 1} and model {self.current_model_index + 1}. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                # Max retries reached with this key, rotate to next key
                                print(f"Rate limited with key {self.current_key_index + 1} and model {self.current_model_index + 1}. Rotating to next key.")
                                self._rotate_api_key()
                                break  # Break inner loop to try next key
                        elif response.status_code == 401:
                            # Invalid key, rotate to next key
                            print(f"Invalid API key {self.current_key_index + 1} with model {self.current_model_index + 1}. Rotating to next key.")
                            self._rotate_api_key()
                            break  # Break inner loop to try next key
                        elif response.status_code == 404:
                            # Model not found, rotate to next model
                            print(f"Model {current_model} not found. Rotating to next model.")
                            self._rotate_model()
                            break  # Break inner loop to try next model
                        else:
                            # Success or other error, return response
                            return response, None, current_model
                            
                    except httpx.TimeoutException as e:
                        if attempt < max_retries:
                            wait_time = (2 ** attempt)  # Exponential backoff
                            print(f"Timeout on attempt {attempt + 1} with key {self.current_key_index + 1} and model {self.current_model_index + 1}. Waiting {wait_time}s before retry...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise e
                    except Exception as e:
                        if attempt < max_retries:
                            wait_time = (2 ** attempt)  # Exponential backoff
                            print(f"Error on attempt {attempt + 1} with key {self.current_key_index + 1} and model {self.current_model_index + 1}: {e}. Waiting {wait_time}s before retry...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise e
                
                # If we've exhausted retries with this key, continue to next key
                continue
            
            # If we've tried all keys with this model, continue to next model
            continue
        
        # If we've tried all models and keys and still failing, return error
        return None, "I'm experiencing high demand right now. Please wait a moment and try again, or contact us directly at 01678-134547 for immediate assistance.", None

    async def get_response(self, message: str, language: str = "en") -> str:
        """Get AI response from OpenRouter"""
        
        # Debug print
        print(f"Getting response for message: {message}")
        print(f"Using API Key: {self._get_current_api_key()[:10] if self._get_current_api_key() else 'None'}...")
        print(f"Using Model: {self._get_current_model()}")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add language instruction to the system prompt if not English
        system_prompt = self.system_prompt
        if language != "en":
            system_prompt += f"\n\nPlease respond in {language} language."
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": message}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        # Debug print
        print(f"Sending request to {self.base_url}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        
        async with httpx.AsyncClient() as client:
            try:
                response, rate_limit_message, used_model = await self._make_request_with_retry(client, headers, payload)
                
                if rate_limit_message:
                    return rate_limit_message
                
                if response is None:
                    return "I'm having technical difficulties. Please contact us at 01678-134547."
                
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {response.headers}")
                print(f"Used model: {used_model}")
                
                response.raise_for_status()
                
                data = response.json()
                print(f"Response data: {data}")
                
                # Extract the AI response
                ai_response = data["choices"][0]["message"]["content"]
                
                # Check if the response is empty and provide a fallback
                if not ai_response or ai_response.strip() == "":
                    print("AI returned empty response, providing fallback")
                    return "Hello! I'm your SmartTech assistant. We specialize in Interactive Smart Boards with Android 12, 16GB RAM, 256GB storage, and many advanced features. Our main product is the RK3588 model available in sizes from 65\" to 110\". How can I help you today? You can ask me about our products, pricing, or how to place an order."
                
                return ai_response
                
            except httpx.TimeoutException as e:
                print(f"Timeout error: {e}")
                return "I'm sorry, I'm experiencing some delays. Please try again in a moment."
            except httpx.HTTPStatusError as e:
                print(f"HTTP status error: {e}")
                print(f"Response text: {e.response.text}")
                if e.response.status_code == 401:
                    return "I'm currently unavailable. Please contact us directly at 01678-134547."
                elif e.response.status_code == 429:
                    return "I'm experiencing high demand right now. Please wait a moment and try again, or contact us directly at 01678-134547 for immediate assistance."
                return "I'm having technical difficulties. Please contact us at 01678-134547."
            except Exception as e:
                print(f"Chatbot error: {e}")
                return "I'm having technical difficulties. Please contact us at 01678-134547."