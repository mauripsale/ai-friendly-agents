
from google.adk.agents import Agent

import requests
from bs4 import BeautifulSoup
import html2text
from typing import Dict, Any, Optional # Updated import
import urllib.parse
import re
import traceback

# Corrected type hint: Dict[str, Any]
def tool_fetch_wikipedia_data(query_word: str, language: str = 'en', cache_locally: bool = True) -> Dict[str, Any]:
    """
    Fetches a Wikipedia page, converts its main content to Markdown,
    and finds the primary image URL.

    Args:
        query_word: The word or phrase to search for on Wikipedia (e.g., "shark").
        language: The language code for the Wikipedia page (default: 'en').
                  Supported codes include 'en', 'de', 'fr', 'es', 'it', 'ja', 'pt'.
        cache_locally: caches images and text on local files under
                  .cache/wikipedia_pages/NAME.md and
                  .cache/wikipedia_pages/NAME.png (or whatever extension it has)


    Returns:
        A dictionary containing:
        - 'status': 'success' or 'error'.
        - 'result': (dict, optional) Present on success, contains:
            - 'markdown_content': The Markdown content (str) or None.
            - 'image_url': The primary image URL (str) or None.
        - 'error_message': (str, optional) Present on error, describes the issue.
    """
    if not query_word:
        print("Error: Query word cannot be empty.")
        return {"status": "error", "error_message": "Query word cannot be empty."}

    if cache_locally:
        print("⏹️TODO⏹️: Riccardo implement this another day. Time to go home to your kids. Ask Gemini to implement it for you. Also add cached_files to return: cached_files: {img: ..., md: ...}")

    supported_languages = ['en', 'de', 'fr', 'es', 'it', 'ja', 'pt']
    if language not in supported_languages:
        print(f"Error: Unsupported language '{language}'. Using 'en'.")
        # Defaulting to 'en' might be better than erroring out, depending on desired behavior.
        # Alternatively, return an error:
        # return {"status": "error", "error_message": f"Unsupported language: {language}. Supported: {supported_languages}"}
        language = 'en' # Defaulting for this example

    formatted_query = query_word[0].upper() + query_word[1:]
    formatted_query = formatted_query.replace(" ", "_")
    # Ensure safe URL encoding for the path component
    wiki_url = f"https://{language}.wikipedia.org/wiki/{urllib.parse.quote(formatted_query)}"
    print(f"Attempting to fetch: {wiki_url} in language '{language}'")

    try:
        headers = {'User-Agent': 'MyWikiFetcherScript/1.2 (Python)'} # Incremented version
        response = requests.get(wiki_url, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error fetching URL {wiki_url}: {e}"
        print(error_msg)
        if e.response.status_code == 404:
            error_msg = f"Page not found for '{query_word}' in language '{language}' ({wiki_url}). Check spelling or if the page exists."
            print(f"-> Specific 404 error: {error_msg}")
        return {"status": "error", "error_message": error_msg}
    except requests.exceptions.RequestException as e:
        error_msg = f"Request Error fetching URL {wiki_url}: {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}
    except Exception as e:
        error_msg = f"An unexpected error occurred during fetch: {e}"
        print(error_msg)
        print(traceback.format_exc())
        return {"status": "error", "error_message": error_msg}

    markdown_content = None
    image_url = None
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        content_div = soup.find(id='mw-content-text')
        main_body = content_div.find('div', class_='mw-parser-output') if content_div else None

        if not main_body:
            error_msg = "Could not find main content area ('div.mw-parser-output'). Page might be structured differently or is not a standard article."
            print(error_msg)
            if soup.find(id='disambigbox') or soup.find(class_='disambiguation') or soup.find('a', title='Category:Disambiguation pages'):
                disambiguation_msg = " This page appears to be a disambiguation page."
                print(disambiguation_msg)
                error_msg += disambiguation_msg
            return {"status": "error", "error_message": error_msg}

        # --- Markdown Extraction ---
        main_body_for_markdown = BeautifulSoup(str(main_body), 'html.parser')
        elements_to_remove_selectors = [
            '.reflist', '.navbox', '.metadata', '.infobox', '.reference', '.mw-editsection',
            '.noprint', '.mw-references-wrap', '.references', '#toc', 'sup.reference',
            'span.mw-editsection', 'table.wikitable', '.sidebar', '.sistersitebox',
            '.portal', '.thumb', '.gallery', 'figure', '.IPA', '.rt-commented', '.mw-empty-elt',
            'div.thumb', 'table.sidebar', 'div.plainlist', 'div.hatnote', 'div.haudio',
            'span.anchor', 'span[id^="cite_ref"]', '.mw-kartographer-maplink', '.extiw',
            '.error', 'div.topicon', 'div.coordinates', 'div.printfooter', 'div#siteSub',
            'div#jump-to-nav', '.mw-jump-link', '.mw-cite-backlink', '.mwe-math-element',
            'noscript', 'style', 'script'
        ]
        for selector in elements_to_remove_selectors:
            tags = main_body_for_markdown.select(selector)
            for tag in tags:
                if hasattr(tag, 'decompose'):
                    try: tag.decompose()
                    except Exception: pass
        for p in main_body_for_markdown.find_all('p'):
            text_content = p.get_text(strip=True).replace('&nbsp;', '').strip()
            if not text_content:
                if hasattr(p, 'decompose'):
                    try: p.decompose()
                    except Exception: pass

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0
        h.unicode_snob = True
        h.escape_snob = True
        h.skip_internal_links = True
        markdown_content = h.handle(str(main_body_for_markdown))
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content).strip()

        # --- Image URL Extraction ---
        infobox = main_body.find('table', class_='infobox')
        if infobox:
            infobox_image_link = infobox.find('a', class_='image')
            image_tag = infobox_image_link.find('img') if infobox_image_link else infobox.find('img')
            if image_tag and image_tag.get('src'):
                src = image_tag.get('src')
                if src.startswith('//'): image_url = 'https:' + src
                elif src.startswith('/'): image_url = f'https://{language}.wikipedia.org' + src # Use correct language domain
                elif src.startswith('http'): image_url = src

        if not image_url:
            thumbinner = main_body.find('div', class_='thumbinner')
            if thumbinner:
                image_tag = thumbinner.find('img')
                if image_tag and image_tag.get('src'):
                    src = image_tag.get('src')
                    if src.startswith('//'): image_url = 'https:' + src
                    elif src.startswith('/'): image_url = f'https://{language}.wikipedia.org' + src
                    elif src.startswith('http'): image_url = src

        if not image_url:
            first_img_tag = main_body.find('img')
            if first_img_tag and first_img_tag.get('src'):
                src = first_img_tag.get('src')
                width = first_img_tag.get('width', '999')
                height = first_img_tag.get('height', '999')
                src_lower = src.lower()
                try:
                    is_large_enough = int(width) > 50 and int(height) > 50
                except ValueError:
                    is_large_enough = True # Assume large enough if dimensions aren't parseable ints

                is_likely_icon = any(keyword in src_lower for keyword in [
                    'logo', 'icon', 'disambig', 'speaker', 'wikimedia', 'wikisource',
                    'wikibooks', 'wikiquote', 'wiktionary', 'button', 'svg' # Added svg
                ])

                if is_large_enough and not is_likely_icon:
                    if src.startswith('//'): image_url = 'https:' + src
                    elif src.startswith('/'): image_url = f'https://{language}.wikipedia.org' + src
                    elif src.startswith('http'): image_url = src

        # --- Clean up image URL ---
        if image_url and '/thumb/' in image_url:
            match = re.match(r'(?P<base>https?://[^/]+/.*/commons)/thumb(?P<path>(?:/[^/]+){2})/(?:(?P<size>\d+px-)?)(?P<filename>.*)', image_url)
            if match:
                cleaned_url = f"{match.group('base')}{match.group('path')}/{match.group('filename')}"
                print(f"Mapped thumbnail URL to potential original: {cleaned_url}")
                image_url = cleaned_url
            else:
                parts = image_url.split('/')
                try:
                    thumb_index = parts.index('thumb')
                    size_part_index = -1
                    for i in range(len(parts) - 1, thumb_index, -1):
                        if re.match(r'^\d+px-', parts[i]):
                            size_part_index = i
                            break
                    if size_part_index > thumb_index:
                        img_path_parts = parts[thumb_index+1:size_part_index]
                        filename_parts = parts[size_part_index+1:]
                        cleaned_url = '/'.join(parts[:thumb_index] + img_path_parts + filename_parts)
                        print(f"Mapped thumbnail URL to potential original (fallback): {cleaned_url}")
                        image_url = cleaned_url
                    else:
                        print(f"Could not apply fallback thumbnail cleaning (size spec not found): {image_url}")
                except ValueError:
                    print(f"Could not apply fallback thumbnail cleaning ('thumb' not found): {image_url}")

    except Exception as e:
        error_msg = f"Error processing HTML content for '{query_word}': {e}"
        print(error_msg)
        print(traceback.format_exc())
        # Return error, but include any markdown that might have been generated before the error
        return {
            "status": "error",
            "error_message": error_msg,
            "partial_result": { # Include partial data if available
                 "markdown_content": markdown_content,
                 "image_url": None # Image URL likely failed if we are here
            } if markdown_content else None
        }

    # Return success dictionary
    return {
        "status": "success",
        "result": {
            "markdown_content": markdown_content,
            "image_url": image_url,
            # "cached_files": {
            #     "image": None, # coming soon
            #     "markdown": None # coming soon
            # }
        }
    }

# The rest of the agent definition remains the same
root_agent = Agent(
    name="Vicky__WikipediaSearchAgent",
    model="gemini-2.0-flash",
    description=(
        "Agent to fetch wikipedia pages and answer questions about them."
    ),
    instruction=(
        "You are a helpful agent who can fetch Wikipedia pages, and extract import info from them."
        " Use this emoji '🇼' when expressing a word, say you searched for Shark, then say '🇼 Shark'."
        " When asked about the page in another language for a word, understand that the user might want you to translate it to the other language first."
        # https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Corl0207_%2828225976491%29.jpg/330px-Corl0207_%2828225976491%29.jpg
    ),
    tools=[tool_fetch_wikipedia_data],
)
