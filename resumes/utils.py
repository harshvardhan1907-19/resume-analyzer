import PyPDF2
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    """
    Utility class for parsing PDF files and extracting text
    """
    
    @staticmethod
    def extract_text_from_pdf(file_obj):
        """
        Extract text from a PDF file object
        
        Args:
            file_obj: File object containing PDF data
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            # Reset file pointer to beginning
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file_obj)
            
            # Extract text from all pages
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            
            text = text.strip()
            
            if not text:
                return "No text could be extracted from this PDF. It may be an image-based PDF or empty."
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")