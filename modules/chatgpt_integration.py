"""
ChatGPT Integration Module for ZeroTraceGPT Image Creator
Provides prompt enhancement and image improvement features
"""

import os
import sys
import requests
import json
import base64
import time
from typing import Optional, Dict, Any
import gradio as gr

class ChatGPTIntegration:
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {}
        self.last_request_time = 0
        self.min_request_interval = 2  # Minimum 2 seconds between requests
        # Prompt for API key on initialization
        self._prompt_api_key()
    
    def _prompt_api_key(self) -> None:
        """Prompt user to enter OpenAI API key interactively"""
        # First, try to get from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.strip():
            print("\n" + "="*60)
            print("🤖 ChatGPT Integration - Using API key from environment variable")
            print("="*60)
            if self._validate_api_key(api_key.strip()):
                self.api_key = api_key.strip()
                self.headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                print("✅ API key validated successfully!")
                print("="*60 + "\n")
                return
            else:
                print("❌ API key from environment variable is invalid. Please enter a new one.\n")
        
        # Check if we're in an interactive terminal
        if not sys.stdin.isatty():
            # Not in interactive terminal (e.g., running as service or in web UI)
            print("\n" + "="*60)
            print("🤖 ChatGPT Integration - API Key Required")
            print("="*60)
            print("⚠️  Running in non-interactive mode.")
            print("Please set your OpenAI API key using one of these methods:")
            print("1. Set environment variable: OPENAI_API_KEY=your_key_here")
            print("2. Use the API key input in the web UI (if available)")
            print("3. Restart in interactive terminal mode")
            print("="*60 + "\n")
            return  # Don't block startup, allow setting later
        
        # Interactive terminal - prompt for API key
        print("\n" + "="*60)
        print("🤖 ChatGPT Integration - API Key Required")
        print("="*60)
        print("Please enter your OpenAI API key.")
        print("You can get your API key from: https://platform.openai.com/api-keys")
        print("The API key will be stored in memory only (not saved to disk).")
        print("(Press ESC or Ctrl+C to skip - prompt enhancement will be disabled)")
        print("-"*60)
        
        try:
            while True:
                try:
                    api_key = input("Enter your OpenAI API key (or press ESC to skip): ").strip()
                except KeyboardInterrupt:
                    # Handle Ctrl+C
                    raise
                except EOFError:
                    # Handle ESC or EOF
                    print("\n⚠️  API key input skipped. Prompt enhancement feature will be disabled.")
                    print("You can set your API key later using:")
                    print("   - Environment variable: OPENAI_API_KEY=your_key_here")
                    print("   - Or restart the application in interactive mode")
                    print("="*60 + "\n")
                    return
                
                # Check for ESC key (if input is empty and user pressed ESC)
                if not api_key:
                    response = input("No API key entered. Skip ChatGPT integration? (y/n): ").strip().lower()
                    if response == 'y':
                        print("\n⚠️  API key skipped. Prompt enhancement feature will be disabled.")
                        print("You can set your API key later using:")
                        print("   - Environment variable: OPENAI_API_KEY=your_key_here")
                        print("   - Or restart the application in interactive mode")
                        print("="*60 + "\n")
                        return
                    continue
                
                # Basic validation - OpenAI API keys typically start with 'sk-'
                if not api_key.startswith('sk-'):
                    response = input("⚠️  Warning: API key doesn't start with 'sk-'. Continue anyway? (y/n): ").strip().lower()
                    if response != 'y':
                        continue
                
                # Test the API key by making a simple request
                print("\n🔍 Validating API key...")
                if self._validate_api_key(api_key):
                    self.api_key = api_key
                    self.headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    print("✅ API key validated successfully!")
                    print("✨ Prompt enhancement feature is now enabled!")
                    print("="*60 + "\n")
                    return
                else:
                    print("❌ Invalid API key. Please check your API key and try again.\n")
                    response = input("Skip API key setup? (y/n): ").strip().lower()
                    if response == 'y':
                        print("\n⚠️  API key skipped. Prompt enhancement feature will be disabled.")
                        print("="*60 + "\n")
                        return
        except (KeyboardInterrupt, EOFError):
            print("\n⚠️  API key input cancelled. Prompt enhancement feature will be disabled.")
            print("You can set your API key later using:")
            print("   - Environment variable: OPENAI_API_KEY=your_key_here")
            print("   - Or restart the application in interactive mode")
            print("="*60 + "\n")
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key by making a test request"""
        try:
            test_headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            # Make a minimal test request
            test_payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            }
            response = requests.post(
                self.base_url, 
                headers=test_headers, 
                json=test_payload, 
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                print("   Error: Invalid API key (401 Unauthorized)")
                return False
            elif response.status_code == 429:
                print("   Warning: Rate limited, but API key appears valid")
                return True  # Rate limit means key is valid
            else:
                print(f"   Warning: Unexpected response ({response.status_code}), but continuing...")
                return True  # Assume valid if not 401
        except requests.exceptions.RequestException as e:
            print(f"   Error: Could not validate API key - {str(e)}")
            return False
    
    def set_api_key(self, api_key: str) -> bool:
        """Set API key programmatically (for UI updates)"""
        if not api_key or not api_key.strip():
            return False
        
        api_key = api_key.strip()
        if self._validate_api_key(api_key):
            self.api_key = api_key
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            return True
        return False
    
    def is_api_key_set(self) -> bool:
        """Check if API key is set"""
        return self.api_key is not None and len(self.api_key) > 0
    
    def _rate_limit_protection(self):
        """Ensure minimum time between API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_api_request(self, payload: dict, max_retries: int = 3) -> dict:
        """Make API request with retry logic and rate limiting"""
        if not self.is_api_key_set():
            return {"error": "API key not set. Please configure your OpenAI API key."}
        
        for attempt in range(max_retries):
            try:
                self._rate_limit_protection()
                response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=30)
                
                if response.status_code == 429:
                    # Rate limited - wait longer and retry
                    wait_time = min(60, (2 ** attempt) * 5)  # Exponential backoff, max 60 seconds
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                        continue
                    else:
                        return {"error": f"Rate limited. Please wait {wait_time} seconds and try again."}
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return {"error": f"Error connecting to ChatGPT API: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}
        
        return {"error": "Max retries exceeded"}
    
    def enhance_prompt(self, original_prompt: str, style_preference: str = "photorealistic", enhancement_percentage: int = 50) -> str:
        """
        Enhance a prompt using ChatGPT for better image generation
        
        Args:
            original_prompt: The original user prompt
            style_preference: Style preference (photorealistic, artistic, anime, etc.)
            enhancement_percentage: Enhancement intensity (10-100%)
        
        Returns:
            Enhanced prompt string
        """
        if not self.is_api_key_set():
            return "❌ API key not configured. Please set your OpenAI API key first."
        
        if not original_prompt.strip():
            return "Please enter a prompt to enhance."
        
        try:
            # Calculate enhancement intensity based on percentage
            if enhancement_percentage <= 30:
                enhancement_level = "subtle"
                detail_multiplier = "1.2-1.5x"
            elif enhancement_percentage <= 60:
                enhancement_level = "moderate"
                detail_multiplier = "1.5-2x"
            elif enhancement_percentage <= 80:
                enhancement_level = "strong"
                detail_multiplier = "2-2.5x"
            else:
                enhancement_level = "maximum"
                detail_multiplier = "2.5-3x"

            system_prompt = f"""You are an expert AI image generation prompt engineer. Your task is to enhance user prompts to create better, more detailed, and more effective prompts for AI image generation.

Enhancement Level: {enhancement_level} ({enhancement_percentage}%)
Detail Multiplier: {detail_multiplier}

Guidelines:
1. Add specific details about lighting, composition, and mood
2. Include technical photography terms when appropriate
3. Specify art style, medium, and quality descriptors
4. Add environmental and atmospheric details
5. Keep the core concept but make it more vivid and descriptive
6. Use comma-separated tags for better AI model understanding
7. Enhancement intensity: {enhancement_level} - aim for {detail_multiplier} more detailed than the original
8. Style preference: {style_preference}

Examples:
- "cat" → "beautiful orange tabby cat, sitting gracefully on a windowsill, soft natural lighting, detailed fur texture, photorealistic, high quality, 8K resolution"
- "landscape" → "breathtaking mountain landscape at sunset, golden hour lighting, dramatic clouds, lush green valleys, photorealistic, cinematic composition, high detail"

Enhance this prompt with {enhancement_level} intensity while keeping the original intent:"""

            user_prompt = f"Original prompt: '{original_prompt}'\n\nPlease enhance this prompt for better AI image generation results."

            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }

            result = self._make_api_request(payload)
            
            if "error" in result:
                return result["error"]
            
            enhanced_prompt = result["choices"][0]["message"]["content"].strip()
            return enhanced_prompt
            
        except KeyError as e:
            return f"Error parsing ChatGPT response: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def improve_image_prompt(self, original_prompt: str, generated_image_description: str = "", enhancement_percentage: int = 50) -> str:
        """
        Generate an improved prompt based on the original prompt and generated image
        
        Args:
            original_prompt: The original prompt used
            generated_image_description: Description of what was generated
            enhancement_percentage: Enhancement intensity (10-100%)
        
        Returns:
            Improved prompt for better results
        """
        if not self.is_api_key_set():
            return "❌ API key not configured. Please set your OpenAI API key first."
        
        if not original_prompt.strip():
            return "Please provide the original prompt to improve."
        
        try:
            # Calculate enhancement intensity based on percentage
            if enhancement_percentage <= 30:
                enhancement_level = "subtle"
                improvement_focus = "minor adjustments"
            elif enhancement_percentage <= 60:
                enhancement_level = "moderate"
                improvement_focus = "balanced improvements"
            elif enhancement_percentage <= 80:
                enhancement_level = "strong"
                improvement_focus = "significant enhancements"
            else:
                enhancement_level = "maximum"
                improvement_focus = "major improvements"

            system_prompt = f"""You are an expert AI image generation prompt engineer. Your task is to analyze the original prompt and suggest improvements for generating a better version of the image.

Enhancement Level: {enhancement_level} ({enhancement_percentage}%)
Improvement Focus: {improvement_focus}

Guidelines:
1. Identify what might be missing from the original prompt
2. Suggest better lighting, composition, or style descriptions
3. Add technical details that could improve quality
4. Consider different artistic approaches or perspectives
5. Suggest specific improvements for better visual impact
6. Keep the core concept but enhance the execution
7. Provide 2-3 alternative improved prompts
8. Enhancement intensity: {enhancement_level} - focus on {improvement_focus}

Focus on making the prompt more effective for AI image generation with {enhancement_level} intensity."""

            user_prompt = f"""Original prompt: '{original_prompt}'
Generated image description: '{generated_image_description}'

Please suggest improvements to create a better version of this image. Provide specific, actionable improvements to the prompt."""

            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 600,
                "temperature": 0.8
            }

            result = self._make_api_request(payload)
            
            if "error" in result:
                return result["error"]
            
            improved_suggestions = result["choices"][0]["message"]["content"].strip()
            return improved_suggestions
            
        except KeyError as e:
            return f"Error parsing ChatGPT response: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def generate_alternative_prompt(self, original_prompt: str, variation_type: str = "creative") -> str:
        """
        Generate alternative prompts for creative variations
        
        Args:
            original_prompt: The original prompt
            variation_type: Type of variation (creative, artistic, photorealistic, etc.)
        
        Returns:
            Alternative prompt string
        """
        if not self.is_api_key_set():
            return "❌ API key not configured. Please set your OpenAI API key first."
        
        if not original_prompt.strip():
            return "Please provide a prompt to create variations."
        
        try:
            system_prompt = f"""You are a creative AI image generation prompt engineer. Create alternative prompts that explore different artistic interpretations of the original concept.

Guidelines:
1. Keep the core subject/concept
2. Explore different artistic styles, moods, or perspectives
3. Vary lighting, composition, and atmosphere
4. Consider different art movements or techniques
5. Create prompts that would generate visually distinct but related images
6. Variation type: {variation_type}

Provide 3 creative alternative prompts that explore different artistic directions."""

            user_prompt = f"Original prompt: '{original_prompt}'\n\nCreate creative alternative prompts for different artistic interpretations."

            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.9
            }

            result = self._make_api_request(payload)
            
            if "error" in result:
                return result["error"]
            
            alternatives = result["choices"][0]["message"]["content"].strip()
            return alternatives
            
        except KeyError as e:
            return f"Error parsing ChatGPT response: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

def _create_dummy_instance():
    """Create a dummy ChatGPT instance when API key is not available"""
    class DummyChatGPT:
        def __init__(self):
            self.api_key = None
        
        def is_api_key_set(self):
            return False
        
        def enhance_prompt(self, *args, **kwargs):
            return "❌ ChatGPT API key is not configured. Prompt enhancement is disabled."
        
        def improve_image_prompt(self, *args, **kwargs):
            return "❌ ChatGPT API key is not configured. Image improvement is disabled."
        
        def generate_alternative_prompt(self, *args, **kwargs):
            return "❌ ChatGPT API key is not configured. Alternative prompts are disabled."
    
    return DummyChatGPT()

# Global instance - initialize on module import (will prompt for API key if in interactive mode)
_chatgpt_instance = None
try:
    _chatgpt_instance = ChatGPTIntegration()
except KeyboardInterrupt:
    # User pressed ESC/Ctrl+C to skip
    print("ChatGPT integration: API key input skipped, feature disabled.")
    _chatgpt_instance = _create_dummy_instance()
except Exception as e:
    # Other errors (non-interactive mode, etc.)
    print(f"ChatGPT integration: {e}")
    _chatgpt_instance = _create_dummy_instance()

# For backward compatibility
chatgpt = _chatgpt_instance if _chatgpt_instance else _create_dummy_instance()

def get_chatgpt_instance():
    """Get ChatGPT integration instance"""
    return _chatgpt_instance if _chatgpt_instance else _create_dummy_instance()

def is_chatgpt_available() -> bool:
    """Check if ChatGPT integration is available (API key is set)"""
    try:
        return chatgpt.is_api_key_set() if hasattr(chatgpt, 'is_api_key_set') else False
    except:
        return False

def enhance_prompt_ui(original_prompt: str, style_preference: str, enhancement_percentage: int) -> str:
    """UI wrapper for prompt enhancement"""
    if not is_chatgpt_available():
        return "❌ ChatGPT API key is not configured. Prompt enhancement is disabled.\n\n" \
               "To enable prompt enhancement:\n" \
               "1. Set environment variable: OPENAI_API_KEY=your_key_here\n" \
               "2. Or restart the application and enter your API key when prompted\n" \
               "3. Get your API key from: https://platform.openai.com/api-keys"
    instance = get_chatgpt_instance()
    return instance.enhance_prompt(original_prompt, style_preference, enhancement_percentage)

def improve_image_prompt_ui(original_prompt: str, image_description: str, enhancement_percentage: int) -> str:
    """UI wrapper for image improvement"""
    if not is_chatgpt_available():
        return "❌ ChatGPT API key is not configured. Image improvement is disabled."
    instance = get_chatgpt_instance()
    return instance.improve_image_prompt(original_prompt, image_description, enhancement_percentage)

def generate_alternative_prompt_ui(original_prompt: str, variation_type: str) -> str:
    """UI wrapper for alternative prompt generation"""
    if not is_chatgpt_available():
        return "❌ ChatGPT API key is not configured. Alternative prompts are disabled."
    instance = get_chatgpt_instance()
    return instance.generate_alternative_prompt(original_prompt, variation_type)
