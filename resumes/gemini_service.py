# resumes/gemini_service.py
import os
import logging
from django.conf import settings
from google import genai

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
        
        if not self.api_key:
            logger.warning("Gemini API key not found in settings")
            self.client = None
            self.model_name = None
            return
        
        try:
            self.client = genai.Client(api_key=self.api_key)
            
            # Use gemini-2.5-flash as primary model
            # Add fallback models in case
            self.model_name = "gemini-2.5-flash"
            
            # Verify the model works
            try:
                test_response = self.client.models.generate_content(
                    model=self.model_name,
                    contents="Test connection"
                )
                logger.info(f"✅ Using Gemini model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Model {self.model_name} failed: {e}")
                # Try fallback models
                fallback_models = [
                    "gemini-2.0-flash",
                    "gemini-1.5-flash",
                    "gemini-pro"
                ]
                for fallback in fallback_models:
                    try:
                        test_response = self.client.models.generate_content(
                            model=fallback,
                            contents="Test connection"
                        )
                        self.model_name = fallback
                        logger.info(f"✅ Using fallback model: {self.model_name}")
                        break
                    except:
                        continue
                
                if not self.model_name:
                    logger.error("❌ No Gemini models available")
                    self.client = None
            
        except Exception as e:
            logger.error(f"Error initializing Gemini: {str(e)}")
            self.client = None
    
    def analyze_resume(self, resume_text):
        if not self.client or not self.model_name:
            return self._get_mock_analysis(resume_text)
        
        if not resume_text or "No text could be extracted" in resume_text:
            return "Unable to analyze: No text could be extracted from the PDF."
        
        try:
            prompt = f"""
            Please analyze the following resume and provide a comprehensive evaluation. Include:
            
            1. **Summary**: A brief overview of the candidate's profile
            2. **Key Skills**: List the main technical and soft skills
            3. **Strengths**: Highlight the candidate's strongest points
            4. **Areas for Improvement**: Suggest areas where the candidate could improve
            5. **Experience Quality**: Assess the quality of work experience
            6. **Recommendations**: Provide actionable suggestions for the candidate
            7. **Overall Rating**: Rate the resume on a scale of 1-10
            
            Format your response with clear headings and bullet points.
            
            Resume Text:
            {resume_text[:8000]}
            """
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            if response and response.text:
                return response.text
            else:
                return "No analysis generated. Please try again."
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return f"Error analyzing resume: {str(e)}"
    
    def _get_mock_analysis(self, resume_text):
        return """
📄 **Resume Analysis (Mock Mode)**

⚠️ **Note**: This is a mock analysis. Gemini API is not configured.

---

**📊 SUMMARY**
The candidate appears to have a technical background with relevant experience.

**🛠️ KEY SKILLS**
• Technical skills based on resume content
• Problem-solving abilities
• Communication skills

**✅ STRENGTHS**
- Professional experience in the field
- Good technical foundation
- Clear presentation of qualifications

**📈 AREAS FOR IMPROVEMENT**
- Add more specific achievements with metrics
- Include project details and outcomes
- Highlight leadership experience

**⭐ OVERALL RATING: 7/10**

**💡 RECOMMENDATIONS**
1. Quantify your achievements (e.g., "Improved performance by 30%")
2. Add a compelling summary section
3. Include relevant certifications
4. Showcase your projects with links

---

*💡 Tip: Add your Gemini API key to get real AI-powered analysis.*
"""