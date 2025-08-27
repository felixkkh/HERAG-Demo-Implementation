import os
from .text_chunker import TextChunker
from ..logging_utils import logger

# Registry of available chunkers: 'type': (import_path, class_name)
CHUNKER_REGISTRY = {
    "character_length": ("demo.chunker.character_length_chunker", "CharacterLengthChunker"),
    "token_length": ("demo.chunker.token_length_chunker", "TokenLengthChunker"),
}

class Chunker(TextChunker):

    def chunk(self, text: str) -> list[str]:
        chunker_type = os.getenv("CHUNKER_TYPE", "character_length").lower()
        import_path, class_name = CHUNKER_REGISTRY.get(chunker_type, CHUNKER_REGISTRY["character_length"])
        module = __import__(import_path, fromlist=[class_name])
        chunker_cls = getattr(module, class_name)
        logger.debug(f"Using chunker: {class_name}")
        return chunker_cls().chunk(text)
