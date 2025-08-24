from abc import ABC, abstractmethod

class TextChunker(ABC):
    """Abstract base class for document chunkers."""
    
    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """Chunk the given text into smaller segments."""
        pass
