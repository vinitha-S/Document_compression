import zlib
import io
import PyPDF2
from django.http import HttpResponse
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from docx import Document


class FileUploadAndCompressView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        if 'file' in request.data:
            uploaded_file = request.data['file']
            file_extension = uploaded_file.name.lower().split('.')[-1]
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

            # Get the file extension (e.g., ".pdf", ".pptx", ".docx"

            if file_extension in ('pptx', 'docx'):
                # Handle PDF, PPTX, and DOCX file compression
                compressed_data = self.compress_file(uploaded_file.read())

                # Create an in-memory file for the compressed data
                compressed_file = io.BytesIO(compressed_data)
                compressed_file.seek(0)

                # Determine the content type based on the file extension
                content_type = {
                    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                }.get(file_extension, 'application/octet-stream')

                # Respond with the compressed file
                response = HttpResponse(compressed_file, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename=compressed.{file_extension}'
                return response
            else:
                # Handle other file types or actions
                return Response({'message': f'File uploaded successfully ({file_extension} format)'},
                                status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid or missing file.'}, status=status.HTTP_400_BAD_REQUEST)

    def compress_file(self, data):
        # Compress data using zlib
        return zlib.compress(data, level=zlib.Z_BEST_COMPRESSION)
