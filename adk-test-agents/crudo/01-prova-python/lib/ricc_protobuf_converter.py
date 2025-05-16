
from typing import Callable, List, Dict, Any, Optional # ,
from google.protobuf.json_format import MessageToDict
from google.cloud import run_v2, logging_v2
from pathlib import Path, PosixPath

# todo ricc move to its own file
class ProtobufConverter:
    """
    Handles conversion of known Protobuf types to dictionaries.

    Solves errors like this:


    🚨 [main] A critical error occurred: Object of type RevisionTemplate is not JSON serializable
    Traceback (most recent call last):
    File "/usr/local/google/home/ricc/git/blahblahpoo/20250401-l300/01-prova-python/main.py", line 151, in main
        chat_session.send_simple_message(line)
    File "/usr/local/google/home/ricc/git/blahblahpoo/20250401-l300/01-prova-python/lib/ricc_genai.py", line 267, in send_simple_message
        response = self.chat.send_message(  # Use self.chat here
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/usr/local/google/home/ricc/git/blahblahpoo/20250401-l300/01-prova-python/.venv/lib/python3.12/site-packages/google/genai/chats.py", line 258, in send_message
        response = self._modules.generate_content(
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/usr/local/google/home/ricc/git/blahblahpoo/20250401-l300/01-prova-python/.venv/lib/python3.12/site-packages/google/genai/models.py", line 4942, in generate_content
        response = self._generate_content(
                ^^^^^^^^^^^^^^^^^^^^^^^
    File "/usr/local/google/home/ricc/git/blahblahpoo/20250401-l300/01-prova-python/.venv/lib/python3.12/site-packages/google/genai/models.py", line 3915, in _generate_content
        response_dict = self._api_client.request(
                        ^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/usr/local/google/home/ricc/git/blahblahpoo/20250401-l300/01-prova-python/.venv/lib/python3.12/site-packages/google/genai/_api_client.py", line 655, in request
        response = self._request(http_request, stream=False)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/usr/local/google/home/ricc/git/blahblahpoo/20250401-l300/01-prova-python/.venv/lib/python3.12/site-packages/google/genai/_api_client.py", line 555, in _request
        data = json.dumps(http_request.data) if http_request.data else None
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/usr/local/google/home/ricc/miniconda3/lib/python3.12/json/__init__.py", line 231, in dumps
        return _default_encoder.encode(obj)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/usr/local/google/home/ricc/miniconda3/lib/python3.12/json/encoder.py", line 200, in encode
        chunks = self.iterencode(o, _one_shot=True)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/usr/local/google/home/ricc/miniconda3/lib/python3.12/json/encoder.py", line 258, in iterencode
        return _iterencode(o, 0)
            ^^^^^^^^^^^^^^^^^
    File "/usr/local/google/home/ricc/miniconda3/lib/python3.12/json/encoder.py", line 180, in default
        raise TypeError(f'Object of type {o.__class__.__name__} '
    TypeError: Object of type RevisionTemplate is not JSON serializable

    """
    def __init__(self):
        self.converters: Dict[type, Callable[[Any], Dict]] = {}
        self.register_default_converters()

    def register_default_converters(self):
        """Registers default converters for known types."""
        self.register_converter(run_v2.Service, lambda obj: MessageToDict(obj._pb))
        self.register_converter(run_v2.RevisionTemplate, lambda obj: MessageToDict(obj._pb))
        #self.register_converter(PosixPath, lambda obj: MessageToDict(obj._pb))
        # NO! ENsure Path is transformed into a STRING you fool! :)
        # self.register_converter(PosixPath, lambda obj: str(obj))
        # https://github.com/pydantic/pydantic/discussions/10235


    def register_converter(self, proto_type: type, converter: Callable[[Any], Dict]):
        """Registers a converter for a specific Protobuf type."""
        self.converters[proto_type] = converter

    def convert(self, obj: Any) -> Optional[Dict]:
        """Converts a Protobuf object to a dictionary if a converter is registered."""
        converter = self.converters.get(type(obj))
        if converter:
            return converter(obj)
        return None


PROTOBUF_CONVERTER = ProtobufConverter()
