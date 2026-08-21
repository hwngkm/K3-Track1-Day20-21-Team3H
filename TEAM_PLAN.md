# Kế hoạch Phân công & Lộ trình Thực hiện Capstone AI Evaluation (Team 3H)

Tài liệu chi tiết về phân công công việc, checkpoint, phương pháp kiểm thử, kết quả đầu ra (deliverables) và phân định việc làm chung / làm riêng cho nhóm 3 người.

---

## 1. Đánh giá tính công bằng (Workload & Time Balance)

| Tiêu chí | Thành viên A (Data & PM Lead) | Thành viên B (Pipeline & Code) | Thành viên C (Judge & Calibration) |
|---|---|---|---|
| **Số nhiệm vụ Solo** | 6 nhiệm vụ | 7 nhiệm vụ | 7 nhiệm vụ |
| **Số phiên làm chung** | 5 phiên (đồng chủ trì) | 5 phiên (tham gia) | 5 phiên (tham gia) |
| **Thời gian làm riêng** | ~180 – 210 phút | ~180 – 210 phút | ~180 – 210 phút |
| **Thời gian làm chung** | ~165 phút | ~165 phút | ~165 phút |
| **Tổng thời gian ước tính** | **~5.5 – 6.0 giờ** | **~5.5 – 6.0 giờ** | **~5.5 – 6.0 giờ** |
| **Độ phức tạp (Cognitive Load)** | Cao (Thiết kế Grid, PM Verdict, Gate) | Cao (Pipeline, Code Checks, Tracing) | Cao (Prompt Eng, Calibration, Error Analysis) |

> **Kết luận:** Khối lượng công việc và thời gian thực hiện đã được cân bằng chính xác giữa 3 thành viên, không có tình trạng dồn việc hay phụ thuộc một chiều.

---

## 2. Việc Làm Chung (Cả 3 thành viên)

1. **Phiên 1 - Brainstorming Input Grid (CP1 - ~30m):** Thống nhất User Personas x Intent Matrix & ranh giới in/out scope.
2. **Phiên 2 - Chấm nhãn độc lập & Chốt "Nhãn Vàng" (CP2 - ~60m):**
   - 3 người tự chấm 100% câu hỏi trên `report.html` độc lập -> xuất `labels-a.csv`, `labels-b.csv`, `labels-c.csv`.
   - Chạy `eval/agreement.py` đo % đồng thuận, cùng thảo luận giải quyết các case bất đồng để chốt `labels.csv`.
3. **Phiên 3 - Thống nhất Rubric v1 & Tiêu chí Blocker (CP3 - ~25m):** Định nghĩa chuẩn Pass/Fail, tiêu chí Blocker vs Điểm cộng.
4. **Phiên 4 - Thảo luận Quyết định Gate & PM Verdict (CP5, CP6 - ~30m):** Thống nhất Ship / Hold, điều kiện Release và kế hoạch Monitoring.
5. **Phiên 5 - Review chéo & Đóng gói bài nộp (CP6 - ~20m):** Kiểm tra tính nhất quán số liệu và ký duyệt `ai-support-log.md`.

---

## 3. Việc Làm Riêng & Phân công theo Checkpoint (CP1 → CP6)

### 📌 CHECKPOINT 1: Coverage & Dataset v1
* **Thành viên A (Chủ trì):** Thiết kế Input Grid; viết 12-15 câu In-scope & Slide context; chuẩn hóa `dataset.jsonl` và `deliverables/evidence/dataset-v1.jsonl`; viết Mục 1 & 2 trong `deliverables/REPORT.md`.
* **Thành viên B:** Viết 10-12 câu Out-of-scope & Edge cases.
* **Thành viên C:** Viết 10-12 câu Adversarial (xin đáp án, prompt injection).
* **Kiểm thử:** `$env:PYTHONUTF8=1; python tests/test_eval_kit.py` (44 tests pass).
* **Đầu ra:** `dataset.jsonl`, `deliverables/evidence/dataset-v1.jsonl`, `REPORT.md` (Mục 1, 2).

---

### 📌 CHECKPOINT 2: Human Baseline & Agreement
* **Thành viên B (Kỹ thuật):** Setup `.env` + Tracing (Braintrust/LangSmith); chạy `python eval/run_eval.py` -> `results-v1.jsonl`; chạy `python eval/report.py` sinh `report.html`; tạo `deliverables/evidence/braintrust-link.md`.
* **Cả 3 thành viên:** Chấm độc lập trên `report.html` -> xuất `labels-a.csv`, `labels-b.csv`, `labels-c.csv`.
* **Thành viên A (Điều phối):** Chạy `python eval/agreement.py` đo đồng thuận; chủ trì chốt `deliverables/evidence/labels.csv`.
* **Kiểm thử:** `$env:PYTHONUTF8=1; python eval/agreement.py labels-a.csv labels-b.csv labels-c.csv`
* **Đầu ra:** `results-v1.jsonl`, 3 file `labels-*.csv`, `labels.csv`, `braintrust-link.md`, `REPORT.md` (Mục 7.2).

---

### 📌 CHECKPOINT 3: Rubric v1 & Routing Map
* **Thành viên C (Chủ trì Rubric):** Soạn thảo chi tiết các tiêu chí Pass/Fail, ví dụ minh họa và quy định Blocker; điền Mục 3 trong `REPORT.md`.
* **Thành viên A & B (Routing Map):** Xây dựng bảng Routing Map (Code vs LLM Judge vs Human Audit) kèm lý do kỹ thuật; điền Mục 4 trong `REPORT.md`.
* **Đầu ra:** `deliverables/REPORT.md` (Mục 3, 4 hoàn chỉnh).

---

### 📌 CHECKPOINT 4: Code Checks & Judge Calibration (v1 → v2)
* **Thành viên B (Làn Code):** Mở rộng `eval/code_checks.py` thêm 1-2 rule kiểm tra logic (format followup, valid scope values).
* **Thành viên C (Làn Judge):** 
  - Vòng 1: Tạo `judge-prompt-v1.md`, chạy `python eval/judge.py` -> `verdicts-v1.jsonl`, đọc Confusion Matrix v1.
  - Vòng 2: Phân tích ca sai (FP/FN), tinh chỉnh thành `judge-prompt-v2.md`, chạy lại `judge.py` -> `verdicts-v2.jsonl`, đọc Confusion Matrix v2.
* **Thành viên A:** Tổng hợp và điền Mục 5 (Calibration Report) trong `REPORT.md`.
* **Kiểm thử:**
  - Code: `$env:PYTHONUTF8=1; python eval/code_checks.py`
  - Judge: `$env:PYTHONUTF8=1; python eval/judge.py`
* **Đầu ra:** `eval/code_checks.py`, `judge-prompt-v1.md`, `judge-prompt-v2.md`, `verdicts-v1.jsonl`, `verdicts-v2.jsonl`, `REPORT.md` (Mục 5).

---

### 📌 CHECKPOINT 5: Scorecard & Quality Gate
* **Thành viên B:** Trích xuất số liệu kỹ thuật: Latency trung bình/P95, số lượng Prompt/Completion Tokens, tổng chi phí ($ USD).
* **Thành viên A & C:** Lập bảng Scorecard (Pass/Fail/Uncertain từng tiêu chí); thiết lập ngưỡng Quality Gate (ngưỡng Ship / Hold) và chỉ ra các điểm rủi ro lớn nhất; điền Mục 6 trong `REPORT.md`.
* **Đầu ra:** `deliverables/REPORT.md` (Mục 6 hoàn chỉnh).

---

### 📌 CHECKPOINT 6: PM Verdict & Final Evidence Pack
* **Thành viên A:** Viết Mục 7 (Verdict + Report 5 phần) dưới góc nhìn Product Manager; trả lời 4 câu hỏi tự soi.
* **Thành viên B & C:** Rà soát toàn bộ thư mục `deliverables/evidence/` đủ 11 file; điền `deliverables/ai-support-log.md`.
* **Cả 3 thành viên:** Cập nhật thông tin nhóm trong `README.md`, chạy test cuối cùng trước khi bàn giao.
* **Kiểm thử:** `$env:PYTHONUTF8=1; python tests/test_eval_kit.py`
* **Đầu ra:** Toàn bộ thư mục `deliverables/` hoàn tất, sẵn sàng bàn giao.
