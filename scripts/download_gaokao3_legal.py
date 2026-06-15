#!/usr/bin/env python3
"""Download 高考三級-法制 PDFs listed in the manifest.

The script is intentionally self-contained and uses only the Python standard
library so it can be run in a fresh environment.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, build_opener


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36"
)


def fetch_bytes(url: str, timeout: int = 30) -> tuple[bytes, str]:
    opener = build_opener()
    request = Request(url, headers={"User-Agent": USER_AGENT, "Referer": "https://lawyer.get.com.tw/"})
    with opener.open(request, timeout=timeout) as response:
        return response.read(), response.geturl()


def fetch_text(url: str) -> str:
    data, _ = fetch_bytes(url)
    for encoding in ("utf-8", "big5", "cp950"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    return html.unescape(value).strip()


def normalize(value: str) -> str:
    return re.sub(r"\s+", "", value.replace("（", "(").replace("）", ")"))


def parse_rows(page_url: str, page_html: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    row_pattern = re.compile(r"<tr[^>]*>(.*?)</tr>", re.I | re.S)
    cell_pattern = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.I | re.S)
    href_pattern = re.compile(r'href=["\']([^"\']*Download\.ashx[^"\']*)["\']', re.I)

    for row_html in row_pattern.findall(page_html):
        cells = cell_pattern.findall(row_html)
        if len(cells) < 5:
            continue
        href_match = href_pattern.search(row_html)
        rows.append(
            {
                "exam_group": strip_tags(cells[1]),
                "subject": strip_tags(cells[2]),
                "year": strip_tags(cells[3]),
                "download_url": urljoin(page_url, html.unescape(href_match.group(1))) if href_match else "",
            }
        )
    return rows


def resolve_download_url(source_page: str, exam_group: str, year: str, subject: str) -> str:
    page_html = fetch_text(source_page)
    wanted = (normalize(exam_group), normalize(subject), year)
    for row in parse_rows(source_page, page_html):
        candidate = (normalize(row["exam_group"]), normalize(row["subject"]), row["year"])
        if candidate == wanted and row["download_url"]:
            return row["download_url"]
    return ""


def download_pdf(url: str, output_path: Path) -> tuple[str, str]:
    data, final_url = fetch_bytes(url)
    if not data.startswith(b"%PDF"):
        return "failed", f"response was not a PDF; final_url={final_url}"
    output_path.write_bytes(data)
    return "downloaded", final_url


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--sleep", type=float, default=1.0, help="Delay between downloads.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "download_report.csv"

    with manifest_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    report_rows = []
    for row in rows:
        filename = row["expected_filename"]
        target = output_dir / filename
        status = "pending"
        detail = ""
        url = row.get("download_url", "").strip()

        try:
            if not url:
                url = resolve_download_url(row["source_page"], row["exam_group"], row["year"], row["subject"])
            if not url:
                status = "missing_download_url"
                detail = "Could not resolve Download.ashx from source page."
            else:
                status, detail = download_pdf(url, target)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            status = "failed"
            detail = f"{type(exc).__name__}: {exc}"

        report_rows.append(
            {
                "year": row["year"],
                "subject": row["subject"],
                "expected_filename": filename,
                "download_url": url,
                "status": status,
                "detail": detail,
            }
        )
        print(f"{row['year']} {row['subject']}: {status}", file=sys.stderr)
        time.sleep(args.sleep)

    with report_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=report_rows[0].keys())
        writer.writeheader()
        writer.writerows(report_rows)

    downloaded = sum(1 for item in report_rows if item["status"] == "downloaded")
    print(f"Downloaded {downloaded}/{len(report_rows)} PDFs. Report: {report_path}")
    return 0 if downloaded == len(report_rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
