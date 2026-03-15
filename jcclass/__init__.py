from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("jcclass")
except PackageNotFoundError:
    __version__ = "unknown"

from .compute import compute_cts, eleven_cts
from .plotting import plot_cts

__all__ = ["compute_cts", "eleven_cts", "plot_cts"]
