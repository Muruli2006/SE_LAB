import math
import pytest
from hypothesis import given, strategies as st
from processor import parse_storage_quota, compute_compression_ratio, lookup_bandwidth_tier_rate

# ============================================================================
# 1. HYPOTHESIS PROPERTY-BASED FUZZ TESTS (NO UNEXPECTED CRASHES)
# ============================================================================

@given(st.text() | st.none())
def test_parse_storage_quota_no_crash(s):
    """
    Hypothesis fuzz test verifying that parse_storage_quota never crashes
    with unexpected exceptions. Malformed inputs must raise controlled
    ValueError or TypeError validation errors.
    """
    try:
        result = parse_storage_quota(s)
        assert isinstance(result, str)
        assert result.startswith("Quota: ")
        assert result.endswith(" GB")
    except (ValueError, TypeError):
        # Expected and handled validation error
        pass
    except Exception as e:
        assert False, f"parse_storage_quota crashed with unexpected exception: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_compute_compression_ratio_safe(s):
    """
    Hypothesis fuzz test verifying that compute_compression_ratio never crashes
    with unexpected exceptions. Malformed inputs or zero-division must be handled.
    """
    try:
        result = compute_compression_ratio(s)
        assert isinstance(result, float)
        assert result >= 0
    except (ValueError, TypeError, ZeroDivisionError):
        # Expected and handled validation error
        pass
    except Exception as e:
        assert False, f"compute_compression_ratio crashed with unexpected exception: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_lookup_bandwidth_tier_rate_safe(s):
    """
    Hypothesis fuzz test verifying that lookup_bandwidth_tier_rate never crashes
    with unexpected exceptions. Malformed inputs must raise controlled ValueError or TypeError.
    """
    try:
        result = lookup_bandwidth_tier_rate(s)
        assert result in (0.08, 0.05, 0.02)
    except (ValueError, TypeError):
        # Expected and handled validation error
        pass
    except Exception as e:
        assert False, f"lookup_bandwidth_tier_rate crashed with unexpected exception: {type(e).__name__}: {e}"


# ============================================================================
# 2. VALID INPUT UNIT TESTS
# ============================================================================

def test_parse_storage_quota_valid():
    assert parse_storage_quota("500MB") == "Quota: 0.50 GB"
    assert parse_storage_quota("20GB") == "Quota: 20.00 GB"
    assert parse_storage_quota("2TB") == "Quota: 2000.00 GB"
    assert parse_storage_quota("  10gb  ") == "Quota: 10.00 GB"
    assert parse_storage_quota("1.5GB") == "Quota: 1.50 GB"
    assert parse_storage_quota("0MB") == "Quota: 0.00 GB"


def test_compute_compression_ratio_valid():
    assert compute_compression_ratio("1024:256") == 4.0
    assert compute_compression_ratio("100:200") == 0.5
    assert compute_compression_ratio("500:500") == 1.0
    assert compute_compression_ratio("  2048 : 512  ") == 4.0
    assert compute_compression_ratio("10.5:2.1") == 5.0
    assert compute_compression_ratio("0:100") == 0.0


def test_lookup_bandwidth_tier_rate_valid():
    assert lookup_bandwidth_tier_rate("HOT_TIER") == 0.08
    assert lookup_bandwidth_tier_rate("COLD") == 0.05
    assert lookup_bandwidth_tier_rate("ARCHIVE") == 0.02
    assert lookup_bandwidth_tier_rate("hot") == 0.08
    assert lookup_bandwidth_tier_rate("  archive_deep  ") == 0.02
    assert lookup_bandwidth_tier_rate("COL_STORAGE") == 0.05


# ============================================================================
# 3. INVALID INPUTS & DEFENSIVE VALIDATION ERROR TESTS
# ============================================================================

def test_parse_storage_quota_invalid_inputs():
    with pytest.raises(TypeError):
        parse_storage_quota(None)
    with pytest.raises(TypeError):
        parse_storage_quota(12345)
    with pytest.raises(ValueError):
        parse_storage_quota("")
    with pytest.raises(ValueError):
        parse_storage_quota("   ")
    with pytest.raises(ValueError):
        parse_storage_quota("MB")
    with pytest.raises(ValueError):
        parse_storage_quota("500KB")  # Unsupported unit
    with pytest.raises(ValueError):
        parse_storage_quota("500PB")  # Unsupported unit
    with pytest.raises(ValueError):
        parse_storage_quota("-500MB")  # Negative value
    with pytest.raises(ValueError):
        parse_storage_quota("abcMB")  # Non-numeric
    with pytest.raises(ValueError):
        parse_storage_quota("infMB")  # Non-finite
    with pytest.raises(ValueError):
        parse_storage_quota("nanGB")  # Non-finite


def test_compute_compression_ratio_invalid_inputs():
    with pytest.raises(TypeError):
        compute_compression_ratio(None)
    with pytest.raises(TypeError):
        compute_compression_ratio(1024)
    with pytest.raises(ValueError):
        compute_compression_ratio("")
    with pytest.raises(ValueError):
        compute_compression_ratio("1024")  # Missing colon
    with pytest.raises(ValueError):
        compute_compression_ratio("1024:256:64")  # Too many colons
    with pytest.raises(ValueError):
        compute_compression_ratio(":256")  # Missing raw bytes
    with pytest.raises(ValueError):
        compute_compression_ratio("1024:")  # Missing compressed bytes
    with pytest.raises(ValueError):
        compute_compression_ratio("abc:256")  # Non-numeric
    with pytest.raises(ValueError):
        compute_compression_ratio("-1024:256")  # Negative raw bytes
    with pytest.raises(ValueError):
        compute_compression_ratio("1024:-256")  # Negative compressed bytes
    with pytest.raises(ValueError):
        compute_compression_ratio("inf:256")  # Non-finite
    with pytest.raises(ValueError):
        compute_compression_ratio("1024:nan")  # Non-finite
    with pytest.raises(ZeroDivisionError):
        compute_compression_ratio("1024:0")  # Division by zero


def test_lookup_bandwidth_tier_rate_invalid_inputs():
    with pytest.raises(TypeError):
        lookup_bandwidth_tier_rate(None)
    with pytest.raises(TypeError):
        lookup_bandwidth_tier_rate(100)
    with pytest.raises(ValueError):
        lookup_bandwidth_tier_rate("")
    with pytest.raises(ValueError):
        lookup_bandwidth_tier_rate("   ")
    with pytest.raises(ValueError):
        lookup_bandwidth_tier_rate("HO")  # Less than 3 chars
    with pytest.raises(ValueError):
        lookup_bandwidth_tier_rate("STANDARD")  # Unsupported tier
    with pytest.raises(ValueError):
        lookup_bandwidth_tier_rate("GLACIER")  # Unsupported tier
    with pytest.raises(ValueError):
        lookup_bandwidth_tier_rate("PREMIUM_TIER")  # Unsupported tier


# ============================================================================
# 4. HYPOTHESIS PROPERTY TESTS (GENERATIVE VALIDATION)
# ============================================================================

@given(st.integers(min_value=0, max_value=10000), st.sampled_from(["MB", "GB", "TB"]))
def test_parse_storage_quota_property_valid(val, unit):
    multipliers = {"MB": 0.001, "GB": 1.0, "TB": 1000.0}
    input_str = f"{val}{unit}"
    expected_gb = val * multipliers[unit]
    expected_str = f"Quota: {expected_gb:.2f} GB"
    assert parse_storage_quota(input_str) == expected_str


@given(
    st.floats(min_value=0.01, max_value=1e6, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.01, max_value=1e6, allow_nan=False, allow_infinity=False)
)
def test_compute_compression_ratio_property_valid(raw, comp):
    input_str = f"{raw}:{comp}"
    expected_ratio = round(raw / comp, 2)
    assert compute_compression_ratio(input_str) == expected_ratio


@given(st.sampled_from(["HOT", "HOT_TIER", "COLD", "COL_STORAGE", "ARCHIVE", "ARC_TIER"]))
def test_lookup_bandwidth_tier_rate_property_valid(tier):
    expected_rates = {"HOT": 0.08, "COL": 0.05, "ARC": 0.02}
    expected = expected_rates[tier[:3].upper()]
    assert lookup_bandwidth_tier_rate(tier) == expected
