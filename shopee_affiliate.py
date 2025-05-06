#!/usr/bin/env python3

import re
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def convert_shopee_affiliate_link(original_url, your_affiliate_id="18396650603"):
    """
    Converts a Shopee affiliate link to your own affiliate ID
    
    Args:
        original_url (str): The original Shopee affiliate URL
        your_affiliate_id (str): Your Shopee affiliate ID (default: 18396650603)
        
    Returns:
        str: The converted Shopee URL with your affiliate ID
    """
    # Remove whitespace and check if URL is empty
    if not original_url or not original_url.strip():
        return ""
    
    original_url = original_url.strip()
    
    # Handle URLs without scheme (add https://)
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url
    
    # If it's a shortened URL (s.shopee.com.br)
    if "s.shopee.com.br" in original_url:
        try:
            # Configure the request with headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            }
            
            # Follow the redirect to get the full URL with a timeout
            response = requests.head(original_url, allow_redirects=True, headers=headers, timeout=10)
            
            if response.status_code == 200 or response.status_code == 301 or response.status_code == 302:
                original_url = response.url
                print(f"Resolved shortened URL to: {original_url}")
            else:
                # If redirect fails, return the original URL
                print(f"Failed to resolve shortened URL. Status code: {response.status_code}")
                return original_url
        except Exception as e:
            # If there's an error following the redirect, return the original URL
            print(f"Error resolving shortened URL: {str(e)}")
            return original_url
    
    # Parse the URL
    parsed_url = urlparse(original_url)
    
    # If it's not a Shopee URL, return the original URL
    if not any(domain in parsed_url.netloc for domain in ["shopee.com.br", "shope.ee"]):
        return original_url
    
    # Extract query parameters
    query_params = parse_qs(parsed_url.query)
    
    # Update the utm_source parameter to your affiliate ID
    if "utm_source" in query_params:
        query_params["utm_source"] = [f"an_{your_affiliate_id}"]
    else:
        # If utm_source doesn't exist, add it
        query_params["utm_source"] = [f"an_{your_affiliate_id}"]
    
    # Make sure other required parameters are present
    if "utm_medium" not in query_params:
        query_params["utm_medium"] = ["affiliates"]
    
    # Update the utm_campaign parameter if it exists
    if "utm_campaign" not in query_params:
        # Add a default campaign ID if none exists
        query_params["utm_campaign"] = [f"id_{your_affiliate_id}"]
    
    # Rebuild the URL with the updated query parameters
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))
    
    return new_url

# For testing
if __name__ == "__main__":
    # Test with full URL
    original_url = "https://shopee.com.br/product/353265407/23398040660?uls_trackid=52l55q7m0157&utm_campaign=id_Tf3N6BDyvC&utm_content=----&utm_medium=affiliates&utm_source=an_18342670223&utm_term=cyvztjyijxj1"
    
    # Your affiliate ID
    your_affiliate_id = "18396650603"
    
    converted_url = convert_shopee_affiliate_link(original_url, your_affiliate_id)
    print(f"Original URL: {original_url}")
    print(f"Converted URL: {converted_url}")
    
    # Test with shortened URL
    shortened_url = "https://s.shopee.com.br/6AYGBLHWXo"
    converted_shortened_url = convert_shopee_affiliate_link(shortened_url, your_affiliate_id)
    print(f"\nOriginal Shortened URL: {shortened_url}")
    print(f"Converted Shortened URL: {converted_shortened_url}")
    
    # Test with the example URL from the user
    user_example = "https://s.shopee.com.br/7pgU9ozK4c"
    converted_user_example = convert_shopee_affiliate_link(user_example, your_affiliate_id)
    print(f"\nUser Example URL: {user_example}")
    print(f"Converted User Example URL: {converted_user_example}") 