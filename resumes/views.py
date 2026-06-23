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
    
class ResumeAnalyzeView(APIView):
    """
    Analyze a resume using AI (Gemini preferred, OpenAI as fallback)
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize both services
        self.gemini_service = GeminiService()
        self.openai_service = OpenAIService()
    
    def post(self, request, *args, **kwargs):
        # Check if file is provided
        file_obj = request.FILES.get('resume')
        if not file_obj:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file is PDF
        if not file_obj.name.lower().endswith('.pdf'):
            return Response(
                {'error': 'File must be a PDF'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Save the file temporarily
            resume = Resume.objects.create(
                user=request.user,
                file=file_obj,
                filename=file_obj.name,
                file_size=file_obj.size,
                status='pending'
            )
            
            # Extract text from PDF
            try:
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
                
                extracted_text = PDFParser.extract_text_from_pdf(file_obj)
                resume.content = extracted_text
                resume.status = 'processing'
                resume.save()
                
                logger.info(f"Extracted {len(extracted_text)} characters from resume {resume.id}")
                
            except Exception as e:
                logger.error(f"PDF extraction error for resume {resume.id}: {str(e)}")
                resume.status = 'failed'
                resume.error_message = str(e)
                resume.save()
                return Response(
                    {'error': f'Failed to extract text from PDF: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Analyze with AI - Try Gemini first, fallback to OpenAI
            analysis = None
            analysis_source = None
            
            # Try Gemini
            try:
                analysis = self.gemini_service.analyze_resume(extracted_text)
                if analysis and "Mock Mode" not in analysis and "Error" not in analysis:
                    analysis_source = "Google Gemini"
                    logger.info(f"Analysis completed using Gemini for resume {resume.id}")
            except Exception as e:
                logger.warning(f"Gemini failed: {str(e)}")
            
            # If Gemini failed, try OpenAI
            if not analysis or analysis_source is None:
                try:
                    analysis = self.openai_service.analyze_resume(extracted_text)
                    if analysis and "Mock Mode" not in analysis and "Error" not in analysis:
                        analysis_source = "OpenAI"
                        logger.info(f"Analysis completed using OpenAI for resume {resume.id}")
                except Exception as e:
                    logger.warning(f"OpenAI failed: {str(e)}")
            
            # If both fail, use mock analysis
            if not analysis or analysis_source is None:
                analysis = self.gemini_service._get_mock_analysis(extracted_text)
                analysis_source = "Mock Mode"
                logger.info(f"Using mock analysis for resume {resume.id}")
            
            # Save the analysis
            resume.analysis = analysis + f"\n\n---\n**Analysis Source**: {analysis_source}"
            resume.status = 'completed'
            resume.analyzed_at = timezone.now()
            resume.save()
            
            return Response({
                'id': resume.id,
                'filename': resume.filename,
                'analysis': resume.analysis,
                'status': resume.status,
                'source': analysis_source,
                'created_at': resume.created_at
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error processing resume: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )