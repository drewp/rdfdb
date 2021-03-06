# Stubs for autobahn.websocket.compress_deflate (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from autobahn.websocket.compress_base import PerMessageCompress, PerMessageCompressOffer, PerMessageCompressOfferAccept, PerMessageCompressResponse, PerMessageCompressResponseAccept
from typing import Any, Optional

class PerMessageDeflateMixin:
    EXTENSION_NAME: str = ...
    WINDOW_SIZE_PERMISSIBLE_VALUES: Any = ...
    MEM_LEVEL_PERMISSIBLE_VALUES: Any = ...

class PerMessageDeflateOffer(PerMessageCompressOffer, PerMessageDeflateMixin):
    @classmethod
    def parse(cls, params: Any): ...
    accept_no_context_takeover: Any = ...
    accept_max_window_bits: Any = ...
    request_no_context_takeover: Any = ...
    request_max_window_bits: Any = ...
    def __init__(self, accept_no_context_takeover: bool = ..., accept_max_window_bits: bool = ..., request_no_context_takeover: bool = ..., request_max_window_bits: int = ...) -> None: ...
    def get_extension_string(self): ...
    def __json__(self): ...

class PerMessageDeflateOfferAccept(PerMessageCompressOfferAccept, PerMessageDeflateMixin):
    offer: Any = ...
    request_no_context_takeover: Any = ...
    request_max_window_bits: Any = ...
    no_context_takeover: Any = ...
    window_bits: Any = ...
    mem_level: Any = ...
    max_message_size: Any = ...
    def __init__(self, offer: Any, request_no_context_takeover: bool = ..., request_max_window_bits: int = ..., no_context_takeover: Optional[Any] = ..., window_bits: Optional[Any] = ..., mem_level: Optional[Any] = ..., max_message_size: Optional[Any] = ...) -> None: ...
    def get_extension_string(self): ...
    def __json__(self): ...

class PerMessageDeflateResponse(PerMessageCompressResponse, PerMessageDeflateMixin):
    @classmethod
    def parse(cls, params: Any): ...
    client_max_window_bits: Any = ...
    client_no_context_takeover: Any = ...
    server_max_window_bits: Any = ...
    server_no_context_takeover: Any = ...
    def __init__(self, client_max_window_bits: Any, client_no_context_takeover: Any, server_max_window_bits: Any, server_no_context_takeover: Any) -> None: ...
    def __json__(self): ...

class PerMessageDeflateResponseAccept(PerMessageCompressResponseAccept, PerMessageDeflateMixin):
    response: Any = ...
    no_context_takeover: Any = ...
    window_bits: Any = ...
    mem_level: Any = ...
    max_message_size: Any = ...
    def __init__(self, response: Any, no_context_takeover: Optional[Any] = ..., window_bits: Optional[Any] = ..., mem_level: Optional[Any] = ..., max_message_size: Optional[Any] = ...) -> None: ...
    def __json__(self): ...

class PerMessageDeflate(PerMessageCompress, PerMessageDeflateMixin):
    DEFAULT_WINDOW_BITS: Any = ...
    DEFAULT_MEM_LEVEL: int = ...
    @classmethod
    def create_from_response_accept(cls, is_server: Any, accept: Any): ...
    @classmethod
    def create_from_offer_accept(cls, is_server: Any, accept: Any): ...
    server_no_context_takeover: Any = ...
    client_no_context_takeover: Any = ...
    server_max_window_bits: Any = ...
    client_max_window_bits: Any = ...
    mem_level: Any = ...
    max_message_size: Any = ...
    def __init__(self, is_server: Any, server_no_context_takeover: Any, client_no_context_takeover: Any, server_max_window_bits: Any, client_max_window_bits: Any, mem_level: Any, max_message_size: Optional[Any] = ...) -> None: ...
    def __json__(self): ...
    def start_compress_message(self) -> None: ...
    def compress_message_data(self, data: Any): ...
    def end_compress_message(self): ...
    def start_decompress_message(self) -> None: ...
    def decompress_message_data(self, data: Any): ...
    def end_decompress_message(self) -> None: ...
