import requests
import json
import os
import numpy as np

# HuggingFace integration
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

# ONNX integration
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

class BaseLLMClient:
    """Base class for all LLM clients"""
    def __init__(self, model_name: str, api_base: str = None, api_key: str = None):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key

    def generate(self, prompt: str) -> str:
        raise NotImplementedError("Each LLM client must implement generate method")

class OllamaClient(BaseLLMClient):
    """Production client for Ollama API"""
    def generate(self, prompt: str) -> str:
        endpoint = f"{self.api_base}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        print(f"[OllamaClient] → {self.model_name} at {endpoint}")
        
        try:
            response = requests.post(endpoint, json=payload, timeout=120)
            response.raise_for_status()
            
            response_data = response.json()
            result = response_data.get("response", "")
            
            print(f"[OllamaClient] ✓ Response received from {self.model_name}")
            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"ERROR: Ollama {self.model_name} failed - {e}"
            print(f"[OllamaClient] ✗ {error_msg}")
            return error_msg

class OllamaCloudClient(BaseLLMClient):
    """Client for Ollama Cloud models"""
    def generate(self, prompt: str) -> str:
        endpoint = f"{self.api_base}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        print(f"[OllamaCloud] → {self.model_name}")
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"]
            
            print(f"[OllamaCloud] ✓ Response received from {self.model_name}")
            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"ERROR: OllamaCloud {self.model_name} failed - {e}"
            print(f"[OllamaCloud] ✗ {error_msg}")
            return error_msg

class HuggingFaceClient(BaseLLMClient):
    """Client for local HuggingFace models"""
    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name)
        if not HUGGINGFACE_AVAILABLE:
            raise ImportError("transformers not installed")
        
        print(f"[HuggingFace] Loading {model_name}...")
        try:
            self.pipeline = pipeline("text-generation", model=model_name, device_map="auto")
            print(f"[HuggingFace] ✓ {model_name} loaded")
        except Exception as e:
            print(f"[HuggingFace] ✗ Failed to load {model_name}: {e}")
            self.pipeline = None

    def generate(self, prompt: str) -> str:
        if not self.pipeline:
            return f"ERROR: HuggingFace model {self.model_name} not loaded"
        
        print(f"[HuggingFace] → {self.model_name}")
        
        try:
            result = self.pipeline(prompt, max_length=200, num_return_sequences=1)
            response = result[0]["generated_text"]
            
            print(f"[HuggingFace] ✓ Response generated from {self.model_name}")
            return response
            
        except Exception as e:
            error_msg = f"ERROR: HuggingFace {self.model_name} failed - {e}"
            print(f"[HuggingFace] ✗ {error_msg}")
            return error_msg

class FoundryClient(BaseLLMClient):
    """Production client for Azure AI Foundry"""
    def generate(self, prompt: str) -> str:
        endpoint = f"{self.api_base}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        print(f"[FoundryClient] → {self.model_name} at {endpoint}")
        
        try:
            response = requests.post(endpoint, json=payload, timeout=60)
            response.raise_for_status()
            
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"]
            
            print(f"[FoundryClient] ✓ Response received from {self.model_name}")
            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"ERROR: Foundry {self.model_name} failed - {e}"
            print(f"[FoundryClient] ✗ {error_msg}")
            return error_msg

class OpenAIClient(BaseLLMClient):
    """Production client for OpenAI API"""
    def generate(self, prompt: str) -> str:
        endpoint = f"{self.api_base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        print(f"[OpenAIClient] → {self.model_name}")
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"]
            
            print(f"[OpenAIClient] ✓ Response received from {self.model_name}")
            return result

        except requests.exceptions.RequestException as e:
            error_msg = f"ERROR: OpenAI {self.model_name} failed - {e}"
            print(f"[OpenAIClient] ✗ {error_msg}")
            return error_msg
