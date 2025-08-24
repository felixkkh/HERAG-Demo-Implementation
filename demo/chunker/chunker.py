import os
from .text_chunker import TextChunker
from logging_utils import logger

# Registry of available chunkers: 'type': (import_path, class_name)
CHUNKER_REGISTRY = {
    "character_length": ("chunker.character_length_chunker", "CharacterLengthChunker"),
    "token_length": ("chunker.token_length_chunker", "TokenLengthChunker"),
}

CHUNKER_TYPE = os.getenv("CHUNKER_TYPE", "character_length").lower()

class Chunker(TextChunker):
    def __init__(self):
        import_path, class_name = CHUNKER_REGISTRY.get(CHUNKER_TYPE, CHUNKER_REGISTRY["character_length"])
        module = __import__(import_path, fromlist=[class_name])
        chunker_cls = getattr(module, class_name)
        self._impl = chunker_cls()
        logger.debug(f"Using chunker: {class_name}")

    def chunk(self, text: str) -> list[str]:
        return self._impl.chunk(text)
