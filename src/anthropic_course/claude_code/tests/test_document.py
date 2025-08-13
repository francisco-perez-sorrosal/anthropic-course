import os
import pytest
from tools.document import binary_document_to_markdown, document_path_to_markdown


class TestBinaryDocumentToMarkdown:
    # Define fixture paths
    FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
    DOCX_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.docx")
    PDF_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.pdf")

    def test_fixture_files_exist(self):
        """Verify test fixtures exist."""
        assert os.path.exists(self.DOCX_FIXTURE), (
            f"DOCX fixture not found at {self.DOCX_FIXTURE}"
        )
        assert os.path.exists(self.PDF_FIXTURE), (
            f"PDF fixture not found at {self.PDF_FIXTURE}"
        )

    def test_binary_document_to_markdown_with_docx(self):
        """Test converting a DOCX document to markdown."""
        # Read binary content from the fixture
        with open(self.DOCX_FIXTURE, "rb") as f:
            docx_data = f.read()

        # Call function
        result = binary_document_to_markdown(docx_data, "docx")

        # Basic assertions to check the conversion was successful
        assert isinstance(result, str)
        assert len(result) > 0
        # Check for typical markdown formatting - this will depend on your actual test file
        assert "#" in result or "-" in result or "*" in result

    def test_binary_document_to_markdown_with_pdf(self):
        """Test converting a PDF document to markdown."""
        # Read binary content from the fixture
        with open(self.PDF_FIXTURE, "rb") as f:
            pdf_data = f.read()

        # Call function
        result = binary_document_to_markdown(pdf_data, "pdf")

        # Basic assertions to check the conversion was successful
        assert isinstance(result, str)
        assert len(result) > 0
        # Check for typical markdown formatting - this will depend on your actual test file
        assert "#" in result or "-" in result or "*" in result


class TestDocumentPathToMarkdown:
    # Define fixture paths
    FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
    DOCX_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.docx")
    PDF_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.pdf")

    # Basic Functionality Tests
    def test_valid_pdf_path(self):
        """Test converting a valid PDF file to markdown."""
        result = document_path_to_markdown(self.PDF_FIXTURE)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "#" in result or "-" in result or "*" in result

    def test_valid_docx_path(self):
        """Test converting a valid DOCX file to markdown."""
        result = document_path_to_markdown(self.DOCX_FIXTURE)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "#" in result or "-" in result or "*" in result

    def test_pdf_and_docx_produce_different_results(self):
        """Test that PDF and DOCX files produce different outputs."""
        pdf_result = document_path_to_markdown(self.PDF_FIXTURE)
        docx_result = document_path_to_markdown(self.DOCX_FIXTURE)
        
        # Assuming the test files have different content
        # This test might need adjustment based on your actual fixture files
        assert pdf_result != docx_result

    # File Path Tests  
    def test_absolute_path_pdf(self):
        """Test with absolute path to PDF file."""
        absolute_path = os.path.abspath(self.PDF_FIXTURE)
        result = document_path_to_markdown(absolute_path)
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_absolute_path_docx(self):
        """Test with absolute path to DOCX file.""" 
        absolute_path = os.path.abspath(self.DOCX_FIXTURE)
        result = document_path_to_markdown(absolute_path)
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_relative_path_pdf(self):
        """Test with relative path to PDF file."""
        # Change to parent directory to make path relative
        original_cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(self.FIXTURES_DIR))
            relative_path = os.path.join("tests", "fixtures", "mcp_docs.pdf")
            result = document_path_to_markdown(relative_path)
            
            assert isinstance(result, str)
            assert len(result) > 0
        finally:
            os.chdir(original_cwd)

    def test_relative_path_docx(self):
        """Test with relative path to DOCX file."""
        # Change to parent directory to make path relative  
        original_cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(self.FIXTURES_DIR))
            relative_path = os.path.join("tests", "fixtures", "mcp_docs.docx")
            result = document_path_to_markdown(relative_path)
            
            assert isinstance(result, str)
            assert len(result) > 0
        finally:
            os.chdir(original_cwd)

    def test_path_with_spaces(self):
        """Test with file path containing spaces."""
        # Create a temporary file with spaces in the name
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            spaced_path = os.path.join(temp_dir, "test file with spaces.pdf")
            shutil.copy2(self.PDF_FIXTURE, spaced_path)
            
            result = document_path_to_markdown(spaced_path)
            
            assert isinstance(result, str)
            assert len(result) > 0

    def test_non_existent_file(self):
        """Test error handling for non-existent file."""
        non_existent_path = "/path/that/does/not/exist.pdf"
        
        with pytest.raises(FileNotFoundError, match="File not found"):
            document_path_to_markdown(non_existent_path)

    def test_invalid_file_extension(self):
        """Test error handling for unsupported file extensions."""
        # Create a temporary file with invalid extension
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_file_path = temp_file.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                document_path_to_markdown(temp_file_path)
        finally:
            os.unlink(temp_file_path)

    def test_directory_path(self):
        """Test error handling when directory path is provided instead of file."""
        with pytest.raises(ValueError, match="Path is not a file"):
            document_path_to_markdown(self.FIXTURES_DIR)
