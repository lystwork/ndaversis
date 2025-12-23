# pylint: disable=too-few-public-methods
"""A module for interacting with different AI services."""
import google.generativeai as genai

class AIService:
    """Base class for AI services."""
    def __init__(self):
        pass

    def generate_content(self, prompt, analysis_data):
        """Generate content using the AI service."""
        raise NotImplementedError

class GeminiService(AIService):
    """An AI service that uses the Google Gemini API."""
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_content(self, prompt, analysis_data):
        """Generate content using the Gemini API."""
        full_prompt = f"{prompt}\n\nCode Analysis:\n{analysis_data}"
        response = self.model.generate_content(full_prompt)
        return response.text

def get_ai_service(config):
    """Factory function to get an AI service instance."""
    if not config:
        return None
    provider = config.get("ai_provider")
    api_key = config.get("api_key")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("API key not found or is a placeholder. AI service disabled.")
        return None

    if provider == "gemini":
        return GeminiService(api_key)
    # Add other providers here
    return None
