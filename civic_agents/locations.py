def guess_seeds_for_domain(base: str) -> list[str]:
    base = base.rstrip("/")
    seeds = []
    for paths in CATEGORY_PATHS.values():
        for p in paths:
            seeds.append(f"{base}/{p}")
    seeds.append(base + "/")
    return list(dict.fromkeys(seeds))
