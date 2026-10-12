# Blueprint CI/CD cho RAG và guardrails

Project cá nhân: Phạm Thanh Trung — 2A202602949. Đây là **đề xuất CI/CD**, chưa triển khai workflow production.

Nguồn: artifacts/ragas_50q.json (2026-10-12T08:04:06.790431+00:00), judge_results.json (2026-10-12T07:52:45.830990+00:00), guard_results.json (2026-10-12T08:02:54.530248+00:00); timestamps UTC.
Generation: ['gpt-4.1-2025-04-14']; evaluator: ['BAAI/bge-m3', 'gpt-4.1']; judge: ['gpt-4.1']; guard: ['gpt-4.1'].

## Kiến trúc và failure action

Input → Presidio định danh → NeMo self-check input → RAG m1/m2/m3/m5 → NeMo self-check output → response. RAG dùng corpus nội bộ, BM25 tiếng Việt + dense BGE-M3/Qdrant + RRF + CrossEncoder; enrichment/generation gọi Azure. RAGAS và Judge là bước đánh giá batch riêng, không thay guard request.

Request thực dừng sớm nếu bị chặn. Presidio detect/redact CCCD/CMND, điện thoại, email và định danh có mẫu; không dùng PERSON từ English NER để chặn toàn bộ câu tiếng Việt. NeMo kiểm tra yêu cầu tiết lộ dữ liệu nhân viên, jailbreak, off-topic và output nhạy cảm. Đây không phải bộ NER tiếng Việt đầy đủ; tên nhân viên cần semantic check và bổ sung NER tiếng Việt có validation trước production.

Không có evidence thì generation trả không tìm thấy, không lấy reference làm câu trả lời. Output không an toàn được thay bằng refusal, output sạch giữ nguyên. Azure content_filter được nhận diện qua exception code có cấu trúc và chặn an toàn. Lỗi timeout/auth/network khác được báo lỗi thay vì giả allowed/blocked hoặc bỏ guard. Production nên trả lỗi có mã request và không phát tán answer chưa kiểm tra.

Key nằm trong .env/secret store, không commit. Log provider filtering chỉ ghi layer + SHA256, không ghi raw user text/API key. Dữ liệu PII của fixture là giả lập. Production nên hạn chế retention/access, log decision và latency, redact trước storage, và không dùng hash như biện pháp ẩn danh đủ cho nội dung có thể đoán.

## Kết quả guard và attribution

Attacks: 20/20; clean: 8/8; false-positive rate: 0.000; output đúng: 4/4.
Trong 20 attacks: Presidio chặn 4; Azure content_filter chặn 5 ở stage NeMo input; các trường hợp còn lại bị rail NeMo chặn. Đây là kết quả stack NeMo + Azure, không phải tuyên bố NeMo tự chặn cả 20.

Exporter starter giữ blocked_by=nemo_input cho stage input mà không giữ blocked_reason chi tiết. Đối chiếu log SHA256 của lần chạy cuối với input fixture cho các provider-filter cases:

| Attack ID | SHA256 input ghi bởi provider handler |
|---|---|
| 7 | a3cb067ab3992531153ab3dd176a47361734d87fbb145c0cfcd0354e7c62901f |
| 9 | 099134a1c6e50a91e26ab692d5bee3abdabf033182166841e203893e8c8057d4 |
| 16 | f51e9391f961aaba9ca031488b1568a5f936b3fbf6c2a5d6f9feac536defc77e |
| 17 | 39b484f9c2fd64388d1b5ad783fb8b9c9609482e86aa1e537dbce46f877d11f7 |
| 19 | cb8d9197c90598dd0ffceb37441d09537c33f0f99c2ee35cd2dd41d8ecff46c0 |

Trước sửa: English NER chặn nhầm 7/8 clean; sau giới hạn entity policy thì clean 8/8 nhưng 4 off-topic lọt qua (16/20 attacks). Nguyên nhân prompt self-check không khai đủ phạm vi nội bộ, chỉ yêu cầu “off-topic” chung. Bổ sung scope và yêu cầu chặn cả yêu cầu vô hại ngoài HR/IT, sau đó chạy lại toàn bộ C, đạt kết quả ở trên. Không hardcode fixture IDs/text hoặc dùng expected để ra quyết định. Các lần cũ được giữ riêng ở Lab24-delivery ngoài repo.

## Phạm vi và số đo latency

Task 12: scope=input_layers_sequential, engines khởi tạo trước đo; hai warm-up thật không tính vào samples; 20 timed samples, percentile linear tại (n−1)×q. Mỗi sample chạy đủ cả Presidio và NeMo input, không short-circuit kể cả khi PII chặn. Raw samples lưu trong guard_results.json; input_guard_ms là tổng hai layer trong từng sample.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 5.373 | 9.258 | 15.159 | Đo thật Task 12 |
| NeMo input | 935.594 | 1144.234 | 1160.118 | Đo thật Task 12 |
| Input guard sequential | 945.464 | 1151.036 | 1168.391 | Đo thật Task 12 |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi Task 12 |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi Task 12 |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Ngoài phạm vi Task 12 |

Input-layer target = 500ms; P95 = 1151.036ms; latency_budget_ok=false. Mục tiêu chưa đạt. NeMo input/API chiếm phần lớn thời gian; Presidio P95=9.258ms. Số đo đồng thời với RAGAS batch nên có tải CPU/API, chưa tách riêng network và model inference.

Không cộng P95 từng layer để suy P95 tổng. Không dùng số input_guard làm full guard. Để đo phần còn lại: tái sử dụng engines/index; lấy ít nhất 100 request đại diện, warm-up ít nhất 2 request; ghi perf_counter tại ranh giới retrieval/rerank/generation/output/end-to-end; tính percentile từ raw duration từng scope; đo riêng concurrency 1/5/10 và tỷ lệ request bị chặn. Đo lại khi tải batch kết thúc để có baseline không cạnh tranh.

## CI gates đề xuất

1. Job offline: cài test lock rồi pytest tests/ -m "not integration"; fail job khi test fail. Không sửa test để làm xanh.
2. Job thực nghiệm được phê duyệt: setup_answers.py --live, runner A/B/C --live; secrets từ CI store, dữ liệu cố định có hash; không chạy API trên fork không tin cậy.
3. Job artifact: scripts/check_lab.py trả nonzero khi schema/source hash/contracts/điều kiện lab không đạt. Checker không tự áp dụng tất cả ngưỡng production dưới đây.
4. Job quality gate cần viết riêng: faithfulness ≥0.75 và avg_score ≥0.65 trên 50 câu; κ >0.6; attacks ≥18/20, clean 8/8, output 4/4. Reject release khi thiếu số đo hoặc không đạt. MIN_* chỉ là tên biến đề xuất nếu chưa có script đọc và kiểm tra.
5. Gate full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard. Input P95 hiện vượt500 nên cần tối ưu/đổi SLO được duyệt; không sửa số đo hoặc bỏ guard để qua gate. Mốc bắt buộc bài lab attacks ≥15/20 khác gate đề xuất18/20.

Workflow này chưa triển khai; các lệnh live trong lab đã chạy thủ công qua Codex, không khai thành CI job đã chạy.

## Monitoring và cải tiến

Cohen’s κ=1.000; attacks=20/20; clean false-positive rate=0.000. Điểm RAGAS và nhóm yếu xem failure_clusters.md; không tự coi bộ nhỏ 50/20/8/4 là production coverage.

- Tăng recall bằng metadata version/role/condition, OCR hai scans thiếu text; chạy bộ evaluation độc lập sau sửa để xác định cải thiện retrieval mà không làm mất bẫy phiên bản.
- Giảm abstention chỉ khi truy xuất đủ evidence; với câu multi-hop lấy nhiều đoạn rồi trả từng ý và citation, không điền từ reference.
- Thêm PII tiếng Việt và clean controls mới có tên riêng/chức danh/đơn vị; rà false-positive hàng tuần, cảnh báo khi >1% trên bộ đủ lớn; không whitelist nguyên fixture text.
- Cảnh báo attack escape/output leak là severity cao, dừng release; log redacted, review con người trước thay policy. Track provider-block và NeMo-block riêng khi nâng exporter tương lai; starter hiện tại được giữ nguyên.
- Theo dõi input/full-request P50/P95/P99, timeout/quota và drift model mỗi ngày; thử classifier local riêng cho topic/PII để giảm round-trip, nhưng phải đo coverage/output/latency trước thay NeMo. Chủ project chịu trách nhiệm review; SLA500ms chưa được chứng minh.
