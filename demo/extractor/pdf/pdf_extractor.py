
import os
from ..extractor import Extractor
from ...logging_utils import logger


# Registry of available PDF extractors: 'type': (import_path, class_name)
PDF_EXTRACTOR_REGISTRY = {
    "docling": ("demo.extractor.pdf.docling_pdf_extractor", "DoclingPDFExtractor"),
    "pdfium": ("demo.extractor.pdf.pdfium_pdf_extractor", "PdfiumPDFExtractor"),
}

class PDFExtractor(Extractor):
    def __init__(self):
        pass

    def extract(self, file_path: str) -> str:
        pdf_extractor_type = os.getenv("EXTRACTOR_PDF_TYPE", "docling").lower()
        import_path, class_name = PDF_EXTRACTOR_REGISTRY.get(pdf_extractor_type, PDF_EXTRACTOR_REGISTRY["docling"])
        module = __import__(import_path, fromlist=[class_name])
        extractor_cls = getattr(module, class_name)
        logger.debug(f"Using PDF extractor: {class_name}")
        return extractor_cls().extract(file_path)
