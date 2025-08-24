from abc import ABC, abstractmethod

class Extractor(ABC):
    """Abstract base class for document extractors."""
    
    @abstractmethod
    def extract(self, file_path: str) -> str:
        """Extract text from the given file path."""
        pass
