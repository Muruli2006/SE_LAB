"""
Code Coverage Test Suite for Cloud Storage Tier Module
Student Identifier: PES1UG24CS676
Lab 6 - Part A: Code Coverage Analysis

This test suite executes functional paths across all statements in cloud_storage_tier.py
including normal inputs, invalid inputs, edge cases, and exception handling.
"""

import sys
from pathlib import Path
import pytest

# Ensure the module directory is accessible regardless of invocation path
sys.path.insert(0, str(Path(__file__).parent))

from cloud_storage_tier import process_storage_tenants, monitor_replication_latency


# =====================================================================
# Tests for process_storage_tenants
# =====================================================================

def test_invalid_tenants_type_raises_value_error():
    """Verify ValueError is raised when tenants argument is not a list."""
    with pytest.raises(ValueError, match="Invalid tenants list or support fee"):
        process_storage_tenants("not_a_list", 10.0)

    with pytest.raises(ValueError, match="Invalid tenants list or support fee"):
        process_storage_tenants(None, 10.0)


def test_negative_support_fee_raises_value_error():
    """Verify ValueError is raised when fixed_support_fee is negative."""
    with pytest.raises(ValueError, match="Invalid tenants list or support fee"):
        process_storage_tenants([], -5.0)


def test_empty_tenants_returns_zero_usage():
    """Verify empty tenant list returns zero usage and 0.0 billed."""
    result = process_storage_tenants([], 15.0)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_inactive_tenant_skipped():
    """Verify inactive tenant accounts are skipped without processing buckets."""
    tenants = [
        {
            "account_active": False,
            "tier": "hot",
            "buckets": [{"size_gb": 200, "corrupted": False, "egress_gb": 50}]
        }
    ]
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_active_hot_tier_standard_bucket():
    """Verify hot tier standard calculation (rate = 0.025/GB) below 500GB."""
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "has_backup_vault": False,
            "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 50}]
        }
    ]
    # 100 * 0.025 = 2.50
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 2.5, "status": "BILLED"}


def test_active_cool_tier_standard_bucket():
    """Verify cool tier rate calculation (rate = 0.015/GB)."""
    tenants = [
        {
            "account_active": True,
            "tier": "cool",
            "has_backup_vault": False,
            "buckets": [{"size_gb": 200, "corrupted": False, "egress_gb": 80}]
        }
    ]
    # 200 * 0.015 = 3.00
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 3.0, "status": "BILLED"}


def test_active_archive_tier_standard_bucket():
    """Verify archive tier rate calculation (rate = 0.005/GB)."""
    tenants = [
        {
            "account_active": True,
            "tier": "archive",
            "has_backup_vault": False,
            "buckets": [{"size_gb": 400, "corrupted": False, "egress_gb": 20}]
        }
    ]
    # 400 * 0.005 = 2.00
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 2.0, "status": "BILLED"}


def test_unknown_tier_flagged_and_skipped():
    """Verify unknown tier flags a bucket and skips tenant billing."""
    tenants = [
        {
            "account_active": True,
            "tier": "glacier_premium",
            "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 0}]
        }
    ]
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_zero_or_negative_bucket_size_flagged():
    """Verify bucket with size <= 0 is flagged and skipped."""
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "buckets": [
                {"size_gb": 0, "corrupted": False, "egress_gb": 0},
                {"size_gb": -20, "corrupted": False, "egress_gb": 0}
            ]
        }
    ]
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_corrupted_bucket_in_hot_tier():
    """Verify corrupted bucket in hot tier is flagged and adds 0.0 without terminating."""
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "buckets": [
                {"size_gb": 100, "corrupted": True, "egress_gb": 0},
                {"size_gb": 100, "corrupted": False, "egress_gb": 0}
            ]
        }
    ]
    # 0.0 + (100 * 0.025 = 2.50) = 2.50
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 2.5, "status": "BILLED"}


def test_corrupted_bucket_in_archive_tier_breaks():
    """Verify corrupted bucket in archive tier zeroes tenant charge and breaks loop."""
    tenants = [
        {
            "account_active": True,
            "tier": "archive",
            "has_backup_vault": False,
            "buckets": [
                {"size_gb": 200, "corrupted": False, "egress_gb": 0},
                {"size_gb": 100, "corrupted": True, "egress_gb": 0},
                {"size_gb": 300, "corrupted": False, "egress_gb": 0}
            ]
        }
    ]
    # Even though bucket 1 had charge 1.0, corruption resets tenant_charge to 0.0 and breaks
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_large_bucket_discount_applied():
    """Verify 10% volume discount applied when bucket size exceeds 500GB."""
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "buckets": [{"size_gb": 1000, "corrupted": False, "egress_gb": 50}]
        }
    ]
    # (1000 * 0.025) * 0.90 = 25.0 * 0.90 = 22.50
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 22.5, "status": "BILLED"}


def test_egress_charge_exceeding_100gb():
    """Verify network egress charge applied for egress beyond 100GB."""
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 250}]
        }
    ]
    # Storage: 100 * 0.025 = 2.50
    # Egress: (250 - 100) * 0.08 = 150 * 0.08 = 12.00
    # Total: 14.50
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 14.5, "status": "BILLED"}


def test_backup_vault_fixed_fee():
    """Verify fixed support fee is added when tenant has backup vault enabled."""
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "has_backup_vault": True,
            "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 50}]
        }
    ]
    # 2.50 + 15.00 = 17.50
    result = process_storage_tenants(tenants, 15.0)
    assert result == {"total_billed": 17.5, "status": "BILLED"}


def test_audit_flagged_status_exceeding_four_flags():
    """Verify status is AUDIT_FLAGGED when flagged buckets exceed 4."""
    tenants = [
        {
            "account_active": True,
            "tier": "hot",
            "buckets": [
                {"size_gb": 0, "corrupted": False, "egress_gb": 0},
                {"size_gb": -5, "corrupted": False, "egress_gb": 0},
                {"size_gb": 0, "corrupted": False, "egress_gb": 0},
                {"size_gb": 100, "corrupted": True, "egress_gb": 0},
                {"size_gb": 100, "corrupted": True, "egress_gb": 0},
                {"size_gb": 100, "corrupted": False, "egress_gb": 0}
            ]
        }
    ]
    # 5 flags (> 4) -> AUDIT_FLAGGED, bucket 6 billed: 100 * 0.025 = 2.5
    result = process_storage_tenants(tenants, 10.0)
    assert result == {"total_billed": 2.5, "status": "AUDIT_FLAGGED"}


# =====================================================================
# Tests for monitor_replication_latency
# =====================================================================

def test_monitor_replication_no_data():
    """Verify monitor_replication_latency returns NO_DATA for empty or None input."""
    assert monitor_replication_latency([]) == "NO_DATA"
    assert monitor_replication_latency(None) == "NO_DATA"


def test_monitor_replication_synced_normal_and_spikes():
    """Verify monitor returns SYNCED when latencies are normal or non-consecutive spikes."""
    # All below 200ms
    cluster_normal = [[100, 150, 120], [80, 190, 110]]
    assert monitor_replication_latency(cluster_normal) == "SYNCED"

    # Non-consecutive spikes: lag_streak resets to 0 when latency <= 200
    cluster_intermittent = [[150, 250, 180, 220, 190]]
    assert monitor_replication_latency(cluster_intermittent) == "SYNCED"


def test_monitor_replication_sync_lag_alert():
    """Verify monitor returns SYNC_LAG_ALERT when lag streak reaches 2."""
    cluster_lagging = [
        [100, 150],
        [120, 250, 310, 100]  # Consecutive spikes > 200ms
    ]
    assert monitor_replication_latency(cluster_lagging) == "SYNC_LAG_ALERT"

