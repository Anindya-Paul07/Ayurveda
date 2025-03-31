"""
Google Search Service

This module provides functionality to perform Google searches using the SerpApi.
It encapsulates the API call and returns formatted search results.
"""

from serpapi import GoogleSearch
import os


def execute_google_search(query):
    """
    Execute a Google search using SerpApi and return formatted results.
    
    Args:
        query (str): The search query string
        
    Returns:
        str: Formatted search results or error message
    """
    api_key = os.getenv('SERP_API_KEY')
    if not api_key:
        return 'SERP API key not configured.'
    
    params = {
        'q': query,
        'location': 'United States',
        'hl': 'en',
        'gl': 'us',
        'num': '3',
        'api_key': api_key,
        'engine': "google",
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if 'organic_results' in results:
            output_lines = []
            for result in results['organic_results']:
                title = result.get('title', 'No Title')
                snippet = result.get('snippet', 'No snippet available.')
                link = result.get('link', 'No link available.')
                output_lines.append(f"Title: {title}\nSnippet: {snippet}\nLink: {link}")
            return '\n\n'.join(output_lines)
        else:
            return 'No results found.'
    except Exception as e:
        return f'Error performing search: {str(e)}'