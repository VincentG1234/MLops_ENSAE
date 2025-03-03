import unittest
from unittest.mock import Mock, patch

from query_data import format_sources, query_database_agent


class TestQueryData(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.mock_embeddings = Mock()
        self.mock_db = Mock()

    def test_format_sources(self):
        """Test the format_sources function"""
        # Test single source
        sources = ['uploads\\document1.md']
        result = format_sources(sources)
        self.assertEqual(result, 'document1')

        # Test multiple sources with order-independent comparison
        sources = ['uploads\\document1.md', 'uploads\\document2.md', 'uploads\\document3.md']
        result = format_sources(sources)
        result_parts = set(result.replace(' and ', '; ').split('; '))
        expected_parts = {'document1', 'document2', 'document3'}
        self.assertEqual(result_parts, expected_parts)

        # Test duplicate sources
        sources = ['uploads\\document1.md', 'uploads\\document1.md']
        result = format_sources(sources)
        self.assertEqual(result, 'document1')

    @patch('query_data.OpenAIEmbeddings')
    @patch('query_data.Chroma')
    @patch('query_data.OpenAI')
    def test_query_database_agent(self, mock_openai, mock_chroma, mock_embeddings):
        """Test the query_database_agent function"""
        # Mock the database response
        mock_doc = Mock()
        mock_doc.page_content = "Test content"
        mock_doc.metadata = {"source": "test_source.md"}
        mock_results = [(mock_doc, 0.8)]

        mock_db_instance = Mock()
        mock_db_instance.similarity_search_with_relevance_scores.return_value = mock_results
        mock_chroma.return_value = mock_db_instance

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_openai_instance = Mock()
        mock_openai_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_openai_instance

        # Test the function
        result = query_database_agent("test question")

        # Verify the response format
        self.assertIn('answer', result)
        self.assertIn('sources', result)
        self.assertIsInstance(result['sources'], list)

if __name__ == '__main__':
    unittest.main()