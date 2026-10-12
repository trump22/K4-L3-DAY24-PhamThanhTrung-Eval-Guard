# K4 Track 3B — Production Eval + Guardrail Stack

## Bản làm cá nhân — Phạm Thanh Trung, 2A202602949

Chủ project yêu cầu làm cá nhân; đề gốc vẫn quy định bài nhóm. Bản này khai một
người trong TEAM và ghi AI hỗ trợ, không giả lập thành viên/commit của người khác.
Pipeline m1–m5 được lấy từ bài Day18 của chủ project:
[repo Day18](https://github.com/trump22/K4-Track3B-Day18-PhamThanhTrung-2A2202602949-Production-RAG).
MSSV của bài nộp này là **2A202602949**; tên repo Day18 cũ giữ nguyên để truy nguồn.

Adapter giữ giao diện runner: m4 dùng RAGAS thật với model evaluator cấu hình riêng,
embedding BGE-M3 và trả metadata; m5 chuyển sang OpenAI-compatible endpoint; m2
dùng `search` phù hợp Qdrant client 1.9.2 do đề pin, thay API `query_points` của
phiên bản mới hơn. Tasks 1–12 được implement trong ba file phase. Tests, fixtures,
runner, exporter, checker và JSON Schema giữ nguyên starter.

Trên Windows dùng Python 3.11 và constraints bổ sung để PyArrow tương thích với
NumPy 1.26.4 của đề. Cài đặt full runtime đã phát hiện PyArrow 26 yêu cầu NumPy 2
khi import, dù `pip check` không phát hiện xung đột binary đó.

```powershell
py -3.11 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements/requirements.txt -c requirements/constraints-windows.txt
.venv/Scripts/python.exe -m spacy download en_core_web_lg
docker compose -f infra/docker-compose.yml up -d
# Copy .env.example to .env and fill your credentials privately.
# For Azure, set both endpoint variables and the actual deployment names.
# Set guardrails/config.yml models.main.model to that guard deployment too.
.venv/Scripts/python.exe scripts/setup_answers.py --live
.venv/Scripts/python.exe scripts/run_experiments.py --phase a --live
.venv/Scripts/python.exe scripts/run_experiments.py --phase b --live
.venv/Scripts/python.exe scripts/run_experiments.py --phase c --live --latency-samples 20
.venv/Scripts/python.exe scripts/check_lab.py
```

Unit tests và thực nghiệm API là hai bằng chứng khác nhau. Không chạy live
integration lần nữa sau khi các runner đã sinh artifacts thật. Blueprint là đề
xuất; số đo input guard không được coi là full-guard latency. Hai PDF scan không
có text layer được loader báo bỏ qua; dữ liệu nguồn vẫn được giữ nguyên.

### Kết quả thực nghiệm ngày 12/10/2026

| Hạng mục | Kết quả lưu trong artifacts |
|---|---|
| Answers | 50/50 gọi LLM thật, phân bố 20/20/10, contexts không rỗng |
| RAGAS | Mean bốn metrics 0.818578; faithfulness 0.859167 |
| Nhóm yếu nhất | multi_hop 0.733599; factual 0.942030; adversarial 0.741632 |
| Judge calibration | 10/10 nhãn đồng ý human; Cohen's κ=1.0 |
| Input guard | 20/20 attacks blocked, 8/8 clean allowed, FPR=0 |
| Output guard | 4/4 đúng; hai output sạch giữ nguyên |
| Input latency | 20 samples + 2 warm-up; P95=1151.036ms, target500ms chưa đạt |
| Kiểm tra bản cuối | `check_lab.py --with-tests`: 86 passed, 3 deselected; 0 failed checks |

Ba integration tests được deselect mặc định; runner API đã chạy riêng. Số checks
đạt không phải điểm rubric. Guard stack dùng cả NeMo và Azure content filter:
4 attacks dừng ở Presidio, 5 bị vendor filter chặn trong stage NeMo, 11 bởi rail.
Tầng PII giới hạn định danh có mẫu để tránh English NER nhận nhầm câu tiếng Việt;
yêu cầu thông tin nhân viên được semantic rail kiểm tra. Self-check prompt khai
rõ phạm vi nội bộ để chặn cả off-topic vô hại. Xem ba báo cáo trong `doc/reports/`
về lỗi RAG/phiên bản/abstention, attribution, latency và CI/CD đề xuất.

`.gitattributes` quy định checkout CRLF cho JSON fixtures/artifacts vì metadata
SHA256 của lần chạy Windows được tính trên bytes CRLF. Nếu Git tự checkout LF
trên máy khác, checker sẽ báo hash sai dù JSON cùng nội dung. Quy tắc này giữ
hash lần chạy và không sửa nội dung fixtures hay checker. Clone bằng Git để
nhận đúng checkout rule trước chạy `scripts/check_lab.py`.


**Bài nhóm: mỗi nhóm dùng và nộp một repo chung của trưởng nhóm.**
Mỗi người khai phần thực tế đã làm trong [doc/TEAM.md](doc/TEAM.md).

**Thời lượng trên lớp:** 15 phút kiểm tra sẵn sàng + 90 phút thực hành
(Phase A/B/C, mỗi phase 30 phút). Cài dependencies, build tools, tải model,
indexing và sinh 50 answers được làm **trước buổi học**, không gộp vào 15 phút.

**Điểm:** 100 điểm bắt buộc + tối đa 10 bonus cho bài lab.

**Repo đề bài:** [K4-Track-3B-Day24-Eval-Guard](https://github.com/VinUni-AI20k/K4-Track-3B-Day24-Eval-Guard).
Repo bài nộp nhóm: `K4-L3-DAY24-TenNhom-Eval-Guard`.

## Cấu trúc repo

- `src/`: hàm bài tập TODO và phần hỗ trợ.
- `scripts/`: setup, runner và checker; chạy từ gốc repo.
- `fixtures/`: bộ câu hỏi và dữ liệu kiểm thử được cấp sẵn.
- `data/`: tài liệu nguồn cho RAG.
- `doc/`: đề bài, hướng dẫn, TEAM và mẫu báo cáo.
- `requirements/`: dependencies và constraints.
- `infra/`: Docker Compose; `guardrails/`: cấu hình guard.
- `tests/`: tests offline và integration tùy chọn.
- `artifacts/`: kết quả nhóm tự tạo sau khi làm bài.

## Mục tiêu và nơi viết kết quả

Nhóm đánh giá đầu ra pipeline RAG, kiểm tra độ tin cậy của LLM Judge và xây guard
cho input/output. Starter có các hàm TODO để học viên làm; runner, xuất JSON,
thống kê percentile và checker là phần hỗ trợ đã cung cấp.

**Trạng thái khi tải về:** chưa có bài làm, thông tin nhóm hay kết quả thực
nghiệm. Các hàm bài tập còn TODO; `doc/TEAM.md` và ba báo cáo là mẫu chưa điền;
`artifacts/` chỉ có `.gitkeep`. Nhóm tự tạo `artifacts/answers_50q.json` và ba JSON kết quả
sau khi chuẩn bị và hoàn thành bài. Các file `fixtures/test_set_50q.json`,
`fixtures/human_labels_10q.json`, `fixtures/adversarial_set_20.json`, `fixtures/clean_set_8.json` và
`fixtures/output_set_4.json` là dữ liệu đề bài được cấp sẵn, không phải kết quả đã chạy.

Dùng **`artifacts/` cho dữ liệu kết quả JSON** và **`doc/reports/` cho báo cáo
Markdown**. Đóng góp cá nhân nằm ở `doc/TEAM.md`, không viết thay cho phân tích kỹ
thuật. File sinh tự động vẫn phải commit vào repo bài nộp sau khi kiểm tra secrets.

| Nội dung | Đường dẫn từ gốc repo | Người phụ trách | Cách tạo |
|---|---|---|---|
| Thành viên, công việc, điều đã học | `doc/TEAM.md` | Từng người, trưởng nhóm đối chiếu | Điền tay |
| Answers và contexts của pipeline | `artifacts/answers_50q.json` | Người tích hợp pipeline | `scripts/setup_answers.py --live` |
| RAGAS từng câu, bottom 10, cluster | `artifacts/ragas_50q.json` | Phase A | Runner tự lưu kết quả thật |
| Phân tích lỗi và hướng sửa | `doc/reports/failure_clusters.md` | Phase A | Điền tay từ JSON |
| Pairwise, nhãn 0/1, κ, bias | `artifacts/judge_results.json` | Phase B | Runner tự lưu kết quả thật |
| Diễn giải κ và bias | `doc/reports/bias_report.md` | Phase B | Điền tay từ JSON |
| 20 attacks, 8 clean inputs, output, latency | `artifacts/guard_results.json` | Phase C | Runner tự lưu kết quả thật |
| Kiến trúc, CI gates, monitoring | `doc/reports/blueprint.md` | Cả nhóm, người tích hợp | Điền tay; đề xuất CI/CD |

Đọc [đề bài](doc/ASSIGNMENT.md), [checkpoints](doc/CHECKPOINTS.md),
[rubric](doc/RUBRIC.md), [quy định](doc/RULES.md) và [nộp bài](doc/SUBMISSION.md).
Giao diện mã bài trước nằm trong [PIPELINE_INTERFACE.md](doc/PIPELINE_INTERFACE.md);
schema và cách chạy nằm trong [REPORT_SCHEMAS.md](doc/REPORT_SCHEMAS.md).

## Chuẩn bị trước buổi học

Môi trường mục tiêu là **Python 3.11**. Dùng `requirements/requirements-test.lock.txt` cho
unit tests offline và `requirements/requirements.txt` cùng `requirements/constraints-core.txt` cho full
runtime. NeMo/Annoy cần compiler C++ trên Windows. Nhóm phải kiểm tra cài đặt,
imports và model trên máy của mình theo [ENVIRONMENT.md](doc/ENVIRONMENT.md).

1. Làm theo [ENVIRONMENT.md](doc/ENVIRONMENT.md), chuẩn bị compiler, Docker và
   dependencies trước buổi học. Windows có thể chạy trực tiếp Python trong
   virtualenv nếu PowerShell không cho kích hoạt; không cần đổi policy toàn máy.
2. Đưa năm module `m1`–`m5` từ bài RAG trước vào `src/`, đối chiếu bảng giao
   diện. `pipeline.py` có thể giữ làm tham khảo; setup **không gọi file này**.
3. Tải spaCy và model embedding/rerank, khởi động Qdrant đã pin
   `qdrant/qdrant:v1.9.7`; kiểm tra key trong `.env`.
4. Từ gốc repo, sinh answers trước buổi học:

```bash
python scripts/setup_answers.py --live
```

Đầu ra cần 50 bản ghi thuộc 20 factual, 20 multi_hop, 10 adversarial. Mỗi bản ghi
có answer, contexts và ground_truth riêng biệt; `generation_mode` ghi rõ LLM hay
extractive fallback, `generation_model` là ID model hoặc null với fallback.
Không dùng ground truth thay answer để tạo điểm đẹp. Task 2 trả RagasEvaluation
với evaluator_models từ m4; metadata phiên bản 2 tách model theo từng vai trò.

## Kiểm tra trên lớp và chạy thực nghiệm

Trong 15 phút đầu, xác nhận virtualenv, Qdrant, module/interface và 50 answers
đã sẵn sàng; điền thành viên/phân công. Cài đặt cold-cache hoặc tải model chưa
xong là việc chuẩn bị còn thiếu, không giả định sẽ hoàn tất trong mốc 15 phút.

1. Hoàn thành các hàm TODO theo ba phase. Tests mặc định dùng mock, không gọi
   API, không tải spaCy/model. Khi chưa implement, student tests phải fail.
2. Chạy unit tests; dùng `-m support` khi chỉ kiểm tra phần scaffold cung cấp:

```bash
python -m pytest tests/ -q
python -m pytest tests/ -m support -q
```

3. Sau khi implement, chạy một batch thực nghiệm thật. `--live` xác nhận dùng
   API và mạng; có chi phí. Runner không tạo báo cáo hợp lệ từ TODO còn nguyên.

```bash
python scripts/run_experiments.py --phase a --live
python scripts/run_experiments.py --phase b --live
python scripts/run_experiments.py --phase c --live --latency-samples 20
```

Phase B dùng đúng `model_answer` của 10 bản ghi human labels cho nhãn 0/1; không
dùng answer pipeline mới và không gửi human_label/human_note vào judge.
Phase C đòi **ít nhất 15/20 attacks**, kiểm tra **8/8 câu sạch được allowed**,
và kiểm tra output. Bonus giữ mốc **18/20 attacks**, kèm clean controls đạt.

4. Điền ba báo cáo Markdown và TEAM, rồi kiểm tra bằng chứng đã lưu:

```bash
python scripts/check_lab.py
```

Checker mặc định không chạy pytest lại và không gọi API. Nếu muốn gộp unit tests
với kiểm tra bài nộp, chỉ chạy `python scripts/check_lab.py --with-tests`.
Checker validate Answers/Phase A/B/C bằng JSON Schema trước khi đối chiếu nguồn
và phép tính; thiếu/sai generation_mode, pair_sources hoặc metadata đều bị từ chối.
Ở bản starter, student tests và checker phải báo chưa hoàn thành do còn TODO,
thiếu answers/kết quả và chưa điền templates.
Integration tests là lựa chọn thay cho chạy batch B/C riêng, không chạy cả hai
để tránh trả phí hai lần: `python -m pytest -m integration --run-live`.

Trưởng nhóm nộp một link repo theo kênh coach công bố. Deadline mặc định là
**11:59 AM (13/10/2026), Asia/Ho_Chi_Minh (UTC+07:00)**; áp dụng điều chỉnh của
key coach trong 48 giờ sau lab theo quy ước chung. Blueprint là đề xuất CI/CD,
không mặc nhiên là workflow đã chạy.
