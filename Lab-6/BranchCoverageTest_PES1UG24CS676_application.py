"""
Branch Coverage Test Suite for Cloud Storage Tier Module
Student Identifier: PES1UG24CS676
Lab 6 - Part B: Branch Coverage Analysis

This test suite is specifically designed to cover all control decisions,
conditional branches (True and False branches), compound conditions,
loop boundaries, and decision paths in cloud_storage_tier.py.
"""

import sys
from pathlib import Path
import pytest

# Ensure the module directory is accessible regardless of invocation path
sys.path.insert(0, str(Path(__file__).parent))

from cloud_storage_tier import process_storage_tenants, monitor_replication_latency


# =====================================================================
# Branch Tests: process_storage_tenants
# =====================================================================

class TestProcessStorageTenantsBranchDecisions:
    """Branch-focused test cases for process_storage_tenants."""

    # -----------------------------------------------------------------
    # Decision 1: if not isinstance(tenants, list) or fixed_support_fee < 0:
    # -----------------------------------------------------------------
    def test_branch_d1_invalid_tenants_type_not_list(self):
        """Branch D1.1 (True): not isinstance(tenants, list) -> raises ValueError."""
        with pytest.raises(ValueError, match="Invalid tenants list or support fee"):
            process_storage_tenants({"tenant": "bad"}, 10.0)

        with pytest.raises(ValueError, match="Invalid tenants list or support fee"):
            process_storage_tenants(None, 0.0)

    def test_branch_d1_negative_support_fee(self):
        """Branch D1.2 (True): isinstance is True, but fixed_support_fee < 0 -> raises ValueError."""
        with pytest.raises(ValueError, match="Invalid tenants list or support fee"):
            process_storage_tenants([], -0.01)

        with pytest.raises(ValueError, match="Invalid tenants list or support fee"):
            process_storage_tenants([], -10.0)

    def test_branch_d1_valid_parameters_zero_support_fee(self):
        """Branch D1.3 (False): valid list and non-negative support fee boundary (0.0)."""
        result = process_storage_tenants([], 0.0)
        assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}

    # -----------------------------------------------------------------
    # Decision 2 & 3: for tenant in tenants & if not tenant.get("account_active", False):
    # -----------------------------------------------------------------
    def test_branch_d2_empty_tenants_loop_bypassed(self):
        """Branch D2.1: tenants loop does zero iterations when list is empty."""
        result = process_storage_tenants([], 5.0)
        assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}

    def test_branch_d3_tenant_account_inactive_and_default(self):
        """Branch D3.1 (True): tenant account_active is False or missing -> continue."""
        tenants = [
            {"account_active": False, "tier": "hot", "buckets": [{"size_gb": 100}]},
            {"tier": "hot", "buckets": [{"size_gb": 100}]}  # missing account_active defaults to False
        ]
        result = process_storage_tenants(tenants, 10.0)
        assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}

    def test_branch_d3_tenant_account_active_true(self):
        """Branch D3.2 (False): tenant account_active is True -> proceed to billing."""
        tenants = [
            {"account_active": True, "tier": "hot", "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 0}]}
        ]
        result = process_storage_tenants(tenants, 0.0)
        # 100 * 0.025 = 2.50
        assert result == {"total_billed": 2.5, "status": "BILLED"}

    # -----------------------------------------------------------------
    # Decision 4: Tier matching (hot, cool, archive, else)
    # -----------------------------------------------------------------
    def test_branch_d4_tier_hot_explicit_and_default(self):
        """Branch D4.1: tier == 'hot' explicitly and via default fallback."""
        # Explicit hot tier
        t1 = [{"account_active": True, "tier": "hot", "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 0}]}]
        r1 = process_storage_tenants(t1, 0.0)
        assert r1 == {"total_billed": 2.5, "status": "BILLED"}

        # Missing tier key defaults to 'hot'
        t2 = [{"account_active": True, "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 0}]}]
        r2 = process_storage_tenants(t2, 0.0)
        assert r2 == {"total_billed": 2.5, "status": "BILLED"}

    def test_branch_d4_tier_cool(self):
        """Branch D4.2: tier == 'cool' -> rate 0.015."""
        tenants = [
            {"account_active": True, "tier": "cool", "buckets": [{"size_gb": 200, "corrupted": False, "egress_gb": 0}]}
        ]
        # 200 * 0.015 = 3.00
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 3.0, "status": "BILLED"}

    def test_branch_d4_tier_archive(self):
        """Branch D4.3: tier == 'archive' -> rate 0.005."""
        tenants = [
            {"account_active": True, "tier": "archive", "buckets": [{"size_gb": 200, "corrupted": False, "egress_gb": 0}]}
        ]
        # 200 * 0.005 = 1.00
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 1.0, "status": "BILLED"}

    def test_branch_d4_tier_unrecognized_else_branch(self):
        """Branch D4.4: unrecognized tier -> flags bucket and continues to next tenant."""
        tenants = [
            {"account_active": True, "tier": "ultra_cold", "buckets": [{"size_gb": 500, "corrupted": False}]},
            {"account_active": True, "tier": "hot", "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 0}]}
        ]
        # First tenant flagged and skipped, second tenant billed 2.50
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 2.5, "status": "BILLED"}

    # -----------------------------------------------------------------
    # Decision 5 & 6: Bucket size validation (size_gb <= 0)
    # -----------------------------------------------------------------
    def test_branch_d5_empty_buckets_list(self):
        """Branch D5.1: buckets list is empty (or omitted) -> skips bucket loop."""
        tenants = [
            {"account_active": True, "tier": "hot", "buckets": []},
            {"account_active": True, "tier": "hot"}  # missing buckets key defaults to []
        ]
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}

    def test_branch_d6_bucket_size_zero_and_negative(self):
        """Branch D6.1 (True): size_gb <= 0 (boundary at 0 and negative value)."""
        tenants = [
            {
                "account_active": True,
                "tier": "hot",
                "buckets": [
                    {"size_gb": 0, "corrupted": False, "egress_gb": 0},
                    {"size_gb": -15, "corrupted": False, "egress_gb": 0}
                ]
            }
        ]
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}

    def test_branch_d6_bucket_size_positive_boundary(self):
        """Branch D6.2 (False): size_gb > 0 (boundary at 1 GB)."""
        tenants = [
            {
                "account_active": True,
                "tier": "hot",
                "buckets": [{"size_gb": 1, "corrupted": False, "egress_gb": 0}]
            }
        ]
        # 1 * 0.025 = 0.025 -> rounded to 0.03
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 0.03, "status": "BILLED"}

    # -----------------------------------------------------------------
    # Decision 7: Corrupted bucket handling across tiers
    # -----------------------------------------------------------------
    def test_branch_d7_corrupted_in_non_archive_continues_loop(self):
        """Branch D7.1: is_corrupted True and tier != 'archive' -> charge += 0.0, does not break."""
        tenants = [
            {
                "account_active": True,
                "tier": "cool",
                "buckets": [
                    {"size_gb": 100, "corrupted": True, "egress_gb": 0},    # Flagged, adds 0.0
                    {"size_gb": 100, "corrupted": False, "egress_gb": 0}   # 100 * 0.015 = 1.50
                ]
            }
        ]
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 1.5, "status": "BILLED"}

    def test_branch_d7_corrupted_in_archive_tier_breaks_loop(self):
        """Branch D7.2: is_corrupted True and tier == 'archive' -> tenant_charge = 0.0 and break."""
        tenants = [
            {
                "account_active": True,
                "tier": "archive",
                "buckets": [
                    {"size_gb": 200, "corrupted": False, "egress_gb": 0},  # Billed 1.00 initially
                    {"size_gb": 100, "corrupted": True, "egress_gb": 0},   # Resets to 0.0 and breaks
                    {"size_gb": 500, "corrupted": False, "egress_gb": 0}  # Never reached due to break
                ]
            }
        ]
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}

    # -----------------------------------------------------------------
    # Decision 8: Volume discount threshold (size_gb > 500)
    # -----------------------------------------------------------------
    def test_branch_d8_size_boundary_500_no_discount(self):
        """Branch D8.1 (False): size_gb == 500 (boundary) -> no volume discount."""
        tenants = [
            {
                "account_active": True,
                "tier": "hot",
                "buckets": [{"size_gb": 500, "corrupted": False, "egress_gb": 0}]
            }
        ]
        # 500 * 0.025 = 12.50
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 12.5, "status": "BILLED"}

    def test_branch_d8_size_boundary_501_discount_applied(self):
        """Branch D8.2 (True): size_gb == 501 (boundary > 500) -> 10% volume discount applied."""
        tenants = [
            {
                "account_active": True,
                "tier": "hot",
                "buckets": [{"size_gb": 501, "corrupted": False, "egress_gb": 0}]
            }
        ]
        # (501 * 0.025) * 0.90 = 12.525 * 0.90 = 11.2725 -> 11.27
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 11.27, "status": "BILLED"}

    # -----------------------------------------------------------------
    # Decision 9: Egress charge threshold (egress_gb > 100)
    # -----------------------------------------------------------------
    def test_branch_d9_egress_boundary_100_no_surcharge(self):
        """Branch D9.1 (False): egress_gb == 100 (boundary) -> no extra egress fee."""
        tenants = [
            {
                "account_active": True,
                "tier": "hot",
                "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 100}]
            }
        ]
        # Only storage: 100 * 0.025 = 2.50
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 2.5, "status": "BILLED"}

    def test_branch_d9_egress_boundary_101_surcharge_applied(self):
        """Branch D9.2 (True): egress_gb == 101 (boundary > 100) -> egress fee applied."""
        tenants = [
            {
                "account_active": True,
                "tier": "hot",
                "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 101}]
            }
        ]
        # Storage: 2.50, Egress: (101 - 100) * 0.08 = 0.08 -> 2.58
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 2.58, "status": "BILLED"}

    # -----------------------------------------------------------------
    # Decision 10: Backup vault fee
    # -----------------------------------------------------------------
    def test_branch_d10_has_backup_vault_true(self):
        """Branch D10.1 (True): has_backup_vault is True -> fixed_support_fee added."""
        tenants = [
            {
                "account_active": True,
                "tier": "hot",
                "has_backup_vault": True,
                "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 0}]
            }
        ]
        # 2.50 + 20.00 = 22.50
        result = process_storage_tenants(tenants, 20.0)
        assert result == {"total_billed": 22.5, "status": "BILLED"}

    def test_branch_d10_has_backup_vault_false_and_default(self):
        """Branch D10.2 (False): has_backup_vault is False or omitted -> no fee added."""
        tenants = [
            {
                "account_active": True,
                "tier": "hot",
                "has_backup_vault": False,
                "buckets": [{"size_gb": 100, "corrupted": False, "egress_gb": 0}]
            }
        ]
        result = process_storage_tenants(tenants, 20.0)
        assert result == {"total_billed": 2.5, "status": "BILLED"}

    # -----------------------------------------------------------------
    # Decision 11 & 12: Audit flag threshold and final status
    # -----------------------------------------------------------------
    def test_branch_d11_flagged_buckets_boundary_4_not_flagged(self):
        """Branch D11.1 (False): flagged_buckets == 4 (boundary <= 4) -> not AUDIT_FLAGGED."""
        tenants = [
            {
                "account_active": True,
                "tier": "hot",
                "buckets": [
                    {"size_gb": 0},  # flag 1
                    {"size_gb": 0},  # flag 2
                    {"size_gb": 0},  # flag 3
                    {"size_gb": 0},  # flag 4
                    {"size_gb": 100, "corrupted": False, "egress_gb": 0}  # billed: 2.50
                ]
            }
        ]
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 2.5, "status": "BILLED"}

    def test_branch_d11_flagged_buckets_boundary_5_audit_flagged(self):
        """Branch D11.2 (True): flagged_buckets == 5 (boundary > 4) -> status is AUDIT_FLAGGED."""
        tenants = [
            {
                "account_active": True,
                "tier": "hot",
                "buckets": [
                    {"size_gb": 0},  # flag 1
                    {"size_gb": 0},  # flag 2
                    {"size_gb": 0},  # flag 3
                    {"size_gb": 0},  # flag 4
                    {"size_gb": 0},  # flag 5
                    {"size_gb": 200, "corrupted": False, "egress_gb": 0}  # billed: 5.00
                ]
            }
        ]
        result = process_storage_tenants(tenants, 0.0)
        assert result == {"total_billed": 5.0, "status": "AUDIT_FLAGGED"}


# =====================================================================
# Branch Tests: monitor_replication_latency
# =====================================================================

class TestMonitorReplicationLatencyBranchDecisions:
    """Branch-focused test cases for monitor_replication_latency."""

    def test_branch_m1_matrix_falsy_empty_and_none(self):
        """Branch M1.1 (True): not cluster_matrix -> returns NO_DATA."""
        assert monitor_replication_latency([]) == "NO_DATA"
        assert monitor_replication_latency(None) == "NO_DATA"

    def test_branch_m1_matrix_with_empty_node_log(self):
        """Branch M1.2: cluster_matrix has an empty inner log -> for loop over logs finishes."""
        assert monitor_replication_latency([[]]) == "SYNCED"

    def test_branch_m2_latency_boundary_200_no_lag(self):
        """Branch M2.1 (False): latency_ms == 200 (boundary) -> lag_streak resets to 0."""
        # 200 is not > 200, so lag_streak resets
        matrix = [[200, 200, 200]]
        assert monitor_replication_latency(matrix) == "SYNCED"

    def test_branch_m2_latency_boundary_201_single_spike_no_alert(self):
        """Branch M2.2: latency_ms == 201 (boundary > 200) followed by normal latency -> resets streak."""
        # A single spike increments lag_streak to 1 (not >= 2), next reading resets it to 0
        matrix = [[201, 150, 250, 100]]
        assert monitor_replication_latency(matrix) == "SYNCED"

    def test_branch_m3_lag_streak_consecutive_spikes_alert(self):
        """Branch M3.1 (True): lag_streak reaches 2 consecutive spikes -> returns SYNC_LAG_ALERT."""
        # First node normal, second node has 2 consecutive spikes
        matrix = [
            [120, 180],
            [205, 210]  # Two consecutive spikes > 200ms
        ]
        assert monitor_replication_latency(matrix) == "SYNC_LAG_ALERT"

    def test_branch_m3_multiple_nodes_all_synced(self):
        """Branch M3.2: multiple nodes all normal -> outer loop finishes completely -> SYNCED."""
        matrix = [
            [50, 100, 150],
            [90, 110, 130],
            [80, 120, 140]
        ]
        assert monitor_replication_latency(matrix) == "SYNCED"

