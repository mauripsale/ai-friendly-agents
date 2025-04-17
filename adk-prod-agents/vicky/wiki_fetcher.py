import requests
from bs4 import BeautifulSoup
import html2text
from typing import Tuple, Optional
import urllib.parse
import re # Import regex for more robust image URL cleaning

def fetch_wikipedia_data(query_word: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches a Wikipedia page, converts its main content to Markdown,
    and finds the primary image URL.

    Args:
        query_word: The word or phrase to search for on Wikipedia (e.g., "shark").

    Returns:
        A tuple containing:
        - The Markdown content of the main article body (str) or None if failed.
        - The URL of the primary image (str) or None if not found or failed.
    """
    # Construct the URL (handle spaces -> underscores, proper URL encoding, capitalize first letter)
    # Capitalize only the first letter, keep the rest as is, replace space with underscore
    if not query_word:
        print("Error: Query word cannot be empty.")
        return None, None
    formatted_query = query_word[0].upper() + query_word[1:]
    formatted_query = formatted_query.replace(" ", "_")
    # Use urllib.parse.quote to handle special characters safely in the URL path
    wiki_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(formatted_query)}"
    print(f"🤖 Attempting to fetch: {wiki_url}")

    try:
        # Setting a User-Agent is good practice!
        headers = {'User-Agent': 'MyCoolWikiFetcher/1.0 (https://example.com/bot; myemail@example.com)'}
        response = requests.get(wiki_url, headers=headers, timeout=10) # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"😭 Error fetching URL {wiki_url}: {e}")
        return None, None
    except Exception as e:
        print(f"😱 An unexpected error occurred during fetch: {e}")
        return None, None

    try:
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Extract Markdown ---
        content_div = soup.find(id='mw-content-text')
        markdown_content = None
        if content_div:
            main_body = content_div.find('div', class_='mw-parser-output')
            if main_body:
                # Make a copy for markdown processing so image search isn't affected
                main_body_for_markdown = BeautifulSoup(str(main_body), 'html.parser')

                # Remove elements we don't want in Markdown
                elements_to_remove = main_body_for_markdown.find_all(
                    ['div', 'table', 'span', 'sup'],
                    class_=['reflist', 'navbox', 'metadata', 'infobox', 'reference', 'mw-editsection']
                )
                # Also remove tables of contents, reference sections by id/class potentially
                toc = main_body_for_markdown.find(id='toc')
                if toc:
                    elements_to_remove.append(toc)

                for tag in elements_to_remove:
                     tag.decompose() # Remove the tag and its content

                # Remove empty paragraphs that might remain after decompositions
                for p in main_body_for_markdown.find_all('p'):
                    if not p.get_text(strip=True):
                        p.decompose()

                h = html2text.HTML2Text()
                h.ignore_links = False # Keep links
                h.ignore_images = True # Ignore images in markdown text, we return the main one separately
                h.body_width = 0 # Don't wrap lines automatically
                markdown_content = h.handle(str(main_body_for_markdown))
            else:
                print("🤔 Could not find main parser output div ('div.mw-parser-output').")
        else:
            print("🤯 Could not find main content div ('#mw-content-text').")


        # --- Find Image URL ---
        # Use the original main_body for image search
        image_url = None
        if main_body: # Check if main_body was found earlier
             # Strategy 1: Look inside the infobox first
            infobox = main_body.find('table', class_='infobox')
            if infobox:
                image_tag = infobox.find('img')
                if image_tag and image_tag.get('src'):
                    src = image_tag['src']
                    # Ensure the URL is absolute
                    if src.startswith('//'):
                        image_url = 'https:' + src
                    elif src.startswith('/'):
                         # This case is less common on Wikipedia itself but good practice
                         image_url = 'https://en.wikipedia.org' + src
                    elif src.startswith('http'):
                         image_url = src # Already absolute
                    else:
                         # Relative path, might happen in rare cases or broken HTML
                         print(f"⚠️ Found potentially relative image path in infobox: {src}")


            # Strategy 2: If no image in infobox, find the first thumbnail image in the main content body
            if not image_url:
                # Look for standard thumbnail images (often in <div class="thumb">)
                thumbinner = main_body.find('div', class_='thumbinner') # thumbinner usually contains the img
                if thumbinner:
                     image_tag = thumbinner.find('img')
                     if image_tag and image_tag.get('src'):
                         src = image_tag['src']
                         if src.startswith('//'):
                            image_url = 'https:' + src
                         elif src.startswith('/'):
                            image_url = 'https://en.wikipedia.org' + src
                         elif src.startswith('http'):
                            image_url = src


        # --- Clean up image URL ---
        # Try to get the original image URL from a thumbnail URL
        # Example: //upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Example.jpg/220px-Example.jpg
        # We want: //upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg
        if image_url and '/thumb/' in image_url:
            # Use regex to remove the /thumb/ part and the size specification like /220px-
            # This captures the path before /thumb/, the path after /thumb/ but before the size spec,
            # and the filename after the size spec.
            match = re.match(r'(.*)/thumb(/.*?/.*?)/(\d+px-.*)', image_url)
            if match:
                # If the typical thumbnail structure is matched, reconstruct without '/thumb/' and size spec
                base_path = match.group(1)
                image_path = match.group(2)
                image_url = base_path + image_path
                print(f" Mapped thumbnail URL to potential original: {image_url}")
            else:
                 # Simpler fallback: Find the last '/...px-' part and remove it
                 parts = image_url.split('/')
                 filename_part_index = -1
                 for i, part in enumerate(reversed(parts)):
                     if re.match(r'^\d+px-', part):
                          filename_part_index = len(parts) - 1 - i
                          break
                 if filename_part_index > 0 and filename_part_index < len(parts) -1 :
                     # Remove the '/thumb/' part and the size spec part
                     image_url = '/'.join(parts[:filename_part_index-1] + parts[filename_part_index+1:])
                     print(f" Mapped thumbnail URL to potential original (fallback): {image_url}")


    except Exception as e:
        print(f"😵‍💫 Error processing HTML content: {e}")
        # Return whatever markdown might have been generated before the error
        return markdown_content, None # Return None for image URL if processing failed


    return markdown_content, image_url

# Example Usage
if __name__ == "__main__":
    # Simple word example
    word = "shark"
    print(f"\n--- Fetching data for '{word}' ---")
    markdown, img_url = fetch_wikipedia_data(word)

    if markdown or img_url:
        print("\n✅ Success!")
        if img_url:
             print("\n--- Primary Image URL ---")
             print(img_url)
        else:
             print("\n--- Primary Image URL ---")
             print("❓ Could not find a suitable image.")

        if markdown:
             print("\n--- Markdown Content (first 500 chars) ---")
             print(markdown[:500].strip() + "...")
             # Optionally save to file
             # try:
             #     filename = f"{word.replace(' ','_')}_wiki.md"
             #     with open(filename, "w", encoding="utf-8") as f:
             #         f.write(markdown)
             #     print(f"\n💾 Full markdown saved to {filename}")
             # except IOError as e:
             #     print(f"\n🚫 Error saving markdown to file: {e}")
        else:
             print("\n--- Markdown Content ---")
             print("❓ Could not generate markdown content.")

    else:
        print(f"\n❌ Failed to retrieve any data for '{word}'.")

    # Example with a multi-word query that might exist
    word_multi = "Great white shark"
    print(f"\n\n--- Fetching data for '{word_multi}' ---")
    markdown_multi, img_url_multi = fetch_wikipedia_data(word_multi)

    if markdown_multi or img_url_multi:
        print("\n✅ Success!")
        if img_url_multi:
             print("\n--- Primary Image URL ---")
             print(img_url_multi)
        else:
             print("\n--- Primary Image URL ---")
             print("❓ Could not find a suitable image.")

        if markdown_multi:
             print("\n--- Markdown Content (first 500 chars) ---")
             print(markdown_multi[:500].strip() + "...")
        else:
             print("\n--- Markdown Content ---")
             print("❓ Could not generate markdown content.")
    else:
        print(f"\n❌ Failed to retrieve any data for '{word_multi}'.")

    # Example for a word that might not have a direct page (or needs disambiguation)
    word_fail = "Schnitzelwurst" # Probably doesn't exist
    print(f"\n\n--- Fetching data for '{word_fail}' ---")
    markdown_fail, img_url_fail = fetch_wikipedia_data(word_fail)
    if not markdown_fail and not img_url_fail:
        print("\n✅ Script handled non-existent page gracefully (as expected).")
    else:
        print("\n🤔 Unexpectedly got some data for a likely non-existent page.")

