"""LGN-Eye: Software replication of lateral geniculate nucleus temporal attention.

Based on Gao et al. (2026) "Ultrafast visual perception beyond human capabilities
enabled by motion analysis using synaptic transistors" (Nature Communications).
"""

__version__ = "0.1.0"

from lgn_eye.config import LGNConfig
from lgn_eye.pipeline import LGNPipeline

__all__ = ["LGNConfig", "LGNPipeline", "__version__"]
