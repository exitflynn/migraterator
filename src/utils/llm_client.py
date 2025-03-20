import os
import requests
import json

class LLMClient:
    def __init__(self, api_key=None, provider=None):
        """
        Initialize the LLM client
        
        Args:
            api_key: API key for the LLM service (defaults to environment variable)
            provider: LLM provider to use ('openai' or 'gemini', defaults to environment variable)
        """
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        if not self.api_key:
            raise ValueError("LLM API key is required")
        
        # Determine which provider to use
        self.provider = provider or os.environ.get("LLM_PROVIDER", "openai").lower()
        
        if self.provider == "openai":
            self.api_url = os.environ.get("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
            self.model = os.environ.get("LLM_MODEL", "gpt-4")
        elif self.provider == "gemini":
            self.api_url = os.environ.get("LLM_API_URL", "https://generativelanguage.googleapis.com/v1beta/models")
            self.model = os.environ.get("LLM_MODEL", "gemini-pro")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}. Use 'openai' or 'gemini'.")
    
    def generate_text(self, prompt, max_tokens=1500):
        """
        Generate text using the LLM
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text
        """
        if self.provider == "openai":
            return self._generate_text_openai(prompt, max_tokens)
        elif self.provider == "gemini":
            return self._generate_text_gemini(prompt, max_tokens)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _generate_text_openai(self, prompt, max_tokens):
        """Generate text using OpenAI API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert DevOps engineer specializing in infrastructure as code."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2  # apparently that gives more factual responses
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _generate_text_gemini(self, prompt, max_tokens):
        """Generate text using Google's Gemini API"""
        # Construct the full URL with the model and API key
        full_url = f"{self.api_url}/{self.model}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Gemini API expects a different format
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "You are an expert DevOps engineer specializing in infrastructure as code.\n\n" + prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": max_tokens,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        response = requests.post(full_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the generated text from Gemini's response format
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected response format from Gemini API: {e}") 