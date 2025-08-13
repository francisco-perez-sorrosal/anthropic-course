from markitdown import MarkItDown, StreamInfo
from io import BytesIO
from pathlib import Path
from pydantic import Field


def binary_document_to_markdown(binary_data: bytes, file_type: str) -> str:
    """Converts binary document data to markdown-formatted text."""
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    file_path: str = Field(description="Path to a PDF or DOCX file to convert to markdown")
) -> str:
    """Converts a document file (PDF or DOCX) to markdown-formatted text.
    
    Takes a file path to a PDF or DOCX document and returns the document
    content converted to markdown format using MarkItDown library.
    
    When to use:
    - When you need to extract and format content from PDF files
    - When you need to convert DOCX documents to markdown
    - When you want readable text representation of document files
    
    Examples:
    >>> document_path_to_markdown("./documents/report.pdf")
    # Report Title\n\nThis is the content...
    >>> document_path_to_markdown("/path/to/document.docx")
    # Document content in markdown format
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    file_extension = path.suffix.lower()
    if file_extension not in ['.pdf', '.docx']:
        raise ValueError(f"Unsupported file type: {file_extension}. Only .pdf and .docx files are supported.")
    
    md = MarkItDown()
    result = md.convert(str(path))
    return result.text_content
