import pypdfium2 as pdfium

from ...extractor.extractor import Extractor

class PdfiumPDFExtractor(Extractor):
    """
    Extracts text from PDF files using pypdfium2.
    """
    def extract(self, file_path):
        pdf = pdfium.PdfDocument(file_path)
        text = []
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            textpage = page.get_textpage()
            page_text = textpage.get_text_bounded()
            text.append(page_text)
        return "\n\n".join(text)
