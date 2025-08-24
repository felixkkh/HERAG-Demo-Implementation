from .text_chunker import TextChunker
from langchain_text_splitters import CharacterTextSplitter


text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base", chunk_size=100, chunk_overlap=0
)

class TokenLengthChunker(TextChunker):

    def chunk(self, text: str) -> list[str]:
        texts = text_splitter.split_text(text)

        return texts
