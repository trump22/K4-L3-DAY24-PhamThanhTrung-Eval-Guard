# Phân tích lỗi Phase A

Project cá nhân: Phạm Thanh Trung — 2A202602949.

Nguồn: artifacts/ragas_50q.json; UTC 2026-10-12T08:04:06.790431+00:00.
Generation: ['gpt-4.1-2025-04-14']; evaluator thật từ m4: ['BAAI/bge-m3', 'gpt-4.1'].
50 answers đều generation_mode=llm, không có local fallback; contexts được retrieval/rerank thật. Qdrant có125 chunks; BGE-M3/CrossEncoder CPU, generation/evaluation Azure. RAGAS chạy đủ200 metric evaluations, 50×4, không dùng mock scores.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.983333 | 0.814583 | 0.700000 |
| answer_relevancy | 0.909785 | 0.711479 | 0.524863 |
| context_precision | 0.975000 | 0.712500 | 0.966667 |
| context_recall | 0.900000 | 0.695833 | 0.775000 |
| avg_score | 0.942030 | 0.733599 | 0.741632 |

Mean trên toàn bộ50: faithfulness=0.859167, answer_relevancy=0.753478, context_precision=0.868333, context_recall=0.793333; avg_score=0.818578. Đây là weighted mean theo số câu20/20/10, không trung bình không trọng số của ba distributions.

## Bottom 10 và diagnostic tree

Giữ đúng thứ tự, score, diagnosis và suggested_fix do student Task3 trả về. Diagnostic tree gắn nhãn theo metric thấp nhất; nhãn “LLM hallucinating” không tự chứng minh answer đã bịa. Cần đối chiếu văn bản bên dưới, đặc biệt các câu “Không tìm thấy.”.

| Rank | ID | Question | Distribution | Avg score | Worst metric | Diagnosis | Suggested fix |
|---|---|---|---|---|---|---|---|
| 1 | 39 | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. | multi_hop | 0.25 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 2 | 21 | Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào? | multi_hop | 0.375 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 3 | 44 | Bao lâu phải đổi mật khẩu một lần? | adversarial | 0.4583 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 4 | 33 | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | multi_hop | 0.4583 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 5 | 26 | Nhân viên vừa kết hôn và cùng tuần đó có con kết hôn. Tổng số ngày nghỉ đặc biệt có lương là bao nhiêu? | multi_hop | 0.4834 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |
| 6 | 5 | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | factual | 0.5 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 7 | 42 | Thâm niên bao nhiêu năm thì được cộng thêm ngày phép? | adversarial | 0.5 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 8 | 43 | Mật khẩu phải có tối thiểu bao nhiêu ký tự? | adversarial | 0.5 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 9 | 40 | Nhân viên cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, phát hiện vi phạm bảo mật. Họ nên và không nên làm gì theo chính sách? | multi_hop | 0.5836 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 10 | 27 | Nhân viên có thâm niên 7 năm theo v2024 được nghỉ bao nhiêu ngày phép? Nếu bị trừ thêm 4 ngày ốm không có giấy y tế thì còn lại bao nhiêu? | multi_hop | 0.6155 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |

### Đối chiếu retrieval/generation ở câu39

Answer “Không tìm thấy.”; ba contexts chỉ gồm thông báo thay thế phiên bản và header policy v1.0, thiếu đoạn quy định8/12 ký tự,90/120ngày,MFA. Reference cần so sánh đủ ba tiêu chí của cả hai phiên bản. Nguyên nhân trực tiếp: retrieval/reranking ưu tiên đoạn nói về phiên bản thay vì đoạn chứa giá trị. Abstention là hợp lý khi không đủ evidence, nhưng không đáp ứng tác vụ. Sửa: mở rộng retrieval theo từng tiêu chí và gom sibling chunks theo document/version; kiểm chứng đủ sáu giá trị trước generation.

### Đối chiếu multi-hop ở câu21

Answer “Không tìm thấy.”; contexts có15ngày cơ bản và ví dụ9năm→18ngày, nhưng không có khung lương Senior20–35triệu. Đồng thời trả cả rule3năm hiện hành và5năm cũ. Reference cần18ngày và lương20–35triệu. Đây là lỗi thiếu evidence cho ý lương và xung đột phiên bản, không phải bằng chứng model tạo thông tin sai. Sửa: decomposed query cho phép/thâm niên/lương, gom evidence theo role và effective date, ưu tiên bản hiện hành trừ câu hỏi yêu cầu so sánh cũ/mới.

### Đối chiếu version conflict ở câu44,42,43

Câu44 answer “Không tìm thấy.” dù context đầu có120ngày, context thứ hai90ngày, thứ ba nói v1 bị thay thế bởi v2. Reference yêu cầu120ngày. Câu43 similarly có cả12 và8ký tự; câu42 có3 và5năm. Model tránh chọn khi version không gắn rõ vào mỗi passage. Đây là abstention/version-disambiguation failure; nhãn faithfulness=0 và diagnostic “hallucinating” chưa phản ánh nguyên nhân văn bản. Sửa: giữ version/effective/status metadata trong evidence mà generation nhìn thấy, liên kết thông báo thay thế với đúng tài liệu. Không xóa policy cũ vì đề cố ý kiểm tra bẫy version.

### Phủ định: câu46 và50

Câu46 trả đúng phủ định không được nghỉ phép khi thử việc; reference còn hướng dẫn nghỉ không lương/phê duyệt. Câu50 abstain dù context cấm VPN cá nhân và yêu cầu WireGuard. Không thể dùng điểm adversarial thấp để nói mọi negation trap đều được nhận diện. Cải tiến prompt trả trực tiếp kết luận phủ định có dẫn evidence khi đã đủ; không gộp câu có nhiều điều kiện thành câu trả lời chung.

## Matrix và nhóm yếu nhất

Matrix đếm **tất cả50 câu** theo worst metric, kể cả câu điểm cao. Mỗi câu đếm một lần, dùng thứ tự metrics để phá hòa. Đây không phải bảng số failures.

| Worst metric | factual | multi_hop | adversarial |
|---|---|---|---|
| faithfulness | 1 | 6 | 3 |
| context_recall | 1 | 6 | 5 |
| context_precision | 1 | 4 | 0 |
| answer_relevancy | 17 | 4 | 2 |

Nhóm yếu nhất theo mean thấp nhất: **multi_hop**, mean=0.733599. Worst metric xuất hiện nhiều nhất: **answer_relevancy**, 23/50. Không chọn nhóm bằng số lượng20/20/10.
17/20 factual có worst metric answer_relevancy nhưng factual mean vẫn0.942; vì metric khác gần1, đây chỉ là yếu tương đối. Multi-hop thấp nhất do cần đủ nhiều policy/điều kiện mà top3 contexts thường thiếu một ý. Đã có BM25 và reranker, nên suggested_fix “Add reranking/BM25” từ tree cần hiểu là cải thiện cấu hình/coverage của thành phần đã tồn tại, không giả rằng pipeline chưa có.

## Bẫy adversarial, ưu tiên sửa và giới hạn

Adversarial mean 0.741632 < factual 0.942030; chênh lệch phản ánh bộ adversarial khó hơn, không chứng minh nhận ra bẫy. Multi-hop mean còn thấp hơn adversarial.
Ưu tiên(1) version-aware evidence,(2) retrieval multi-hop/decomposition/sibling chunks,(3) generation trả đủ từng ý khi có evidence và abstain chỉ phần thiếu,(4) OCR nguồn scan thiếu text. Sau mỗi sửa, tạo batch mới với timestamps/hashes và thêm held-out câu paraphrase, không sửa test/ground_truth hay chọn bỏ câu điểm thấp. Giữ artifacts hiện tại làm baseline đánh giá của lab; các cải tiến RAG chưa được thực hiện/đo trong bản này.

Hai PDF scan không có text layer bị loader bỏ qua, chưa OCR; corpus gốc vẫn được giữ. 50câu, cùng họ gpt-4.1 làm generation/evaluator và local embeddings chỉ là một cấu hình. RAGAS metric/diagnosis cần người đối chiếu; scores là số đo của lần chạy, không bảo đảm factual accuracy mọi đầu vào.
