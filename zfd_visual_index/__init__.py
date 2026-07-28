"""Pixel native Stage B visual indexing with semantic authority held at zero."""

from .authority import (
    AuthorityMetadataReport,
    GraphemeAuthorityMetadataRecord,
    authority_record_receipt_sha256,
    pixel_occurrence_id,
    validate_grapheme_authority_metadata,
)
from .core import (
    DescriptorDistance,
    PageLocalVisualExemplar,
    PageLocalVisualIndexReceipt,
    PixelDescriptor,
    VisualIndexCandidate,
    VisualIndexConfig,
    VisualNeighbour,
    descriptor_distance,
    extract_pixel_descriptor,
    index_page_candidates,
    resolve_visual_index_output,
    validate_page_local_visual_index,
)
from .stage_a import (
    FrozenStageAPage,
    FrozenStageARun,
    open_frozen_stage_a_run,
    validate_stage_a_geometry_graph,
)


__all__ = [
    "AuthorityMetadataReport",
    "DescriptorDistance",
    "FrozenStageAPage",
    "FrozenStageARun",
    "GraphemeAuthorityMetadataRecord",
    "PageLocalVisualExemplar",
    "PageLocalVisualIndexReceipt",
    "PixelDescriptor",
    "VisualIndexCandidate",
    "VisualIndexConfig",
    "VisualNeighbour",
    "authority_record_receipt_sha256",
    "descriptor_distance",
    "extract_pixel_descriptor",
    "index_page_candidates",
    "open_frozen_stage_a_run",
    "pixel_occurrence_id",
    "resolve_visual_index_output",
    "validate_grapheme_authority_metadata",
    "validate_page_local_visual_index",
    "validate_stage_a_geometry_graph",
]

__version__ = "0.1.0"
