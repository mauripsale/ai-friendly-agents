import subprocess
import logging
import sys
from jinja2 import Template


def generate_readme():
    """
    Generates the README.md file by:
    1. Executing the 'just -l' command.
    2. Capturing its output.
    3. Using Jinja2 to render a template, injecting the captured output.
    4. Writing the final content to 'README.md'.

    NOTE: using `README.tpl` as the base template.
    """

    logging.basicConfig(level=logging.ERROR)

    try:
        just_l_output = subprocess.check_output(['just', '-l'], text=True)
    except FileNotFoundError:
        just_l_output = "Error: 'just' command not found. Please ensure it's installed and in your PATH."
        logging.error(just_l_output)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        just_l_output = f"Error running 'just -l': {e.output}"
        logging.error(f"Error executing command: {e}")
        sys.exit(1)
    except Exception as e:
        just_l_output = f"An unexpected error occurred: {e}"
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


    # Create a Jinja2 Template object from the defined string content.
    with open('./README.tpl') as fh:
        template = Template(fh.read())

    rendered_readme = template.render(just_l_output=just_l_output)

    with open('README.md', 'w') as f:
        f.write(rendered_readme)

    logging.info("README.md generated successfully!")

if __name__ == "__main__":
    # Ensure this function is called only when the script is executed directly.
    generate_readme()

