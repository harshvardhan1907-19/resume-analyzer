# resumes/services.py
import os
import logging
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Service class for interacting with OpenAI API
    """
    
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.warning("OpenAI API key not found in settings")
        
        # Initialize client without proxies parameter
        # For older versions (before 1.0.0)
        try:
            self.client = OpenAI(api_key=api_key)
        except TypeError as e:
            # If the error is about proxies, try older initialization
            logger.warning(f"Error with new OpenAI client: {e}")
            # Try importing the old style
            import openai
            openai.api_key = api_key
            self.client = None  # We'll use the module directly
    
    def analyze_resume(self, resume_text):
        """
        Analyze resume text using OpenAI API
        """
        if not resume_text or "No text could be extracted" in resume_text:
            return "Unable to analyze: No text could be extracted from the PDF."
        
        try:
            # Create a prompt for the AI
            prompt = f"""
            Please analyze the following resume and provide a comprehensive evaluation. Include:
            
            1. **Summary**: A brief overview of the candidate's profile
            2. **Key Skills**: List the main technical and soft skills
            3. **Strengths**: Highlight the candidate's strongest points
            4. **Areas for Improvement**: Suggest areas where the candidate could improve
            5. **Overall Rating**: Rate the resume on a scale of 1-10
            
            Resume Text:
            {resume_text[:8000]}
            """
            
            # Try using the client if available
            if self.client:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert resume reviewer and career coach."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                return response.choices[0].message.content
            else:
                # Fallback to old style
                import openai
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert resume reviewer and career coach."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"Error analyzing resume: {str(e)}"