# 高考三級-法制考古題下載任務

本次任務範圍為高點法律網公開考古題頁面中的「高考三級-法制」。

- 來源頁面：https://lawyer.get.com.tw/exam/List.aspx?iPageNo=1&sFilter=%e9%ab%98%e8%80%83%e4%b8%89%e7%b4%9a-%e6%b3%95%e5%88%b6&sFilterType=0
- 年度範圍：114 年至 105 年
- 科目：民法、民事訴訟法與刑事訴訟法、行政法、刑法
- 命名規則：`OO年-科目.pdf`
- 本次執行日期：2026-06-15

## 本次狀態

已從公開頁面確認 40 個符合條件的年度與科目項目。由於目前執行環境直連 `lawyer.get.com.tw` 與 `fd.get.com.tw` 題檔下載端時回傳 403，且瀏覽器工具讀取 PDF 入口時出現 timeout、429 或安全開啟限制，因此本次未把 PDF 題檔直接寫入 repo。

已改用 fallback 方式提交下列可重跑成果：

- `manifests/gaokao3_legal_114-105_manifest.csv`：40 筆下載清單、來源頁、預期檔名、狀態與備註。
- `scripts/download_gaokao3_legal.py`：可重跑的下載腳本，會讀取 manifest，嘗試解析來源頁中的 `Download.ashx` 入口並下載 PDF。
- `outputs/gaokao3_legal_114-105_summary.md`：本次整理與缺漏摘要。

## 使用方式

在可連外且可正常存取高點下載端的環境中執行：

```bash
python scripts/download_gaokao3_legal.py \
  --manifest manifests/gaokao3_legal_114-105_manifest.csv \
  --output-dir outputs/gaokao3_legal_pdfs
```

腳本會：

1. 讀取 manifest 中的年度、科目與來源頁。
2. 若 manifest 已有可用下載 URL，優先使用。
3. 若尚未解析下載 URL，重新抓取來源頁並比對考試類組、科目與年度。
4. 依命名規則輸出 PDF，例如 `114年-民法.pdf`。
5. 在輸出資料夾內寫入 `download_report.csv`，記錄成功、缺漏或失敗原因。

## 注意

manifest 中狀態為 `listed_pending_download` 表示已在公開清單中確認有該筆資料，但本環境未能直接下載 PDF。狀態為 `download_url_observed` 表示本次工具曾成功開啟或看到該下載入口，但仍未在容器內完成檔案下載。
