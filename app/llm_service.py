import os
from typing import Optional, Dict, Any
from anthropic import Anthropic, RateLimitError, APIError
import openai
from openai import OpenAI
from fastapi import HTTPException
import time
import google.generativeai as genai

class LLMService:
    def __init__(self):
        self.provider = os.getenv('LLM_PROVIDER', 'anthropic').lower()
        self.anthropic_client = None
        self.openai_client = None
        
        if self.provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            self.anthropic_client = Anthropic(api_key=api_key)
            self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        
        elif self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.openai_client = OpenAI(api_key=api_key)
            self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        
        elif self.provider == 'google':
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            genai.configure(api_key=api_key)
            self.model = os.getenv('GOOGLE_MODEL', 'gemini-pro')
            self.gemini_model = genai.GenerativeModel(self.model)
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate_response(self, prompt: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                if self.provider == 'anthropic':
                    return await self._generate_anthropic_response(prompt)
                elif self.provider == 'openai':
                    return await self._generate_openai_response(prompt)
                elif self.provider == 'google':
                    return await self._generate_gemini_response(prompt)
                    
            except RateLimitError:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                else:
                    raise HTTPException(
                        status_code=429,
                        detail="API rate limit exceeded. Please try again later."
                    )
            
            except (APIError, openai.APIError) as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"API error: {str(e)}"
                    )
            
            except genai.types.BlockedPromptException as e:
                # Handle Gemini content filter blocks
                raise HTTPException(
                    status_code=400,
                    detail="The request was blocked by content filters. Please try rephrasing your question."
                )
            
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Unexpected error: {str(e)}"
                )
    
    async def _generate_anthropic_response(self, prompt: str) -> str:
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return response.content[0].text
    
    async def _generate_openai_response(self, prompt: str) -> str:
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    async def _generate_gemini_response(self, prompt: str) -> str:
        # Configure safety settings to be less restrictive for philosophical dialogue
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]
        
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40
                ),
                safety_settings=safety_settings
            )
            
            # Check if response was blocked
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                return "I apologize, but I cannot provide a response to this query. Please try rephrasing your question or asking about a different topic."
            
            # Check candidates
            if response.candidates:
                candidate = response.candidates[0]
                
                # Check finish reason
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason != 1:  # 1 = STOP (normal completion)
                    finish_reasons = {
                        2: "blocked by safety filters",
                        3: "hit max tokens limit",
                        4: "recitation issue",
                        5: "other reason"
                    }
                    reason = finish_reasons.get(candidate.finish_reason, "unknown reason")
                    return f"I apologize, but I couldn't provide a complete response ({reason}). Please try rephrasing your question."
                
                # Get the text from content parts
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    return candidate.content.parts[0].text
            
            # Fallback if structure is different
            if hasattr(response, 'text'):
                return response.text
            
            return "I apologize, but I couldn't generate a proper response. Please try again with a different question."
            
        except Exception as e:
            # Handle any other Gemini-specific errors
            if "finish_reason" in str(e):
                return "I apologize, but I cannot provide a response to this query due to content filters. Please try rephrasing your question."
            raise e