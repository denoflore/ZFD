"""Immutable records shared across the image native evidence lane."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PageRecord:
    page_id: str
    source_id: str
    surface_label: str
    iiif_id: str
    iiif_base_uri: str
    image_request_uri: str
    image_sha256: str | None = None
    image_path: str | None = None
    width: int | None = None
    height: int | None = None
    mime_type: str | None = None
    acquisition_status: str = "not_acquired"


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source_label: str
    title: str
    stable_locator: str
    date_kind: str
    date_basis: str
    dating_authority: str
    dating_authority_locator: str
    dating_certainty: str
    material_date_start: int | None
    material_date_end: int | None
    writing_date_start: int | None
    writing_date_end: int | None
    text_date_start: int | None
    text_date_end: int | None
    copy_date_start: int | None
    copy_date_end: int | None
    publication_date_start: int | None
    publication_date_end: int | None
    institution: str
    shelfmark: str
    language: str
    script: str
    hand_style: str
    genre: str
    region: str
    source_type: str
    evidentiary_role: str
    training_use: str
    rights_statement: str
    rights_locator: str
    rights_status: str
    identity_status: str
    manifest_sha256: str | None
    asset_mapping_sha256: str | None
    page_mapping_sha256: str | None
    lineage_sha256: str | None
    control_group: str
    hand_boundary_sha256: str | None = None
    line_annotation_sha256: str | None = None
    split_lineage_sha256: str | None = None


@dataclass(frozen=True)
class SplitAsset:
    asset_id: str
    parent_asset_id: str
    lineage_root_id: str
    sha256: str
    perceptual_hash: str
    manuscript_id: str
    hand_id: str
    style: str
    split: str


@dataclass(frozen=True)
class TerminologyRecord:
    term_id: str
    ocr_id: str
    observed_form: str | None
    expanded_form: str | None
    normalized_historical_form: str | None
    reconstructed_form: str | None
    latin_parallel: str | None
    modern_croatian: str | None
    literal_english: str | None
    fluent_english: str | None
    source_id: str | None
    witness_date_kind: str | None
    witness_date_start: int | None
    witness_date_end: int | None
    witness_language: str | None
    witness_script: str | None
    witness_domain: str | None
    passage_locator: str | None
    stable_locator: str | None
    source_sha256: str | None
    passage_asset_id: str | None
    passage_asset_sha256: str | None
    passage_image_id: str | None
    passage_image_sha256: str | None
    diplomatic_passage: str | None
    reviewer_id: str | None
    adjudicator_id: str | None
    review_state: str
    alternatives: tuple[str, ...]
    confidence: float | None
    confidence_basis: str | None
    speculation: bool


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    record_id: str | None = None
    detail: dict[str, Any] | None = None


@dataclass(frozen=True)
class ValidationReport:
    errors: tuple[ValidationIssue, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors
