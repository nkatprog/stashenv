"""Compare two profiles side-by-side, optionally across projects."""
from typing import Optional
from stashenv.store import load_profile
from stashenv.export import env_to_dict


def compare_profiles(
    project_dir_a: str,
    profile_a: str,
    password_a: str,
    project_dir_b: str,
    profile_b: str,
    password_b: str,
) -> dict:
    """Return a comparison report between two profiles."""
    raw_a = load_profile(project_dir_a, profile_a, password_a)
    raw_b = load_profile(project_dir_b, profile_b, password_b)
    dict_a = env_to_dict(raw_a)
    dict_b = env_to_dict(raw_b)

    all_keys = sorted(set(dict_a) | set(dict_b))
    result = {}
    for key in all_keys:
        val_a = dict_a.get(key)
        val_b = dict_b.get(key)
        if val_a is None:
            status = "only_in_b"
        elif val_b is None:
            status = "only_in_a"
        elif val_a == val_b:
            status = "equal"
        else:
            status = "differs"
        result[key] = {"a": val_a, "b": val_b, "status": status}
    return result


def format_compare(report: dict, reveal: bool = False) -> str:
    """Format the comparison report as a human-readable string."""
    lines = []
    for key, info in report.items():
        status = info["status"]
        if status == "equal":
            val = info["a"] if reveal else "***"
            lines.append(f"  = {key} = {val}")
        elif status == "differs":
            if reveal:
                lines.append(f"  ~ {key}: [{info['a']}] vs [{info['b']}]")
            else:
                lines.append(f"  ~ {key}: <differs>")
        elif status == "only_in_a":
            lines.append(f"  < {key} (only in A)")
        elif status == "only_in_b":
            lines.append(f"  > {key} (only in B)")
    return "\n".join(lines) if lines else "(no keys found)"
