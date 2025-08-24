
import os
from ..extractor import Extractor
from logging_utils import logger


# Registry of available PDF extractors: 'type': (import_path, class_name)
PDF_EXTRACTOR_REGISTRY = {
    "docling": ("extractor.pdf.docling_pdf_extractor", "DoclingPDFExtractor"),
    "pdfium": ("extractor.pdf.pdfium_pdf_extractor", "PdfiumPDFExtractor"),
}

PDF_EXTRACTOR_TYPE = os.getenv("EXTRACTOR_PDF_TYPE", "docling").lower()


class PDFExtractor(Extractor):
    def __init__(self):
        import_path, class_name = PDF_EXTRACTOR_REGISTRY.get(PDF_EXTRACTOR_TYPE, PDF_EXTRACTOR_REGISTRY["docling"])
        module = __import__(import_path, fromlist=[class_name])
        extractor_cls = getattr(module, class_name)
        self._impl = extractor_cls()
        logger.debug(f"Using PDF extractor: {class_name}")

    def extract(self, file_path: str) -> str:
        return self._impl.extract(file_path)
