import math

def parse_storage_quota(quota_str):
    """
    Parses storage quota string with unit suffix into Gigabytes (GB).
    Assumes format: '<digits><2-letter unit>' (e.g. '500MB', '20GB', '2TB').
    Defensively validates input types, empty/malformed strings, unit suffixes,
    and non-negative finite numeric values.
    """
    if not isinstance(quota_str, str):
        raise TypeError(f"Quota input must be a string, got {type(quota_str).__name__}")

    cleaned = quota_str.strip().upper()
    if len(cleaned) < 3:
        raise ValueError("Quota string is empty or too short (expected e.g. '500MB')")

    unit = cleaned[-2:]
    val_str = cleaned[:-2].strip()

    multipliers = {
        "MB": 0.001,
        "GB": 1.0,
        "TB": 1000.0
    }

    if unit not in multipliers:
        raise ValueError(f"Unsupported storage unit '{unit}'. Supported units are MB, GB, TB.")

    if not val_str:
        raise ValueError("Quota numeric value is missing")

    try:
        value = float(val_str)
    except ValueError:
        raise ValueError(f"Invalid numeric value '{val_str}' for storage quota")

    if math.isnan(value) or math.isinf(value):
        raise ValueError("Storage quota must be a finite numeric value")

    if value < 0:
        raise ValueError("Storage quota value cannot be negative")

    gb_total = value * multipliers[unit]
    return f"Quota: {gb_total:.2f} GB"


def compute_compression_ratio(size_metric_str):
    """
    Computes compression ratio: raw_bytes / compressed_bytes.
    Assumes format: 'raw_bytes:compressed_bytes' (e.g. '1024:256').
    Defensively validates input types, colon delimiter format, numeric values,
    negative values, non-finite values, and division by zero.
    """
    if not isinstance(size_metric_str, str):
        raise TypeError(f"Size metric input must be a string, got {type(size_metric_str).__name__}")

    cleaned = size_metric_str.strip()
    if not cleaned:
        raise ValueError("Size metric string cannot be empty")

    parts = cleaned.split(':')
    if len(parts) != 2:
        raise ValueError("Size metric must be in format 'raw_bytes:compressed_bytes' with exactly one colon delimiter")

    raw_str = parts[0].strip()
    comp_str = parts[1].strip()

    if not raw_str or not comp_str:
        raise ValueError("Both raw_bytes and compressed_bytes must be non-empty numeric strings")

    try:
        raw_bytes = float(raw_str)
        comp_bytes = float(comp_str)
    except ValueError:
        raise ValueError("Raw bytes and compressed bytes must be numeric values")

    if math.isnan(raw_bytes) or math.isinf(raw_bytes) or math.isnan(comp_bytes) or math.isinf(comp_bytes):
        raise ValueError("Byte values must be finite numbers")

    if raw_bytes < 0 or comp_bytes < 0:
        raise ValueError("Byte values cannot be negative")

    if comp_bytes == 0:
        raise ZeroDivisionError("Compressed bytes cannot be zero (division by zero)")

    ratio = raw_bytes / comp_bytes
    return round(ratio, 2)


def lookup_bandwidth_tier_rate(tier_descriptor):
    """
    Looks up rate per GB for egress traffic using the first 3 letters of the tier name.
    Assumes standard tier prefix with at least 3 letters.
    Defensively validates input types, string length, and standard supported tiers.
    """
    if not isinstance(tier_descriptor, str):
        raise TypeError(f"Tier descriptor must be a string, got {type(tier_descriptor).__name__}")

    cleaned = tier_descriptor.strip().upper()
    if len(cleaned) < 3:
        raise ValueError("Tier descriptor must be at least 3 characters long")

    prefix = cleaned[:3]
    tier_rates = {
        "HOT": 0.08,
        "COL": 0.05,
        "ARC": 0.02
    }

    if prefix not in tier_rates:
        raise ValueError(f"Unsupported bandwidth tier prefix '{prefix}'. Supported tiers: HOT, COLD, ARCHIVE")

    return tier_rates[prefix]


def main():
    print("==== Running parse_storage_quota ====")
    q_input = input("Enter quota (e.g. 500MB, 10GB, 2TB): ")
    try:
        print(parse_storage_quota(q_input))
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")

    print("\n==== Running compute_compression_ratio ====")
    c_input = input("Enter raw:compressed bytes (e.g. 1024:256): ")
    try:
        print("Compression Ratio:", compute_compression_ratio(c_input))
    except (ValueError, TypeError, ZeroDivisionError) as e:
        print(f"Error: {e}")

    print("\n==== Running lookup_bandwidth_tier_rate ====")
    t_input = input("Enter tier descriptor (e.g. HOT_TIER, COLD, ARCHIVE): ")
    try:
        print("Rate per GB: $", lookup_bandwidth_tier_rate(t_input))
    except (ValueError, TypeError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
