# Remaining Default Exam Download Tasks Summary

Execution date: 2026-06-15

## Scope

1. 地方政府特考三等-法制, ROC years 114 to 105, subjects: 民法, 民事訴訟法與刑事訴訟法, 行政法, 刑法.
2. 特考三等-司法人員(法院書記官), ROC years 114 to 105, subjects: 民法概要, 刑法概要, 民事訴訟法概要與刑事訴訟法概要, 行政法概要.

## Verified execution result

The current execution container could not directly fetch `lawyer.get.com.tw` pages or external question-file downloads. `curl -L` to the listed source pages returned `CONNECT tunnel failed, response 403`. No PDF files were downloaded or committed.

## GitHub fallback contents

- `manifests/remaining_default_tasks_manifest.json`: two task definitions, 80 expected year-subject items after expansion.
- `scripts/download_exam_papers.py`: reusable downloader/verifier for the two manifests.
- `outputs/remaining_default_tasks_summary.md`: this summary.

## Status definitions

- `pending_source_verification`: expected item from the requested task; the source/download page was not reachable from the current container and must be verified by rerunning the script from a reachable network.
- `downloaded`: script successfully downloaded a PDF.
- `not_found`: script could reach the source page but could not find a matching year-subject item.
- `download_failed`: script found a candidate download URL but the file download failed.

## Known exception

For the法院書記官 task, the requested exam label is `特考三等-司法人員(法院書記官)` while all requested subjects contain `概要`. The script therefore requires exact source-page verification before any item is marked downloaded.
