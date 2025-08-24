from .text_chunker import TextChunker
from langchain_text_splitters import CharacterTextSplitter


text_splitter = CharacterTextSplitter(
    separator="",
    chunk_size=200,
    chunk_overlap=0,
    length_function=len,
    is_separator_regex=False,
)

class CharacterLengthChunker(TextChunker):

    def chunk(self, text: str) -> list[str]:
        texts = text_splitter.split_text(text)

        return texts
