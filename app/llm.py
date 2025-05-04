import google.generativeai as genai
from typing import List
from app.models import Assessment
from app.config import settings
import logging
import ast
import json
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class GeminiProcessor:
    """Wrapper for Gemini Pro LLM for refining recommendations"""
    
    def __init__(self):
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel()
            self.safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
            logger.info("Gemini processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            raise

    def refine_recommendations(self, query: str, assessments: List[Assessment]) -> List[Assessment]:
        """
        Refine and re-rank assessments using Gemini LLM
        
        Args:
            query: Original user query
            assessments: List of assessments from vector search
            
        Returns:
            Refined and re-ranked list of assessments
        """
        if not assessments:
            return assessments
            
        try:
            # Prepare prompt
            prompt = self._create_prompt(query, assessments)
            
            # Call Gemini API
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            
            # Parse response
            refined_assessments = self._parse_response(response.text, assessments)
            logger.info("Successfully refined recommendations with Gemini")
            return refined_assessments
            
        except Exception as e:
            logger.error(f"Gemini processing failed: {str(e)}")
            return assessments  # Fallback to original results

    def _create_prompt(self, query: str, assessments: List[Assessment]) -> str:
        """Create the prompt for Gemini"""
        assessments_text = "\n\n".join(
            f"Assessment {i+1}:\n"
            f"Name: {assess.name}\n"
            f"Description: {assess.description}\n"
            f"Type: {assess.test_type}\n"
            f"Duration: {assess.duration}\n"
            f"Remote: {'Yes' if assess.remote_support else 'No'}\n"
            f"Adaptive: {'Yes' if assess.adaptive_support else 'No'}\n"
            f"URL: {assess.url}\n"
            f"Current Score: {assess.score:.2f}"
            for i, assess in enumerate(assessments)
        )
        
        return f"""
        You are an expert in psychometric assessments and HR technology. 
        Your task is to refine SHL assessment recommendations based on the user's query.

        User Query:
        {query}

        Initial Recommendations (from vector search):
        {assessments_text}

        Instructions:
        1. Filter to only the most relevant {len(assessments)//2} assessments
        2. Re-score them (0.0-1.0) based on:
        - Query relevance
        - Duration requirements
        - Test type matching
        3. Return ONLY a JSON list with exactly {len(assessments)//2} items
        4. Format: [{{"url": "...", "score": 0.95}}

        Output must be valid JSON that can be parsed directly.
        """

    def _parse_response(self, response_text: str, original_assessments: List[Assessment]) -> List[Assessment]:
        """Parse Gemini's response and validate the results"""
        #logger.info(response_text)
        try:
            # First try to parse as proper JSON
            try:
                response_data = json.loads(response_text)
                if isinstance(response_data, list):
                    refined_items = response_data
                else:
                    raise ValueError("Response is not a list")
            except json.JSONDecodeError:
                # Fallback to extracting JSON substring
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                json_str = response_text[json_start:json_end]
                
                # Safely evaluate the string as JSON
                refined_items = ast.literal_eval(json_str)
            logger.info(refined_items)
            refined_assessments = []
            for item in refined_items:
                if not item or not isinstance(item, dict):
                    continue
                try:
                    # Normalize field names (Gemini might use different casing)
                    item_url = item.get('url') or item.get('URL')
                    item_score = item.get('score') or item.get('Score')

                    if not item_url or item_score is None:
                        continue

                    # Find matching original assessment
                    original = next((a for a in original_assessments if a.url == item_url), None)
                    if not original:
                        continue

                    refined_assessments.append(Assessment(
                        url=original.url,
                        name=original.name,
                        adaptive_support=original.adaptive_support,
                        description=original.description,
                        duration=original.duration,
                        remote_support=original.remote_support,
                        test_type=original.test_type,
                        score=float(item_score)
                    ))
                except (KeyError, StopIteration, ValidationError, TypeError) as e:
                    logger.warning(f"Failed to parse assessment: {str(e)}")
            
            return refined_assessments[:len(original_assessments)//2]  # Return top half
        
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            return original_assessments[:len(original_assessments)//2]  # Fallback to top half