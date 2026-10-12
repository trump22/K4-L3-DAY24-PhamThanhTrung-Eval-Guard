# Project cá nhân K4 Track 3B — Lab24

Tên project: PhamThanhTrung. Người nộp: Phạm Thanh Trung — 2A202602949.

Repo: https://github.com/trump22/K4-L3-DAY24-PhamThanhTrung-Eval-Guard

Theo yêu cầu trực tiếp của người học, bài được triển khai dưới dạng project cá nhân với một thành viên. Đề gốc quy định bài nhóm; README/RULES/SUBMISSION gốc vẫn giữ yêu cầu này. Việc chấp nhận hình thức cá nhân do coach quyết định; kết quả kỹ thuật không chứng minh miễn yêu cầu bài nhóm.

Ngày chạy: 12/10/2026. Deadline hiển thị trên Vlearn: 13/10/2026 11:59 — Asia/Ho_Chi_Minh (UTC+07:00).

Commit mã và bằng chứng thực nghiệm: ghi SHA sau khi đóng gói; commit tài liệu kế tiếp chỉ lưu SHA đó. Link nộp sẽ trỏ bản cuối trên GitHub.

## Thành viên và công việc thực tế

| STT | Họ và tên | MSSV | Vai trò / công việc | Bằng chứng |
|---|---|---|---|---|
| 1 | Phạm Thanh Trung | 2A202602949 | Chủ project; yêu cầu bài cá nhân, cung cấp cấu hình Azure, cho phép triển khai/chạy/nộp với Codex hỗ trợ | src/phase_a_ragas.py, phase_b_judge.py, phase_c_guard.py; artifacts/; doc/reports/ |

Codex hỗ trợ triển khai Tasks 1–13, tích hợp pipeline, cài dependency, chạy lệnh, đọc lỗi, viết báo cáo theo JSON và đóng gói/nộp dưới sự ủy quyền của người học. Không khai các thao tác do Codex thực hiện thành thao tác tự viết tay của người học; không khai thành viên giả hoặc commit giả để mô phỏng nhóm.

## Môi trường và chuẩn bị

- Windows, Python 3.11.9 trong .venv riêng. MSVC Build Tools 18 dùng để build Annoy. Core constraints của starter giữ nguyên.
- RAGAS 0.1.22; NeMo Guardrails 0.10.0; Presidio và spaCy en_core_web_lg 3.8.0. LangChain 0.2.17; NumPy 1.26.4; CPU PyTorch 2.14.1.
- requirements/constraints-windows.txt thêm PyArrow 17.0.0/Pandas 2.2.3 để tương thích NumPy 1.26.4; không sửa constraints-core.txt. pip check không phát hiện lỗi tương thích DLL, vì vậy đã kiểm tra import/runtime thật.
- Docker Desktop engine 29.4.2, Qdrant qdrant/qdrant:v1.9.7 theo compose starter. Collection lab24_production có 125 chunks được index thật; không sử dụng fallback in-memory cho lần setup.
- Local embeddings BAAI/bge-m3; reranker BAAI/bge-reranker-v2-m3 chạy CPU. Enrichment và generation qua Azure endpoint OpenAI-compatible gpt-4.1; completion generation trả ID gpt-4.1-2025-04-14.
- Lệnh setup_answers.py tạo đủ 50 answers: factual 20, multi_hop 20, adversarial 10; tất cả generation_mode=llm và có contexts. Enrichment 371,2s; indexing 57,5s; query 457,6s. Không điền ground truth vào câu trả lời khi thiếu evidence.
- Loader bỏ qua hai PDF không có text layer: BCTC.pdf và Nghi_dinh_so_13-2023_ve_bao_ve_du_lieu_ca_nhan_508ee.pdf. Giữ file gốc, ghi thiếu OCR thay vì giả nội dung.
- Key chỉ ở .env bị ignore. Không đưa .venv, cache model, cache enrichment, installer hay log chứa thông tin riêng vào Git. PII trong fixtures/artifacts là dữ liệu giả lập do đề cung cấp.

## INDIVIDUAL

### PhamThanhTrung-2A202602949

- Phạm vi bài cá nhân: đánh giá RAGAS 50 câu, Judge/swap/calibration, Presidio/NeMo/latency và blueprint. Nguồn pipeline của bài Day18 được tái sử dụng với adapter tương thích runner Day24, theo yêu cầu đề.
- AI hỗ trợ: Codex viết/hoàn thiện student functions, adapter, cài môi trường, chạy thực nghiệm thật, phân tích evidence và báo cáo. Người học đã yêu cầu thực hiện và chọn hình thức cá nhân; chưa có bằng chứng người học tự giải thích từng hàm trong phiên này. Cần đọc và trình bày lại kiến trúc, kappa và phạm vi latency trước khi bảo vệ bài.
- Bằng chứng: bốn JSON trong artifacts với timestamps/models/source hashes; ba Markdown trong doc/reports; lịch sử commit của bản nộp. Không tạo nhãn/số đo thủ công, không sửa fixtures, tests, schemas, runner hay checker.
- Cách kiểm tra: pytest offline với mock để kiểm tra hợp đồng; các runner --live để kiểm tra runtime/API. Lượt tests sớm khi pip chưa cài xong có 43 failed do thiếu jsonschema; sau hoàn tất dependency có 86 passed, 3 deselected. Đây là lỗi thời điểm chạy của Codex, không được che bằng sửa test. Kết quả kiểm tra bản cuối ghi trong README sau khi chạy checker --with-tests.
- Các lỗi đã xử lý: API Azure content_filter được nhận diện qua code có cấu trúc và chặn an toàn, không coi mọi exception là attack; WinError 1114 của Torch được khắc phục bằng import Torch trước Arrow/LangChain; Presidio English NER nhận nhầm tiếng Việt, nên tầng PII chỉ dùng định danh có mẫu, semantic employee-data requests chuyển tới NeMo; scope prompt được bổ sung rõ để chặn cả yêu cầu ngoài chủ đề nhưng vô hại.
- Điều cần nắm: mean thấp không đồng nghĩa nhận ra bẫy; swap winner tương đối khác nhãn calibration; kappa=1 trong 10 mẫu không bảo đảm tổng quát; input-layer P95 khác full guard/RAG; vendor filtering và quyết định NeMo cần phân biệt.
- Giới hạn: bộ dữ liệu nhỏ; cùng họ model cho nhiều vai trò; Windows CPU; PDF scans chưa OCR; model không đảm bảo deterministic tuyệt đối. Blueprint là đề xuất CI/CD, không phải hệ thống production đã triển khai.

## Nguồn và phạm vi thay đổi

- Starter chính thức: https://github.com/VinUni-AI20k/K4-Track-3B-Day24-Eval-Guard — base d98f9b47c27678be1687a2853dd55aed6aecba24.
- Pipeline Day18: https://github.com/trump22/K4-Track3B-Day18-PhamThanhTrung-2A2202602949-Production-RAG . Tên repo nguồn có chuỗi MSSV khác; chỉ là tên nguồn được giữ nguyên, MSSV khai hiện tại là 2A202602949.
- Chỉ hoàn thiện mã học viên, thêm năm module m1–m5 và llm adapter, cấu hình model/prompt, constraints Windows, README/TEAM/reports và artifacts thật. Framework, tests, fixtures, corpus và schema giữ nguyên so với starter.

## Cập nhật sau khi nộp

Chưa có cập nhật sau deadline. Bản nộp được đóng gói ngày 12/10/2026; mọi sửa đổi sau đó cần ghi thời điểm/commit và tuân theo quyết định coach.
