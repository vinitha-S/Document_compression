
import PyPDF2
from django.http import HttpResponse
import io
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class FileUploadAndCompressView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        if 'file' in request.data:
            uploaded_file = request.data['file']

            # Check the file type
            if uploaded_file.name.lower().endswith('.pdf'):
                # Handle PDF file upload and compression
                pdf_reader = PyPDF2.PdfFileReader(uploaded_file)
                pdf_writer = PyPDF2.PdfFileWriter()

                for page_num in range(pdf_reader.getNumPages()):
                    page = pdf_reader.getPage(page_num)
                    page.compressContentStreams()  # Compress the content streams on each page
                    pdf_writer.addPage(page)

                # Create an in-memory file for the compressed PDF
                compressed_pdf = io.BytesIO()
                pdf_writer.write(compressed_pdf)
                compressed_pdf.seek(0)
                # Respond with the compressed PDF
                response = HttpResponse(compressed_pdf, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename=compressed.pdf'
                return response
            else:
                return Response({'message': 'File uploaded successfully (but not a PDF)'},
                                status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid or missing file.'}, status=status.HTTP_400_BAD_REQUEST)
