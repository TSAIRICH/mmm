#!/usr/bin/env python3
"""Verify and download Taiwan exam papers from Highpoint public listings."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"
DOWNLOAD_LINK_RE = re.compile(r"<a[^>]+href=[\"']([^\"']*Download\.ashx[^\"']*)[\"'][^>]*>(.*?)</a>", re.I | re.S)


def fetch_text(url: str, timeout: int) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
    for encoding in ("utf-8", "big5", "cp950"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def fetch_bytes(url: str, timeout: int) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def normalize(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def candidate_downloads(page_html: str, source_url: str) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    for match in DOWNLOAD_LINK_RE.finditer(page_html):
        start = max(0, match.start() - 500)
        end = min(len(page_html), match.end() + 500)
        context = re.sub(r"<[^>]+>", " ", page_html[start:end])
        context = html.unescape(re.sub(r"\s+", " ", context))
        candidates.append((context, urljoin(source_url, html.unescape(match.group(1)))))
    return candidates


def find_download_url(page_html: str, source_url: str, exam: str, roc_year: str, subject: str) -> str | None:
    wanted = [normalize(exam), normalize(str(roc_year)), normalize(subject)]
    for context, url in candidate_downloads(page_html, source_url):
        if all(item in normalize(context) for item in wanted):
            return url
    return None


def read_manifest(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        rows: list[dict[str, str]] = []
        for task in data["tasks"]:
            for year in task["years"]:
                for subject in task["subjects"]:
                    rows.append({
                        "task": task["task"],
                        "exam": task["exam"],
                        "roc_year": str(year),
                        "subject": subject,
                        "source_page": task["source_page"],
                        "download_url": "",
                        "expected_filename": f"{year}年-{subject}.pdf",
                        "status": task.get("default_status", "pending_source_verification"),
                        "notes": task.get("note", ""),
                    })
        return rows
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(manifest: Path, output_dir: Path, timeout: int, delay: float) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_manifest(manifest)
    pages: dict[str, str] = {}
    report: list[dict[str, str]] = []
    for row in rows:
        source_page = row["source_page"]
        download_url = row.get("download_url") or ""
        error = ""
        try:
            if not download_url:
                if source_page not in pages:
                    pages[source_page] = fetch_text(source_page, timeout)
                    time.sleep(delay)
                download_url = find_download_url(pages[source_page], source_page, row["exam"], row["roc_year"], row["subject"]) or ""
            if not download_url:
                status = "not_found"
            else:
                data = fetch_bytes(download_url, timeout)
                if not data.startswith(b"%PDF"):
                    raise ValueError("downloaded content is not a PDF")
                (output_dir / row["expected_filename"]).write_bytes(data)
                status = "downloaded"
                time.sleep(delay)
        except Exception as exc:
            status = "download_failed" if download_url else "source_fetch_failed"
            error = str(exc)
        report.append({**row, "resolved_download_url": download_url, "final_status": status, "error": error})
        print(f"{row['roc_year']} {row['subject']}: {status}")
    write_report(output_dir / "download_report.csv", report)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--delay", type=float, default=0.5)
    args = parser.parse_args()
    run(args.manifest, args.output_dir, args.timeout, args.delay)


if __name__ == "__main__":
    main()
