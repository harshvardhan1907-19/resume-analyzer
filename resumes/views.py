import logging
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

class ResumeAnalyzeView(APIView):
    # This ensures your 'Authorization: Bearer <token>' header is enforced
    permission_classes = [IsAuthenticated]
    # Necessary for handling file uploads (FormData)
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        try:
            # Check if file exists in the request
            if 'resume' not in request.FILES:
                return Response(
                    {"error": "No resume file found in the request."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['resume']
            
            # --- YOUR AI ANALYSIS LOGIC HERE ---
            # Extract text from uploaded_file (e.g., using PyPDF2 or pdfplumber)
            # Send text to your LLM / AI wrapper
            mock_analysis = "This is a placeholder for your AI model's feedback text."
            # -----------------------------------

            # The frontend expects this exact structural format:
            return Response({
                "analysis": mock_analysis,
                "filename": uploaded_file.name,
                "created_at": datetime.datetime.now().isoformat()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Catch crashes and explicitly force a JSON error response instead of HTML
            return Response(
                {"error": f"Internal server processing error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )