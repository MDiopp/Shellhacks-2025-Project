# civic_agents/locations.py (add)
def guess_seeds_for_domain(base: str) -> list[str]:
    base = base.rstrip("/")
    seeds = []
    for paths in CATEGORY_PATHS.values():
        for p in paths:
            seeds.append(f"{base}/{p}")
    # Always include homepage for link discovery
    seeds.append(base + "/")
    # de-dup
    return list(dict.fromkeys(seeds))
