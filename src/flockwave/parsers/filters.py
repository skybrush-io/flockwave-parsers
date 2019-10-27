"""Pre- and post-filters that can be used to construct a parser that
automatically rejects certain messages.
"""

from .types import Filter

__all__ = ("reject_shorter_than",)


def reject_shorter_than(min_length: int) -> Filter[bytes]:
    """Returns a pre-filter that can be used to reject messages shorter than
    a certain length.
    """

    def filter(data: bytes) -> bool:
        return len(data) >= min_length

    return filter
