import sys
from typing import ContextManager, Optional, TextIO

from prompt_toolkit.utils import is_windows

from .base import DummyInput, Input, PipeInput

__all__ = [
    "create_input",
    "create_pipe_input",
]


def create_input(
    stdin: Optional[TextIO] = None, always_prefer_tty: bool = False
) -> Input:
    """
    Create the appropriate `Input` object for the current os/environment.

    :param always_prefer_tty: When set, if `sys.stdin` is connected to a Unix
        `pipe`, check whether `sys.stdout` or `sys.stderr` are connected to a
        pseudo terminal. If so, open the tty for reading instead of reading for
        `sys.stdin`. (We can open `stdout` or `stderr` for reading, this is how
        a `$PAGER` works.)
    """
    if is_windows():
        from .win32 import Win32Input

        # If `stdin` was assigned `None` (which happens with pythonw.exe), use
        # a `DummyInput`. This triggers `EOFError` in the application code.
        if stdin is None and sys.stdin is None:
            return DummyInput()

        return Win32Input(stdin or sys.stdin)
    else:
        from .vt100 import Vt100Input

        # If no input TextIO is given, use stdin/stdout.
        if stdin is None:
            stdin = sys.stdin

            if always_prefer_tty:
                for io in [sys.stdin, sys.stdout, sys.stderr]:
                    if io.isatty():
                        stdin = io
                        break

        return Vt100Input(stdin)


def create_pipe_input() -> ContextManager[PipeInput]:
    """
    Create an input pipe.
    This is mostly useful for unit testing.

    Usage::

        with create_pipe_input() as input:
            input.send_text('inputdata')

    Breaking change: In prompt_toolkit 3.0.28 and earlier, this was returning
    the `PipeInput` directly, rather than through a context manager.
    """
    if is_windows():
        from .win32_pipe import Win32PipeInput

        return Win32PipeInput.create()
    else:
        from .posix_pipe import PosixPipeInput

        return PosixPipeInput.create()
