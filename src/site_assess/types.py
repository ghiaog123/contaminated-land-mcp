"""Shared data contract. Mirrors docs/02-architecture.md "Tool contracts". Owned by main; lanes import, never edit.

chunk_id format: "<doc_id>:p<page>:<n>" with n zero-padded to 4 digits, for example
"nepm-asc-b1:p12:0003". page is 1-based in the PDF as served. Drafts cite as "[<chunk_id>]".
"""
from typing import Literal, TypedDict

SectionType = Literal["results_discussion"]
SearchMode = Literal["hybrid", "bm25", "vector"]


class Passage(TypedDict):
    chunk_id: str
    doc_id: str
    doc_title: str
    page: int
    section: str | None
    text: str          # untrusted data; tables rendered as markdown
    score: float


class CriterionSource(TypedDict):
    doc_id: str
    page: int
    table: str


class Exceedance(TypedDict):
    sample_id: str
    depth_m: float | None
    analyte: str
    result: float
    unit: str
    criterion: float
    criterion_unit: str
    ratio: float        # result / criterion after unit conversion, rounded to 2 dp
    source: CriterionSource


class NotScreened(TypedDict):
    sample_id: str
    analyte: str
    reason: Literal["below_lor", "no_criterion", "unit_mismatch", "no_depth", "non_numeric_criterion"]


class ScreeningResult(TypedDict):
    site_id: str
    criteria_set: str
    samples_screened: int
    analytes_screened: int
    exceedances: list[Exceedance]
    not_screened: list[NotScreened]
    notes: list[str]    # fixed caveats, e.g. duplicates screened separately


class CriteriaSetInfo(TypedDict):
    id: str
    title: str
    source: CriterionSource
    land_use: str
    matrix: str


class Citation(TypedDict):
    chunk_id: str
    doc_id: str
    page: int


class DraftResult(TypedDict):
    markdown: str
    citations: list[Citation]
    warnings: list[str]
    model: str          # model id actually used
    redactions: int     # count only, never values


class LLMReply(TypedDict):
    text: str
    model: str
    input_tokens: int
    output_tokens: int
