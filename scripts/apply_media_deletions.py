import json
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    plan_path = Path("scripts/media_to_delete.json")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    rows = plan.get("rows", [])

    # Snapshot URL counts before edits so we can verify exact decrements.
    before_counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        file_path = Path(row["file"])
        url = row["url"]
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        before_counts[(row["file"], url)] = text.count(url)

    by_file: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_file[row["file"]].append(row)

    errors: list[str] = []
    for file_name, file_rows in by_file.items():
        path = Path(file_name)
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        for row in file_rows:
            line_index = int(row["line"]) - 1
            if line_index < 0 or line_index >= len(lines):
                errors.append(f"OUT_OF_RANGE {file_name}:{row['line']}")
                continue
            if row["url"] not in lines[line_index]:
                errors.append(f"URL_MISMATCH {file_name}:{row['line']}")

    if errors:
        print(f"ABORTED_VALIDATION_ERRORS: {len(errors)}")
        for err in errors[:30]:
            print(err)
        return 1

    removed = 0
    for file_name, file_rows in by_file.items():
        path = Path(file_name)
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        for row in sorted(file_rows, key=lambda item: int(item["line"]), reverse=True):
            line_index = int(row["line"]) - 1
            del lines[line_index]
            removed += 1
        path.write_text("".join(lines), encoding="utf-8", newline="")

    expected_decrements: Counter[tuple[str, str]] = Counter(
        (row["file"], row["url"]) for row in rows
    )
    failures: list[tuple[str, int, int, int]] = []
    for key, expected in expected_decrements.items():
        file_name, url = key
        after = Path(file_name).read_text(encoding="utf-8", errors="ignore").count(url)
        before = before_counts[key]
        if before - after != expected:
            failures.append((file_name, expected, before, after))

    print(f"FILES_CHANGED: {len(by_file)}")
    print(f"ROWS_REMOVED: {removed}")
    print(f"VERIFY_DECREMENT_FAILURES: {len(failures)}")
    for file_name, expected, before, after in failures[:20]:
        print(
            f"FAIL {file_name} expected_dec={expected} before={before} after={after}"
        )

    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
