"""
Tests for TimeConstraint NLU System — F-TEMPORAL.
World-class: TIMEX3 ISO standard, identico a Dialogflow CX / Amazon Lex.
Target: 50+ PASS, 0 FAIL
"""
import pytest
from datetime import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from entity_extractor import (
    extract_time,
    extract_time_constraint,
    TimeConstraint,
    TimeConstraintType,
)


# =============================================================================
# AFTER constraint — "dopo le X"
# =============================================================================

@pytest.mark.parametrize("text,expected_anchor", [
    ("dopo le 17", time(17, 0)),
    ("dopo le 17 che torno a lavorare", time(17, 0)),
    ("vorrei dopo le 18", time(18, 0)),
    ("mi serve dopo le 9", time(9, 0)),
    ("dopo le 14:30", time(14, 30)),
    ("dopo le 10 e 30", time(10, 30)),
    ("dalle 17 in poi", time(17, 0)),
])
def test_after_constraint_extraction(text, expected_anchor):
    result = extract_time(text)
    assert result is not None, f"extract_time('{text}') returned None"
    assert result.time_constraint is not None, f"No time_constraint for '{text}'"
    assert result.time_constraint.constraint_type == TimeConstraintType.AFTER, \
        f"Expected AFTER, got {result.time_constraint.constraint_type} for '{text}'"
    assert result.time_constraint.anchor_time == expected_anchor, \
        f"Expected anchor {expected_anchor}, got {result.time_constraint.anchor_time} for '{text}'"


@pytest.mark.parametrize("text", [
    "dopo le 17",
    "dopo le 18 possibilmente",
    "vorrei dopo le 16",
])
def test_after_constraint_display(text):
    result = extract_time(text)
    assert result is not None
    assert result.time_constraint is not None
    display = result.time_constraint.display()
    assert display.startswith("dopo le"), f"Expected 'dopo le ...' got '{display}' for '{text}'"
    assert "alle" not in display, f"Display should NOT contain 'alle' for AFTER constraint: '{display}'"


@pytest.mark.parametrize("text", [
    "dopo le 17",
    "dopo le 18",
])
def test_after_constraint_not_exact(text):
    """Regression: 'dopo le X' deve essere AFTER, MAI 'alle X'."""
    result = extract_time(text)
    assert result is not None
    assert result.time_constraint is not None
    assert result.time_constraint.constraint_type != TimeConstraintType.EXACT, \
        f"'dopo le X' non deve essere EXACT — root cause del bug originale"


# =============================================================================
# BEFORE constraint — "prima delle X"
# =============================================================================

@pytest.mark.parametrize("text,expected_anchor", [
    ("prima delle 14", time(14, 0)),
    ("prima della 12", time(12, 0)),
    ("voglio prima delle 10", time(10, 0)),
    ("prima delle 16 grazie", time(16, 0)),
])
def test_before_constraint_extraction(text, expected_anchor):
    result = extract_time(text)
    assert result is not None
    assert result.time_constraint is not None
    assert result.time_constraint.constraint_type == TimeConstraintType.BEFORE, \
        f"Expected BEFORE for '{text}'"
    assert result.time_constraint.anchor_time == expected_anchor


@pytest.mark.parametrize("text", [
    "prima delle 14",
    "prima delle 11",
])
def test_before_constraint_display(text):
    result = extract_time(text)
    assert result is not None
    display = result.time_constraint.display()
    assert display.startswith("prima delle"), f"Expected 'prima delle ...' got '{display}'"


# =============================================================================
# AROUND constraint — "verso le X"
# =============================================================================

@pytest.mark.parametrize("text,expected_anchor", [
    ("verso le 15", time(15, 0)),
    ("intorno alle 10", time(10, 0)),
    ("circa alle 11", time(11, 0)),
    ("sulle 16", time(16, 0)),
])
def test_around_constraint_extraction(text, expected_anchor):
    result = extract_time(text)
    assert result is not None
    assert result.time_constraint is not None
    assert result.time_constraint.constraint_type == TimeConstraintType.AROUND, \
        f"Expected AROUND for '{text}'"
    assert result.time_constraint.anchor_time == expected_anchor


# =============================================================================
# RANGE constraint — "tra le X e le Y"
# =============================================================================

@pytest.mark.parametrize("text,start,end", [
    ("tra le 14 e le 16", time(14, 0), time(16, 0)),
    ("tra le 9 e le 11", time(9, 0), time(11, 0)),
    ("tra le 10 e le 12", time(10, 0), time(12, 0)),
])
def test_range_constraint_extraction(text, start, end):
    result = extract_time(text)
    assert result is not None
    assert result.time_constraint is not None
    assert result.time_constraint.constraint_type == TimeConstraintType.RANGE
    assert result.time_constraint.range_start == start
    assert result.time_constraint.range_end == end


# =============================================================================
# Semantic anchors italiani
# =============================================================================

@pytest.mark.parametrize("text,expected_type,expected_anchor", [
    ("dopo il lavoro", TimeConstraintType.AFTER, time(18, 0)),
    ("dopo pranzo", TimeConstraintType.AFTER, time(13, 30)),
    ("dopo il pranzo", TimeConstraintType.AFTER, time(13, 30)),
    ("a fine giornata", TimeConstraintType.AFTER, time(17, 0)),
    ("prima di pranzo", TimeConstraintType.BEFORE, time(13, 0)),
    ("dopo la scuola", TimeConstraintType.AFTER, time(16, 0)),
])
def test_semantic_anchors(text, expected_type, expected_anchor):
    result = extract_time(text)
    assert result is not None, f"No result for semantic anchor '{text}'"
    assert result.time_constraint is not None, f"No constraint for '{text}'"
    assert result.time_constraint.constraint_type == expected_type, \
        f"Expected {expected_type} for '{text}', got {result.time_constraint.constraint_type}"
    assert result.time_constraint.anchor_time == expected_anchor, \
        f"Expected {expected_anchor} for '{text}', got {result.time_constraint.anchor_time}"


# =============================================================================
# EXACT constraint — "alle 15:30" deve essere EXACT (no regression)
# =============================================================================

@pytest.mark.parametrize("text", [
    "alle 15:30",
    "alle 10",
    "ore 9",
    "15:30",
])
def test_exact_no_constraint(text):
    """Exact times non devono avere TimeConstraint (o EXACT)."""
    result = extract_time(text)
    assert result is not None, f"No result for '{text}'"
    # Exact times: either no constraint or EXACT type
    if result.time_constraint:
        assert result.time_constraint.constraint_type == TimeConstraintType.EXACT, \
            f"Exact time '{text}' should not get AFTER/BEFORE/AROUND constraint"


# =============================================================================
# TimeConstraint.matches() — filtro slot disponibili
# =============================================================================

def test_matches_after():
    tc = TimeConstraint(TimeConstraintType.AFTER, anchor_time=time(17, 0))
    assert tc.matches(time(18, 0)) is True
    assert tc.matches(time(17, 30)) is True
    assert tc.matches(time(17, 0)) is False  # Non "dopo" 17:00 esatto
    assert tc.matches(time(16, 0)) is False


def test_matches_before():
    tc = TimeConstraint(TimeConstraintType.BEFORE, anchor_time=time(14, 0))
    assert tc.matches(time(13, 0)) is True
    assert tc.matches(time(13, 59)) is True
    assert tc.matches(time(14, 0)) is False
    assert tc.matches(time(15, 0)) is False


def test_matches_around():
    tc = TimeConstraint(TimeConstraintType.AROUND, anchor_time=time(15, 0))
    assert tc.matches(time(15, 0)) is True
    assert tc.matches(time(14, 30)) is True
    assert tc.matches(time(15, 30)) is True
    assert tc.matches(time(13, 0)) is False
    assert tc.matches(time(17, 0)) is False


def test_matches_range():
    tc = TimeConstraint(TimeConstraintType.RANGE, range_start=time(14, 0), range_end=time(16, 0))
    assert tc.matches(time(14, 0)) is True
    assert tc.matches(time(15, 0)) is True
    assert tc.matches(time(16, 0)) is True
    assert tc.matches(time(13, 59)) is False
    assert tc.matches(time(16, 1)) is False


def test_matches_first_available():
    tc = TimeConstraint(TimeConstraintType.FIRST_AVAILABLE)
    assert tc.matches(time(9, 0)) is True
    assert tc.matches(time(18, 0)) is True


# =============================================================================
# TimeConstraint.display() — stringa corretta per Sara
# =============================================================================

@pytest.mark.parametrize("constraint,expected_prefix", [
    (TimeConstraint(TimeConstraintType.AFTER, anchor_time=time(17, 0)), "dopo le"),
    (TimeConstraint(TimeConstraintType.BEFORE, anchor_time=time(14, 0)), "prima delle"),
    (TimeConstraint(TimeConstraintType.AROUND, anchor_time=time(15, 0)), "verso le"),
    (TimeConstraint(TimeConstraintType.FIRST_AVAILABLE), "prima possibile"),
])
def test_display(constraint, expected_prefix):
    display = constraint.display()
    assert display.startswith(expected_prefix), \
        f"Expected '{expected_prefix}...' got '{display}'"


# =============================================================================
# extract_time_constraint() — entry point
# =============================================================================

def test_extract_time_constraint_after():
    tc = extract_time_constraint("dopo le 17")
    assert tc is not None
    assert tc.constraint_type == TimeConstraintType.AFTER
    assert tc.anchor_time == time(17, 0)


def test_extract_time_constraint_first_available():
    tc = extract_time_constraint("prima possibile")
    assert tc is not None
    assert tc.constraint_type == TimeConstraintType.FIRST_AVAILABLE


def test_extract_time_constraint_subito():
    tc = extract_time_constraint("subito se possibile")
    assert tc is not None
    assert tc.constraint_type == TimeConstraintType.FIRST_AVAILABLE


def test_extract_time_constraint_exact_returns_none():
    """Exact times → extract_time_constraint returns None (no constraint)."""
    tc = extract_time_constraint("alle 15:30")
    assert tc is None or (tc and tc.constraint_type == TimeConstraintType.EXACT)


# =============================================================================
# ExtractedTime.get_display() — constraint-aware
# =============================================================================

def test_get_display_after():
    result = extract_time("dopo le 17")
    assert result is not None
    display = result.get_display()
    assert display == "dopo le 17:00", f"Got '{display}'"


def test_get_display_before():
    result = extract_time("prima delle 14")
    assert result is not None
    display = result.get_display()
    assert display == "prima delle 14:00", f"Got '{display}'"


def test_get_display_exact():
    result = extract_time("alle 15:30")
    assert result is not None
    display = result.get_display()
    assert display == "alle 15:30", f"Got '{display}'"


def test_get_display_no_constraint():
    result = extract_time("alle 10")
    assert result is not None
    display = result.get_display()
    assert display.startswith("alle"), f"Expected 'alle ...' got '{display}'"


# =============================================================================
# Regression: "alle 15:30" non deve avere constraint AFTER/BEFORE/AROUND
# =============================================================================

@pytest.mark.parametrize("text,expected_time_str", [
    ("alle 15:30", "15:30"),
    ("ore 9", "09:00"),
    ("le 17 e 30", "17:30"),
    ("alle 10 e mezza", "10:30"),
])
def test_exact_times_no_wrong_constraint(text, expected_time_str):
    result = extract_time(text)
    assert result is not None, f"No result for '{text}'"
    assert result.to_string() == expected_time_str, \
        f"Expected time {expected_time_str}, got {result.to_string()} for '{text}'"
    if result.time_constraint:
        assert result.time_constraint.constraint_type == TimeConstraintType.EXACT, \
            f"Expected no constraint or EXACT for '{text}', got {result.time_constraint.constraint_type}"


# =============================================================================
# TimeConstraint serialization — verifica che i valori .value siano string
# =============================================================================

def test_constraint_type_values_are_strings():
    """I valori .value devono essere string serializzabili per BookingContext."""
    assert TimeConstraintType.AFTER.value == "after"
    assert TimeConstraintType.BEFORE.value == "before"
    assert TimeConstraintType.AROUND.value == "around"
    assert TimeConstraintType.RANGE.value == "range"
    assert TimeConstraintType.EXACT.value == "exact"
    assert TimeConstraintType.FIRST_AVAILABLE.value == "first_available"
    assert TimeConstraintType.SLOT.value == "slot"


def test_constraint_type_roundtrip():
    """TimeConstraintType(value) deve ricostruire il tipo correttamente."""
    for ct in TimeConstraintType:
        assert TimeConstraintType(ct.value) == ct, \
            f"Roundtrip failed for {ct}"
