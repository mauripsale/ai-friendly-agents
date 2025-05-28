# ricclib/markdown_utils.py
import re
from typing import List

def demote_markdown_headers(markdown_content: str) -> str:
    """
    Demotes all Markdown headers within a string by one level.
    For example, '# Title' becomes '## Title', and '## Subtitle' becomes '### Subtitle'.
    This prevents H1 headers from individual files clashing with the
    main '# [File X] filename' headers in the consolidated output.
    """
    lines: List[str] = markdown_content.splitlines()
    processed_lines: List[str] = []
    for line in lines:
        match = re.match(r"^(#+)\s+(.*)", line)
        if match:
            hashes = match.group(1)
            title_text = match.group(2)
            # Add one more '#' to demote the header.
            # Max markdown header level is typically H6, but for this purpose,
            # just adding one '#' is sufficient to ensure it's not an H1.
            demoted_header = f"#{hashes} {title_text}"
            processed_lines.append(demoted_header)
        else:
            processed_lines.append(line)
    return "\n".join(processed_lines)

if __name__ == '__main__':
    print("🧪 Testing markdown_utils.py...")
    test_md_content = """# Original H1
Some text.
## Original H2
# Another Original H1
No leading space should not be a header.
#Also not a header
   # Indented H1, also not a header by strict markdown, but good to test
###### H6 Header
"""
    expected_output = """## Original H1
Some text.
### Original H2
## Another Original H1
No leading space should not be a header.
#Also not a header
   # Indented H1, also not a header by strict markdown, but good to test
####### H6 Header""" # Note: H6 becomes H7 essentially.
    
    demoted = demote_markdown_headers(test_md_content)
    print("\nOriginal Markdown:")
    print(test_md_content)
    print("\nDemoted Markdown:")
    print(demoted)

    assert demote_markdown_headers("# Title") == "## Title"
    assert demote_markdown_headers("## Subtitle") == "### Subtitle"
    assert demote_markdown_headers("Not a header") == "Not a header"
    assert demote_markdown_headers("  # Not a header (leading space)") == "  # Not a header (leading space)"
    print("✅ markdown_utils.py basic tests passed! Headers demoted as expected.")
