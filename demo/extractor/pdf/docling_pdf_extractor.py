import os
from docling.datamodel.base_models import InputFormat


from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

from ..extractor import Extractor

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = os.getenv("EXTRACTOR_PDF_OCR", "false").lower() == "true"
pipeline_options.do_table_structure = os.getenv("EXTRACTOR_PDF_TABLE_STRUCTURE", "false").lower() == "true"

converter = DocumentConverter(
    allowed_formats=[
        InputFormat.PDF,
    ],
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    },
)

class DoclingPDFExtractor(Extractor):
    
    def extract(self, file_path: str) -> str:
        result = converter.convert(file_path)
        return result.document.export_to_markdown()
