# 台灣國考考古題下載整理

本 repo 用於整理公開網站上的國考考古題下載任務、manifest、可重跑腳本與執行摘要。

## 已整理任務

### 高考三級-法制

- 年度：114 年至 105 年
- 科目：民法、民事訴訟法與刑事訴訟法、行政法、刑法
- 來源頁面：https://lawyer.get.com.tw/exam/List.aspx?iPageNo=1&sFilter=%e9%ab%98%e8%80%83%e4%b8%89%e7%b4%9a-%e6%b3%95%e5%88%b6&sFilterType=0
- 既有成果：
  - `manifests/gaokao3_legal_114-105_manifest.csv`
  - `scripts/download_gaokao3_legal.py`
  - `outputs/gaokao3_legal_114-105_summary.md`

### 地方政府特考三等-法制

- 年度：114 年至 105 年
- 科目：民法、民事訴訟法與刑事訴訟法、行政法、刑法
- 來源頁面：https://lawyer.get.com.tw/exam/List.aspx?iPageNo=1&sFilter=%e5%9c%b0%e6%96%b9%e6%94%bf%e5%ba%9c%e7%89%b9%e8%80%83%e4%b8%89%e7%ad%89-%e6%b3%95%e5%88%b6&sFilterType=0
- 本次 fallback 成果：
  - `manifests/remaining_default_tasks_manifest.json`
  - `scripts/download_exam_papers.py`
  - `outputs/remaining_default_tasks_summary.md`

### 特考三等-司法人員(法院書記官)

- 年度：114 年至 105 年
- 科目：民法概要、刑法概要、民事訴訟法概要與刑事訴訟法概要、行政法概要
- 來源頁面：https://lawyer.get.com.tw/exam/List.aspx?iPageNo=1&sFilter=%e7%89%b9%e8%80%83%e4%b8%89%e7%ad%89-%e5%8f%b8%e6%b3%95%e4%ba%ba%e5%93%a1%28%e6%b3%95%e9%99%a2%e6%9b%b8%e8%a8%98%e5%ae%98%29&sFilterType=0
- 本次 fallback 成果：
  - `manifests/remaining_default_tasks_manifest.json`
  - `scripts/download_exam_papers.py`
  - `outputs/remaining_default_tasks_summary.md`

## 命名規則

下載後的 PDF 檔名主體統一使用：

```text
OO年-科目.pdf
```

例如：

```text
114年-民法.pdf
114年-民事訴訟法與刑事訴訟法.pdf
```

## 本次 GitHub fallback 狀態

2026-06-15 本次執行時，外部來源頁與題檔下載端在目前容器環境回傳：

```text
CONNECT tunnel failed, response 403
```

因此未將 PDF 題檔標示為已下載，也未把未驗證題檔寫入 repo。已改為建立完整預期 manifest、可重跑腳本與結果摘要。manifest 中的 `pending_source_verification` 表示該筆是使用者指定範圍內的預期項目，仍需在可連到 `lawyer.get.com.tw` 的環境中由腳本驗證來源頁與下載入口。

## 重跑方式

地方政府特考三等-法制：

```bash
python scripts/download_exam_papers.py \
  --manifest manifests/remaining_default_tasks_manifest.json \
  --output-dir outputs/local_government_legal_system_pdfs
```

特考三等-司法人員(法院書記官)：

```bash
python scripts/download_exam_papers.py \
  --manifest manifests/remaining_default_tasks_manifest.json \
  --output-dir outputs/judicial_third_clerk_pdfs
```

腳本會依 manifest 逐筆重新抓取來源頁、比對考試類別/年度/科目、解析下載入口、下載 PDF，並在輸出資料夾建立 `download_report.csv`。
