import argparse
import os
import re
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


RAW_RE = re.compile(
    r"^https?://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)$",
    re.IGNORECASE,
)
GITHUB_BLOB_RE = re.compile(
    r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/(?:blob|raw)/([^/]+)/(.*)$",
    re.IGNORECASE,
)


def to_cdn_url(url: str) -> str:
    if not url:
        return url
    if "cdn.jsdelivr.net/gh/" in url:
        return url

    raw_match = RAW_RE.match(url)
    if raw_match:
        user, repo, branch, rest = raw_match.groups()
        return f"https://cdn.jsdelivr.net/gh/{user}/{repo}@{branch}/{rest}"

    blob_match = GITHUB_BLOB_RE.match(url)
    if blob_match:
        user, repo, branch, rest = blob_match.groups()
        return f"https://cdn.jsdelivr.net/gh/{user}/{repo}@{branch}/{rest}"

    return url


def migrate_text(value: str | None) -> str | None:
    if value is None:
        return None

    value = re.sub(
        r"https?://raw\.githubusercontent\.com/([^/\s]+)/([^/\s]+)/([^/\s]+)/([^\s)\"']+)",
        r"https://cdn.jsdelivr.net/gh/\1/\2@\3/\4",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"https?://(?:www\.)?github\.com/([^/\s]+)/([^/\s]+)/(?:blob|raw)/([^/\s]+)/([^\s)\"']+)",
        r"https://cdn.jsdelivr.net/gh/\1/\2@\3/\4",
        value,
        flags=re.IGNORECASE,
    )
    return value


def migrate_list(items: list[str] | None) -> list[str]:
    if not items:
        return []
    return [to_cdn_url(v) for v in items]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate GitHub raw/blob media URLs in DB to jsDelivr CDN URLs."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply updates. Without this flag, runs in dry-run mode.",
    )
    args = parser.parse_args()

    load_dotenv(Path("backend/.env"))
    db_url = os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL/DIRECT_URL not found in backend/.env")

    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT key, text, photo, video, document, icon_url
                FROM guides
                """
            )
            rows = cur.fetchall()

            changed_rows = 0
            changed_fields = 0

            for key, text, photo, video, document, icon_url in rows:
                new_text = migrate_text(text)
                new_photo = migrate_list(photo)
                new_video = migrate_list(video)
                new_document = migrate_list(document)
                new_icon_url = to_cdn_url(icon_url) if icon_url else icon_url

                if (
                    new_text != text
                    or new_photo != (photo or [])
                    or new_video != (video or [])
                    or new_document != (document or [])
                    or new_icon_url != icon_url
                ):
                    changed_rows += 1
                    changed_fields += sum(
                        [
                            new_text != text,
                            new_photo != (photo or []),
                            new_video != (video or []),
                            new_document != (document or []),
                            new_icon_url != icon_url,
                        ]
                    )

                    if args.apply:
                        cur.execute(
                            """
                            UPDATE guides
                            SET text = %s,
                                photo = %s,
                                video = %s,
                                document = %s,
                                icon_url = %s,
                                updated_at = NOW()
                            WHERE key = %s
                            """,
                            (new_text, new_photo, new_video, new_document, new_icon_url, key),
                        )

            print(f"Guides scanned: {len(rows)}")
            print(f"Rows to update: {changed_rows}")
            print(f"Field updates: {changed_fields}")
            print(f"Mode: {'apply' if args.apply else 'dry-run'}")

            if args.apply:
                conn.commit()
                print("Done: changes committed.")
            else:
                conn.rollback()
                print("Dry-run complete: no changes committed.")


if __name__ == "__main__":
    main()
