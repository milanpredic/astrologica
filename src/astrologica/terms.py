"""Public facade for traditional terms (bounds) tables and lookups."""

from astrologica._internal.domain.tables.terms import (
    TERMS_ASTROLOGICAL_ASSOCIATION,
    TERMS_CHALDEAN,
    TERMS_DOROTHEAN,
    TERMS_EGYPTIAN,
    TERMS_PTOLEMAIC,
    TermBoundary,
    TermSection,
    TermsSystem,
    TermsTable,
    term_boundaries,
    term_of,
)

__all__ = [
    "TERMS_ASTROLOGICAL_ASSOCIATION",
    "TERMS_CHALDEAN",
    "TERMS_DOROTHEAN",
    "TERMS_EGYPTIAN",
    "TERMS_PTOLEMAIC",
    "TermBoundary",
    "TermSection",
    "TermsSystem",
    "TermsTable",
    "term_boundaries",
    "term_of",
]
