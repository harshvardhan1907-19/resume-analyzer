import logging
import os
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone

from .models import Resume
from .serializers import ResumeUploadSerializer, ResumeSerializer
from .utils import PDFParser

from .services import OpenAIService
from .gemini_service import GeminiService
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

class ResumeUploadView(generics.CreateAPIView):
    """
    Upload a new resume and extract text
    """
    serializer_class = ResumeUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_create(self, serializer):
        # Save the resume
        resume = serializer.save(user=self.request.user)
        
        # Extract text from PDF
        try:
            file_obj = resume.file
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            
            # Extract text
            extracted_text = PDFParser.extract_text_from_pdf(file_obj)
            resume.content = extracted_text
            resume.status = 'completed'
            resume.save()
            
            logger.info(f"Successfully extracted text from resume {resume.id}")
            
        except Exception as e:
            logger.error(f"Error processing PDF for resume {resume.id}: {str(e)}")
            resume.status = 'failed'
            resume.error_message = str(e)
            resume.save()
            raise

class ResumeListView(generics.ListAPIView):
    """
    List all resumes for the authenticated user
    """
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user).order_by('-created_at')
    
# resumes/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import datetime

# resumes/views.py
import datetime
from pypdf import PdfReader
from google import genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class ResumeAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        try:
            # 1. Validate file presence
            if 'resume' not in request.FILES:
                return Response(
                    {"error": "No resume file found in the request."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['resume']
            
            # 2. In-memory Text Extraction from PDF
            try:
                reader = PdfReader(uploaded_file)
                resume_text = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        resume_text += text + "\n"
                
                if not resume_text.strip():
                    return Response(
                        {"error": "Could not extract text from the PDF. Ensure it is not an image-only scan."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                return Response(
                    {"error": f"Failed to parse PDF file: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 3. Call the Gemini AI Client with fallback models
            client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
            
            prompt = (
                "You are an expert technical recruiter and resume reviewer. "
                "Analyze the following resume text. Provide constructive feedback, "
                "highlight key strengths, note missing critical skills or areas of improvement, "
                "and give actionable advice to make it stand out:\n\n"
                f"{resume_text}"
            )

            models_to_try = [
                'gemini-3.5-flash',
                'gemini-2.5-flash',
                'gemini-1.5-flash',
            ]
            
            response = None
            last_error = None
            for model_name in models_to_try:
                try:
                    logger.info(f"Attempting resume analysis with Gemini model: {model_name}")
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    logger.info(f"Successfully analyzed resume with model: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to generate content with {model_name}: {str(e)}")
                    last_error = e
                    continue
            
            if response is None:
                raise last_error or Exception("All Gemini models failed to respond.")
            
            ai_analysis = response.text

            # 4. Return the live data to your frontend
            return Response({
                "analysis": ai_analysis,
                "filename": uploaded_file.name,
                "created_at": datetime.datetime.now().isoformat()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Internal server processing error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )