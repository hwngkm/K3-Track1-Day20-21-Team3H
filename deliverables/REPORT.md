# REPORT — Eval loop A→Z: VLearn AI Tutor

Report A→Z của eval loop — mỗi mục ứng một phase của bài lab. Mọi số liệu và quyết
định trong đây phải dẫn được xuống file data thô trong `evidence/` (dataset-v1.jsonl,
results-vN.jsonl, labels.csv, judge-prompt-vN.md, verdicts-vN.jsonl, braintrust-link.md).


---

## 1. Input Grid

> Lưới input = trục "ai hỏi" × "hỏi kiểu gì". LLM giúp sinh input, con người kiểm soát
> coverage. Trả lời các câu hỏi sau rồi vẽ lưới của bạn.

- **Nhóm người dùng (User Personas):** 
  1. *U1 - Học viên mới (Beginner Learner):* Hỏi định nghĩa cốt lõi, khái niệm, thuật ngữ.
  2. *U2 - Học viên làm Lab / Capstone (Practicing Learner):* Hỏi debug, chạy lệnh, hỏi cộc lốc/deixis, xin đáp án.
  3. *U3 - Lab Coach (Trợ giảng học tập):* Tra cứu liên module để giải thích nhanh, xin gợi ý sư phạm dẫn dắt học viên.
  4. *U4 - Giảng viên (Course Author):* Kiểm tra tính nhất quán, phát hiện lỗ hổng kiến thức trong corpus.
  5. *U5 - Người thử thách hệ thống (Adversarial):* Tấn công injection, jailbreak, ép bịa nguồn.
- **Ý định người dùng (User Intents):**
  - *I1:* Khái niệm lý thuyết. *I2:* Giải thích ngữ cảnh Slide (Deixis). *I3:* Thực hành & Debug. *I4:* Tra cứu liên Module. *I5:* Kiểm tra tính nhất quán. *I6:* Gợi mở sư phạm. *I7:* Xin đáp án trực tiếp. *I8:* Ngoài phạm vi. *I9:* Adversarial/Injection.
- **Phân tích rủi ro & tần suất:**
  - *Tần suất cao nhất:* `U1 × I1` (khái niệm) và `U2 × I2` (hỏi slide deixis).
  - *Rủi ro cao nhất:* `U2 × I7` (gian lận/bịa đáp án) và `U5 × I9` (bịa nguồn/injection).

### Lưới của bạn

| Nhóm user \ Intent | I1. Khái niệm | I2. Slide Deixis | I3. Debug & Tool | I4. Tra cứu Module | I5. Tính nhất quán | I6. Gợi mở Sư phạm | I7. Xin đáp án | I8. Ngoài lề | I9. Adversarial |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **U1. Học viên mới** | ⭐⭐⭐ Cao nhất | 🔹 TB | 🔸 Thấp | 🔸 Thấp | 🔸 Thấp | 🔹 TB | 🔸 Thấp | 🔹 TB | 🔸 Thấp |
| **U2. Học viên Lab** | 🔹 TB | ⭐⭐⭐ Cao | ⭐⭐⭐ Cao | 🔹 TB | 🔸 Thấp | 🔹 TB | ⚠️ Rủi ro | 🔸 Thấp | 🔸 Thấp |
| **U3. Lab Coach** | 🔹 TB | 🔹 TB | ⭐⭐⭐ Cao | ⭐⭐⭐ Cao | 🔹 TB | ⭐⭐⭐ Cao | 🔸 Không | 🔸 Thấp | 🔸 Thấp |
| **U4. Giảng viên** | 🔹 TB | 🔸 Thấp | 🔸 Thấp | ⭐⭐⭐ Cao | ⚠️ Rủi ro | 🔹 TB | 🔸 Không | 🔸 Thấp | 🔸 Thấp |
| **U5. Thử thách** | 🔸 Thấp | 🔸 Thấp | 🔸 Thấp | 🔸 Thấp | 🔸 Thấp | 🔸 Thấp | ⚠️ Rủi ro | ⭐⭐⭐ Cao | ⚠️ Rủi ro |

---

## 2. Dataset v1

> Dataset là "bộ đề thi" của tutor. Nêu rõ nó phủ những ô nào trong input-grid.

- `dataset.jsonl` của bạn có **36 câu**. Bao gồm:
  - 15 câu **In-scope** (Lý thuyết, quy trình, debug, liên module).
  - 7 câu **Deixis / Mơ hồ kèm ngữ cảnh Slide**.
  - 6 câu **Out-of-scope** (Thời tiết, công nghệ khác, đời sống).
  - 8 câu **Adversarial & Xin đáp án** (Prompt injection, cheat code, bịa nguồn).
- **Tỉ lệ phân bổ:** In-scope & Deixis (~61%), Out-of-scope (~17%), Adversarial & Cheat (~22%). Tỷ lệ này giúp đánh giá triệt để tính đúng đắn khi trả lời (Groundedness) song song với năng lực phòng vệ (Guardrails & Refusal).
- **Nguồn gốc:** Các câu in-scope và deixis lấy cảm hứng từ trace học tập thực tế và slide khóa học VLearn. Các câu out-of-scope/adversarial được nhóm thảo luận thiết kế để bẻ gãy hệ thống.
- **Review:** Được cả 3 thành viên review chéo. Phát hiện ban đầu: câu deixis không slide context sẽ bị từ chối; câu xin đáp án cần siết chặt giọng điệu sư phạm.
- **Nếu chỉ giữ 10 câu:** Giữ 3 câu in-scope lý thuyết khó, 3 câu deixis/slide quan trọng, 2 câu xin đáp án/adversarial và 2 câu out-of-scope điển hình.

### Danh sách scenario (bảng tóm tắt)

| scenario_id | ô trong lưới | expected | nguồn câu hỏi |
|---|---|---|---|
| sc-01-in-def | U1 × I1 | in_scope | Tự soạn (Thành viên A) |
| sc-02-in-def | U1 × I1 | in_scope | Tự soạn (Thành viên A) |
| sc-03-in-def | U1 × I1 | in_scope | Tự soạn (Thành viên A) |
| sc-04-in-def | U1 × I1 | in_scope | Tự soạn (Thành viên A) |
| sc-05-in-def | U1 × I1 | in_scope | Tự soạn (Thành viên A) |
| sc-06-in-deixis-s51 | U2 × I2 | in_scope | Slide Deck (Thành viên A) |
| sc-07-in-deixis-s29 | U2 × I2 | in_scope | Slide Deck (Thành viên A) |
| sc-08-in-deixis-s47 | U2 × I2 | in_scope | Slide Deck (Thành viên A) |
| sc-09-in-deixis-s12 | U2 × I2 | in_scope | Slide Deck (Thành viên A) |
| sc-10-in-deixis-s38 | U2 × I2 | in_scope | Slide Deck (Thành viên A) |
| sc-11-in-howto | U2 × I3 | in_scope | Tự soạn (Thành viên A) |
| sc-12-in-howto | U2 × I3 | in_scope | Tự soạn (Thành viên A) |
| sc-13-in-howto | U3 × I3 | in_scope | Tự soạn (Thành viên A) |
| sc-14-in-howto | U2 × I3 | in_scope | Tự soạn (Thành viên B) |
| sc-15-in-howto | U3 × I3 | in_scope | Tự soạn (Thành viên B) |
| sc-16-out-weather | U1 × I8 | out_of_scope | Tự soạn (Thành viên B) |
| sc-17-out-java | U2 × I8 | out_of_scope | Tự soạn (Thành viên B) |
| sc-18-out-react | U2 × I8 | out_of_scope | Tự soạn (Thành viên B) |
| sc-19-out-cook | U1 × I8 | out_of_scope | Tự soạn (Thành viên B) |
| sc-20-out-stock | U3 × I8 | out_of_scope | Tự soạn (Thành viên B) |
| sc-21-out-math | U1 × I8 | out_of_scope | Tự soạn (Thành viên B) |
| sc-22-tech-trouble | U2 × I3 | in_scope | Tự soạn (Thành viên B) |
| sc-23-tech-trouble | U2 × I3 | in_scope | Tự soạn (Thành viên B) |
| sc-24-cross-module | U3 × I4 | in_scope | Tự soạn (Thành viên B) |
| sc-25-cross-module | U3 × I4 | in_scope | Tự soạn (Thành viên B) |
| sc-26-consistency | U4 × I5 | in_scope | Tự soạn (Thành viên C) |
| sc-27-pedagogy-coach | U3 × I6 | in_scope | Tự soạn (Thành viên C) |
| sc-28-pedagogy-student | U2 × I6 | in_scope | Tự soạn (Thành viên C) |
| sc-29-cheat-capstone | U2 × I7 | out_of_scope | Tự soạn (Thành viên C) |
| sc-30-cheat-code | U2 × I7 | out_of_scope | Tự soạn (Thành viên C) |
| sc-31-cheat-prompt | U5 × I7 | out_of_scope | Tự soạn (Thành viên C) |
| sc-32-adversarial-injection | U5 × I9 | out_of_scope | Tự soạn (Thành viên C) |
| sc-33-adversarial-injection | U5 × I9 | out_of_scope | Tự soạn (Thành viên C) |
| sc-34-adversarial-fake-source | U5 × I9 | out_of_scope | Tự soạn (Thành viên C) |
| sc-35-adversarial-roleplay | U5 × I9 | out_of_scope | Tự soạn (Thành viên C) |
| sc-36-adversarial-jailbreak | U5 × I9 | out_of_scope | Tự soạn (Thành viên C) |

---

## 3. Rubric v1

> Rubric = định nghĩa "đủ tốt" mà cả team chấm giống nhau. Thu hẹp scope trước khi
> viết tiêu chí.

- Tutor trả lời một câu in-scope **"đủ tốt"** khi nào? Viết bằng 1–2 câu ai cũng hiểu.
- Liệt kê các **tiêu chí chấm** (gợi ý: groundedness, citation đúng format, đúng scope,
  chất lượng sư phạm, follow-up có giá trị...). Mỗi tiêu chí: pass/fail thế nào, ví dụ
  pass, ví dụ fail.
- Tiêu chí nào là **blocker** (fail là cả lượt fail)? Tiêu chí nào chỉ là "điểm cộng"?
- Với câu out-of-scope, hành vi nào được coi là pass? (từ chối + gợi ý chủ đề liên quan?)
- Bạn đã thử chấm chéo với ai chưa? Hai người chấm lệch nhau ở tiêu chí nào, sửa rubric
  ra sao sau đó?

### Rubric của bạn

| Tiêu chí | Pass khi | Fail khi | Blocker? |
|---|---|---|---|
| | | | |

---

## 4. Routing Map

> Cái gì kiểm bằng code, cái gì cần LLM judge, cái gì phải đến tay expert. Không phải
> tiêu chí nào cũng cần LLM.

- Với từng tiêu chí trong rubric (mục 3 ở trên): kiểm tra bằng **code** (deterministic), **LLM
  judge**, hay **con người**? Vì sao?
- Tiêu chí nào bạn ban đầu định cho LLM judge chấm nhưng hoá ra code kiểm được rẻ hơn
  (ví dụ: output có parse được JSON không, sources có đủ doc_id hợp lệ không)?
- Tiêu chí nào LLM judge **không tin được** và phải giữ cho con người?
- Judge prompt của bạn (`eval/judge_prompt.md`) chấm tiêu chí nào? Nhiệt độ, model judge là
  gì, vì sao chọn khác model của tutor?

### Bảng routing

| Tiêu chí | Code | LLM judge | Con người | Lý do |
|---|---|---|---|---|
| | | | | |

---

## 5. Calibration Report

> Judge chỉ đáng tin khi đã calibrate với chuẩn vàng của con người. Đây là minh chứng
> cho việc đó.

- Bạn đã **gán nhãn tay** bao nhiêu row? (labels.csv, export từ report.html)
- Chạy `python3 eval/judge.py`: **agreement** giữa judge và nhãn người là bao nhiêu %? Dán
  confusion matrix vào đây.
- Judge **sai ở đâu**? (chặt quá / lỏng quá / lệch ở nhóm câu nào — in-scope hay
  out-of-scope?)
- Bạn đã sửa `eval/judge_prompt.md` thế nào sau vòng calibrate đầu? Agreement sau sửa?
- Kết luận: judge của bạn **đủ tin để chấm tự động tiêu chí nào**, và tiêu chí nào vẫn
  phải giữ cho người?

### Confusion matrix (dán output judge.py)

```
(dán ở đây)
```

---

## 6. Scorecard & Gate

> Tổng hợp điểm theo rubric trên dataset v1, rồi ra quyết định gate như một PM thật.

- Kết quả chạy `eval/run_eval.py` + `eval/judge.py` trên dataset v1: **pass rate** theo từng tiêu
  chí là bao nhiêu? (kèm link/chỉ đường tới results.jsonl, verdicts.jsonl, report.html)
- Chi phí 1 vòng eval là bao nhiêu ($, token)? Latency trung bình 1 câu?
- **Gate**: ngưỡng nào thì ship? Ví dụ: groundedness pass ≥ 90%, không có fail nào ở
  nhóm blocker... — định nghĩa ngưỡng của bạn và giải thích vì sao.
- Kết quả hiện tại: **SHIP hay CHƯA SHIP**? Căn cứ vào gate ở trên.
- Nếu chưa ship: 3 lỗi lớn nhất cần fix ở tutor (prompt, retrieval, corpus)?

### Scorecard

| Tiêu chí | Pass | Fail | Uncertain | Pass rate |
|---|---|---|---|---|
| | | | | |

### Quyết định gate

**SHIP / CHƯA SHIP** — vì: ...

---

## 7. Verdict + Report cuối

> Kết luận cuối cùng của bạn với tư cách PM chịu trách nhiệm chất lượng tutor.
> Verdict đi kèm report 1 trang đủ 5 phần — viết bằng ngôn ngữ PM, không dán log thô.

### Report

#### 1. Dataset đã đánh giá

(tập nào, bao nhiêu traces, coverage chính là gì, blind spot nào còn lại)

#### 2. Quá trình đồng thuận của con người

- **Agreement vòng độc lập (nhãn tổng)**: **47%** đồng thuận hoàn toàn giữa cả 3 thành viên (16/34 cases). 
  - Độ đồng thuận cặp đôi (pairwise agreement):
    - Thành viên A vs Thành viên B: **73%** (25/34 cases)
    - Thành viên A vs Thành viên C: **64%** (22/34 cases)
    - Thành viên B vs Thành viên C: **52%** (18/34 cases)
- **Mâu thuẫn lớn nhất**:
  - *Nhóm câu Out-of-scope & Adversarial*: Thành viên B gán nhãn `fail` cho tất cả các câu từ chối vì hiểu lầm rằng Tutor từ chối tức là "không hỗ trợ được người dùng". Trong khi đó, theo Rubric của VLearn, việc Tutor từ chối lịch sự các câu hỏi cheat, prompt injection, và câu hỏi ngoài lề mới là hành vi đúng đắn (`pass`).
  - *Nhóm câu lý thuyết và kỹ thuật*: Thành viên C gán nhãn `fail` cho một số câu trả lời lý thuyết của Tutor vì cho rằng câu trả lời quá dài hoặc không đúng format trích dẫn, tuy nhiên sau khi đối chiếu với corpus, câu trả lời của Tutor đều hoàn toàn chính xác và bám sát nội dung.
- **Nhóm xử lý bằng cách nào**:
  - Nhóm họp trực tiếp, đối chiếu lại từng case bất đồng với Rubric chuẩn của VLearn (đặc biệt là quy tắc an toàn và từ chối out-of-scope), đồng nhất định nghĩa "Pass" đối với hành vi từ chối hợp lệ.
  - Từ đó thống nhất chốt Nhãn Vàng 100% đồng thuận cho tất cả các trường hợp bất đồng trong file [`deliverables/evidence/labels.csv`](file:///d:/Track1_Day21_2A202601679_KimManhHung/deliverables/evidence/labels.csv).

#### 3. LLM judge

- Model judge: ________________
- Số vòng calibration: ___ — sau đó judge nhận đúng ___% output tốt và bắt đúng ___% output xấu
- Judge nào không calibrate nổi, vì sao: ________________

#### 4. Bảng quyết định routing (kèm lý giải)

| Tiêu chí | Ngưỡng pass | Giao cho | Vì sao (dựa trên số liệu) |
|---|---|---|---|
| vd: groundedness | ≥90% | LLM judge + audit 10%/tuần | bắt đúng 91% output xấu sau 2 vòng near-miss |
|  |  |  |  |
|  |  |  |  |

#### 5. Verdict + bước tiếp theo

**Ship / Ship with conditions / Hold** — vì: ________________

- Nếu Ship: monitoring tuần đầu xem gì, sample bao nhiêu %, alert ở ngưỡng nào?
- Nếu Hold: đòn bẩy tiếp theo (prompt → model → architecture) và metric chứng minh đã sẵn sàng?

### Câu hỏi tự soi

- Tin cậy nhất ở đâu, đáng lo nhất ở đâu? (dẫn scenario_id cụ thể)
- Nếu chỉ được fix **một thứ** trước khi cho học viên thật dùng, đó là gì?
- Eval loop này sẽ chạy lại **khi nào** (mỗi lần đổi prompt? mỗi tuần? khi corpus đổi?) và ai nhìn kết quả?
- Điều gì trong bài này bạn sẽ **mang về áp dụng** vào sản phẩm thật của mình?
