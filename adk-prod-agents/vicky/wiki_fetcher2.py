import requests
from bs4 import BeautifulSoup
import html2text
from typing import Tuple, Optional
import urllib.parse
import re # Import regex for more robust image URL cleaning
import traceback # For printing detailed errors

# Corrected type hint: Tuple[Optional[str], Optional[str]]
def fetch_wikipedia_data(query_word: str, language: str = 'en') -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches a Wikipedia page, converts its main content to Markdown,
    and finds the primary image URL.

    Args:
        query_word: The word or phrase to search for on Wikipedia (e.g., "shark").
        language: The language of the Wikipedia page (default: 'en').

    Returns:
        A tuple containing:
        - The Markdown content of the main article body (str) or None if failed.
        - The URL of the primary image (str) or None if not found or failed.
    """
    if not query_word:
        # Using print for simple logging in this script
        print("Error: Query word cannot be empty.")
        return None, None
    if language not in ['en', 'de', 'fr', 'es', 'it', 'ja', 'zh']:
        language = 'en'

    formatted_query = query_word[0].upper() + query_word[1:]
    formatted_query = formatted_query.replace(" ", "_")
    # Ensure safe URL encoding for the path component
    wiki_url = f"https://{language}.wikipedia.org/wiki/{urllib.parse.quote(formatted_query)}"
    print(f"Attempting to fetch: {wiki_url} in language '{language}'")

    try:
        # Standard practice: Set a descriptive User-Agent
        headers = {'User-Agent': 'MyWikiFetcherScript/1.1 (Python)'} # Incremented version
        # Increased timeout for potentially slow connections or large pages
        response = requests.get(wiki_url, headers=headers, timeout=20)
        # Raise HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {wiki_url}: {e}")
        # Specifically mention 404 errors
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
             print(f"Page not found at {wiki_url}. Check spelling or if page exists.")
        return None, None
    except Exception as e:
        # Catch any other unexpected errors during the request phase
        print(f"An unexpected error occurred during fetch: {e}")
        print(traceback.format_exc())
        return None, None

    markdown_content = None
    image_url = None
    try:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the main content area of a Wikipedia page
        content_div = soup.find(id='mw-content-text')
        # Within that, find the primary parser output div
        main_body = content_div.find('div', class_='mw-parser-output') if content_div else None

        # Handle cases where the main content area isn't found (e.g., special pages, errors)
        if not main_body:
             print("Could not find main content area ('div.mw-parser-output'). Page might be structured differently.")
             # Check common indicators for disambiguation pages
             if soup.find(id='disambigbox') or soup.find(class_='disambiguation') or soup.find('a', title='Category:Disambiguation pages'):
                 print("This page appears to be a disambiguation page.")
             return None, None # Cannot extract standard content/image

        # --- Markdown Extraction ---
        # Create a deep copy for manipulation to avoid affecting the original tree used for image search
        main_body_for_markdown = BeautifulSoup(str(main_body), 'html.parser')

        # Define CSS selectors for elements to remove before markdown conversion
        elements_to_remove_selectors = [
            '.reflist', '.navbox', '.metadata', '.infobox', '.reference', '.mw-editsection',
            '.noprint', '.mw-references-wrap', '.references', '#toc', 'sup.reference',
            'span.mw-editsection', 'table.wikitable', '.sidebar', '.sistersitebox',
            '.portal', '.thumb', '.gallery', 'figure', '.IPA', '.rt-commented', '.mw-empty-elt',
            'div.thumb', 'table.sidebar', 'div.plainlist', 'div.hatnote', 'div.haudio',
            'span.anchor', 'span[id^="cite_ref"]', '.mw-kartographer-maplink', '.extiw',
            '.error', 'div.topicon', 'div.coordinates', 'div.printfooter', 'div#siteSub',
            'div#jump-to-nav', '.mw-jump-link', '.mw-cite-backlink', '.mwe-math-element', # Even more removals
            'noscript' # Remove noscript tags and their content
        ]
        # Iterate and remove selected elements
        for selector in elements_to_remove_selectors:
            tags = main_body_for_markdown.select(selector)
            for tag in tags:
                 if hasattr(tag, 'decompose'):
                     try: tag.decompose()
                     except Exception: pass # Fail silently if already removed

        # Explicitly remove style and script tags
        for tag in main_body_for_markdown.find_all(['style', 'script']):
             if hasattr(tag, 'decompose'): tag.decompose()

        # Remove paragraphs that are empty or contain only whitespace/nbsp
        for p in main_body_for_markdown.find_all('p'):
            text_content = p.get_text(strip=True).replace('&nbsp;', '').strip()
            if not text_content:
                 if hasattr(p, 'decompose'):
                    try: p.decompose()
                    except Exception: pass

        # Configure and run the HTML-to-Markdown converter
        h = html2text.HTML2Text()
        h.ignore_links = False       # Keep hyperlinks
        h.ignore_images = True       # We extract the main image separately
        h.body_width = 0             # Disable automatic line wrapping
        h.unicode_snob = True        # Use Unicode characters where appropriate
        h.escape_snob = True         # Avoid excessive escaping of characters like '*' or '_'
        h.skip_internal_links = True # Ignore links like '#Section'
        # Convert the cleaned HTML structure to Markdown
        markdown_content = h.handle(str(main_body_for_markdown))
        # Post-process: reduce multiple consecutive newlines to a maximum of two
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content).strip()

        # --- Image URL Extraction (use original main_body structure) ---
        # Strategy 1: Look for the primary image within the page's infobox
        infobox = main_body.find('table', class_='infobox')
        if infobox:
            # Often the main image is linked and has class 'image'
            infobox_image_link = infobox.find('a', class_='image')
            # Find the 'img' tag within the link or directly in the infobox
            image_tag = infobox_image_link.find('img') if infobox_image_link else infobox.find('img')
            if image_tag and image_tag.get('src'):
                src = image_tag.get('src')
                # Resolve protocol-relative or path-relative URLs to absolute HTTPS URLs
                if src.startswith('//'): image_url = 'https:' + src
                elif src.startswith('/'): image_url = 'https://en.wikipedia.org' + src
                elif src.startswith('http'): image_url = src # Already absolute

        # Strategy 2: If no infobox image, look for the first prominent thumbnail image
        if not image_url:
            # Thumbnails are usually within a 'thumbinner' div
            thumbinner = main_body.find('div', class_='thumbinner')
            if thumbinner:
                 image_tag = thumbinner.find('img')
                 if image_tag and image_tag.get('src'):
                     src = image_tag.get('src')
                     if src.startswith('//'): image_url = 'https:' + src
                     elif src.startswith('/'): image_url = 'https://en.wikipedia.org' + src
                     elif src.startswith('http'): image_url = src

        # Strategy 3: As a fallback, find the first reasonably sized image in the main content
        if not image_url:
             # Find the very first image tag in the parsed main body
             first_img_tag = main_body.find('img')
             if first_img_tag and first_img_tag.get('src'):
                  src = first_img_tag.get('src')
                  # Get dimensions if available, default to large values
                  width = first_img_tag.get('width', '999')
                  height = first_img_tag.get('height', '999')
                  src_lower = src.lower() # For case-insensitive checks
                  # Apply heuristics to avoid small icons, logos, interface elements
                  try:
                      # Check if dimensions are numeric and greater than a threshold (e.g., 50x50)
                      # Also check source URL for common indicator words
                      if (int(width) > 50 and int(height) > 50 and
                          'logo' not in src_lower and 'icon' not in src_lower and
                          'disambig' not in src_lower and 'speaker' not in src_lower and
                          'wikimedia' not in src_lower and 'wikisource' not in src_lower and
                          'wikibooks' not in src_lower and 'wikiquote' not in src_lower and
                          'wiktionary' not in src_lower and 'button' not in src_lower):
                           if src.startswith('//'): image_url = 'https:' + src
                           elif src.startswith('/'): image_url = 'https://en.wikipedia.org' + src
                           elif src.startswith('http'): image_url = src
                  except ValueError: # Handle cases where width/height aren't integers
                       # Apply same heuristic checks on src if dimensions invalid/missing
                       if ('logo' not in src_lower and 'icon' not in src_lower and
                           'disambig' not in src_lower and 'speaker' not in src_lower and
                           'wikimedia' not in src_lower and 'button' not in src_lower):
                            if src.startswith('//'): image_url = 'https:' + src
                            elif src.startswith('/'): image_url = 'https://en.wikipedia.org' + src
                            elif src.startswith('http'): image_url = src

        # --- Clean up image URL (attempt to convert thumbnail URL to original) ---
        if image_url and '/thumb/' in image_url:
            # Regex tries to match common Wikimedia thumbnail URL structure
            # Example: .../commons/thumb/a/ab/File.jpg/120px-File.jpg
            # We want: .../commons/a/ab/File.jpg
            match = re.match(r'(?P<base>https?://[^/]+/.*/commons)/thumb(?P<path>(?:/[^/]+){2})/(?:(?P<size>\d+px-)?)(?P<filename>.*)', image_url)
            if match:
                # Reconstruct URL using captured groups, excluding 'thumb' and size specifier
                cleaned_url = f"{match.group('base')}{match.group('path')}/{match.group('filename')}"
                print(f"Mapped thumbnail URL to potential original: {cleaned_url}")
                image_url = cleaned_url
            else:
                # Fallback method if regex doesn't match expected structure
                parts = image_url.split('/')
                try:
                    thumb_index = parts.index('thumb')
                    # Try to find the size specification part (e.g., '120px-...')
                    size_part_index = -1
                    for i in range(len(parts) - 1, thumb_index, -1):
                         if re.match(r'^\d+px-', parts[i]):
                             size_part_index = i
                             break
                    # If both 'thumb' and a size part were found in sequence
                    if size_part_index > thumb_index:
                         # Reconstruct: parts before 'thumb' + path parts between 'thumb' and size + filename parts after size
                         img_path_parts = parts[thumb_index+1:size_part_index]
                         filename_parts = parts[size_part_index+1:]
                         cleaned_url = '/'.join(parts[:thumb_index] + img_path_parts + filename_parts)
                         print(f"Mapped thumbnail URL to potential original (fallback): {cleaned_url}")
                         image_url = cleaned_url
                    else:
                         print(f"Could not apply fallback thumbnail cleaning (size spec not found): {image_url}")
                except ValueError:
                     # 'thumb' keyword wasn't found in the URL path components
                     print(f"Could not apply fallback thumbnail cleaning ('thumb' not found): {image_url}")

    except Exception as e:
        # Catch-all for errors during HTML processing or image/markdown extraction
        print(f"Error processing HTML content for '{query_word}': {e}")
        print(traceback.format_exc())
        # Return None for potentially corrupted data if processing failed midway

    # Return the extracted markdown content and image URL (which could be None)
    return markdown_content, image_url


# --- New Troubleshooting Function ---
def troubleshoot_wiki_result(query_word: str, test_description: str):
    """
    Calls fetch_wikipedia_data and prints formatted results for testing.

    Args:
        query_word: The word/phrase to fetch from Wikipedia.
        test_description: A string describing the test case.
    """
    print(f"\n\n--- Test Case: {test_description} ('{query_word}') ---")
    markdown, img_url = fetch_wikipedia_data(query_word)

    print("\n--- Results ---")
    if img_url:
        # Using emojis for fun visual cues! ✅
        print(f"✅ Image URL: {img_url}")
    else:
        page_exists_check = markdown is not None
        if page_exists_check:
             # Using emojis for fun visual cues! ❓
             print("❓ Image URL: Not Found on page (or failed extraction)")
        else:
             # Using emojis for fun visual cues! ❓
             print("❓ Image URL: Not Found (Page likely missing, disambiguation, or processing failed)")

    if markdown:
        # Using emojis for fun visual cues! ✅
        print(f"✅ Markdown Content (First 500 chars):\n{markdown[:500].strip()}...")
        # --- Optional File Saving ---
        # Uncomment the block below to save the full markdown content to a file
        # try:
        #     filename_base = query_word.replace(' ','_').replace('/','')
        #     safe_filename = re.sub(r'[^\w\-_\. ]', '_', filename_base) + "_wiki.md"
        #     with open(safe_filename, "w", encoding="utf-8") as f:
        #         f.write(markdown)
        #     # Using emojis for fun visual cues! 💾
        #     print(f"💾 Full markdown saved to {safe_filename}")
        # except IOError as e:
        #     # Using emojis for fun visual cues! 🚫
        #     print(f"🚫 Error saving markdown to file {safe_filename}: {e}")
        # except Exception as e_save:
        #     # Using emojis for fun visual cues! 🚫
        #     print(f"🚫 Unexpected error saving file {safe_filename}: {e_save}")
        # --- End Optional File Saving ---
    else:
        # Using emojis for fun visual cues! ❓
        print("❓ Markdown Content: Not Generated (See logs above for potential reasons)")

    # Print a separator line for better readability between test cases
    print("-" * (len(f"--- Test Case: {test_description} ('{query_word}') ---") -2 )) # Match separator length


# --- Main execution block (Refactored) ---
if __name__ == "__main__":
    # Define test cases as a list of tuples (query_word, description)
    test_cases = [
        ("shark", "Single simple word"),
        ("Great white shark", "Multi-word phrase"),
        #("Python", "Potential disambiguation/redirect"),
        ("Platypus", "Animal with standard page"),
        ("Zürich", "Name with non-ASCII character"),
        #("Sun", "Common noun / celestial body"),
        #("Mercury (planet)", "Page with parenthetical disambiguation"),
        ("Albert Einstein", "Person name"),
        #("Quantum mechanics", "Scientific concept"),
        #("Wikipedia", "Meta example"),
        #("This shouldn't exist", "Likely non-existent page (common placeholder)"),
        ("POLA", "Riccardo knows this to be a 403 redirect."),
        #("Apple", "Very common word with likely primary topic"),
        #("Apple Inc.", "Specific company page"),
        #("HTTP", "Acronym page") # Added acronym test
    ]

    # Iterate through the test cases and run the troubleshooting function
    print("Starting Wikipedia Fetcher Troubleshooting...")
    for word, description in test_cases:
        troubleshoot_wiki_result(word, description)

    print("\n\nTroubleshooting finished!")


