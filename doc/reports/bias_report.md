# Đánh giá LLM Judge Phase B

Project cá nhân: Phạm Thanh Trung — 2A202602949.

Nguồn: `artifacts/judge_results.json`; thời điểm UTC: 2026-10-12T07:52:45.830990+00:00.
Generation: ['gpt-4.1-2025-04-14']; judge: ['gpt-4.1'].

## Năm cặp A/B và hai lượt

A lấy nguyên từ answers_50q.json; B là model_answer trong human_labels_10q.json; reference lấy từ test_set_50q.json. IDs cố định: 1, 5, 12, 21, 41. Hai lượt gọi API thật; lượt 2 đảo vị trí rồi quy winner/scores về A/B ban đầu. Reasoning lượt 2 giữ nguyên lời model, nên các chữ A/B trong reasoning vẫn chỉ vị trí đã đảo.

| ID | Candidate A | Candidate B | Pass 1 | Pass 2 quy về gốc | Final | Nhất quán |
|---|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc khi kết hôn. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | B | B | B | True |
| 5 | Không tìm thấy. | Cần Giám đốc phòng ban phê duyệt. | A | A | A | True |
| 12 | Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là 1 tháng lương. | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | A | A | A | True |
| 21 | Không tìm thấy. | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | B | B | B | True |
| 41 | Nhân viên chính thức được hưởng 15 ngày phép năm có lương theo chính sách mới. | Nhân viên được nghỉ 12 ngày phép năm. | A | A | A | True |

### Cặp 1

- Lượt 1: Answer B đầy đủ và chính xác hơn vì nêu rõ quyền lợi 'có lương', phù hợp với đáp án tham chiếu. Answer A thiếu thông tin về việc nghỉ có lương.
- Scores lượt 1: {'A': 0.7, 'B': 1.0}.
- Lượt 2 (reasoning theo vị trí đảo): Answer A đầy đủ và chính xác hơn vì nêu rõ là nghỉ có lương, phù hợp với đáp án tham chiếu. Answer B thiếu thông tin về việc nghỉ có lương.
- Scores lượt 2 đã quy về A/B gốc: {'A': 0.7, 'B': 1.0}.

### Cặp 5

- Lượt 1: A không cung cấp thông tin nhưng không gây hiểu lầm; B trả lời sai người phê duyệt, gây sai lệch nghiêm trọng.
- Scores lượt 1: {'A': 0.3, 'B': 0.0}.
- Lượt 2 (reasoning theo vị trí đảo): Answer A sai về độ chính xác vì theo chính sách, Tổng Giám đốc mới là người phê duyệt đơn hàng trên 50 triệu. Answer B không cung cấp thông tin nhưng không gây sai lệch.
- Scores lượt 2 đã quy về A/B gốc: {'A': 0.2, 'B': 0.0}.

### Cặp 12

- Lượt 1: A chính xác và đầy đủ hơn vì nêu rõ điều kiện 6 tháng trở lên, sát với đáp án tham chiếu. B thiếu điều kiện này nên chưa đầy đủ.
- Scores lượt 1: {'A': 1.0, 'B': 0.7}.
- Lượt 2 (reasoning theo vị trí đảo): B trả lời đúng trọng tâm câu hỏi, nêu rõ đối tượng là nhân viên chính thức có từ 6 tháng trở lên, đầy đủ và súc tích hơn A. A thiếu thông tin về điều kiện 6 tháng.
- Scores lượt 2 đã quy về A/B gốc: {'A': 1.0, 'B': 0.7}.

### Cặp 21

- Lượt 1: Answer B chính xác, đầy đủ và súc tích theo chính sách tham chiếu; Answer A không có thông tin.
- Scores lượt 1: {'A': 0.0, 'B': 1.0}.
- Lượt 2 (reasoning theo vị trí đảo): Answer A chính xác, đầy đủ và súc tích theo đáp án tham chiếu; Answer B không trả lời câu hỏi.
- Scores lượt 2 đã quy về A/B gốc: {'A': 0.0, 'B': 1.0}.

### Cặp 41

- Lượt 1: Answer A chính xác theo chính sách v2024 hiện hành và súc tích, trong khi Answer B chỉ đúng với chính sách cũ đã bị thay thế.
- Scores lượt 1: {'A': 1.0, 'B': 0.3}.
- Lượt 2 (reasoning theo vị trí đảo): Answer B chính xác với chính sách v2024 hiện hành và súc tích, trong khi Answer A chỉ đúng với chính sách cũ đã bị thay thế.
- Scores lượt 2 đã quy về A/B gốc: {'A': 1.0, 'B': 0.3}.

Position inconsistency: 0/5 = 0.000.
Verbosity win rate: 0.800; decisive cases: 5; chi tiết: {'a_wins_a_longer': 2, 'b_wins_b_longer': 2, 'total_decisive': 5}.

Không có cặp đổi winner khi đảo vị trí trong mẫu 5 cặp. Chưa thể kết luận model không có position bias. Bốn trong năm winner dài hơn, nhưng cặp 1 bổ sung “có lương”, cặp 12 giữ điều kiện thâm niên, cặp 21 trả đủ hai ý và cặp 41 dùng phiên bản hiện hành; đây là khác biệt nội dung, không chứng minh độ dài gây ra chiến thắng. Cặp 5 chọn câu không tìm thấy thay cho câu sai người phê duyệt; winner tương đối không có nghĩa đáp án A đạt chất lượng.

## Calibration đúng model_answer

Binary judge dùng đúng question, model_answer của fixture và reference. Human label/note không được đưa vào prompt; nhãn human chỉ dùng sau gọi API để so sánh. Không dùng answers mới của pipeline để thay candidate calibration.

| ID | Model answer gốc | Judge | Human | Đồng ý | Reasoning judge |
|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | 1 | True | Answer đúng với reference về số ngày nghỉ (3 ngày làm việc có lương) khi kết hôn. Không thiếu ý thiết yếu, không đảo phủ định, dùng đúng chính sách. |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | 0 | True | Answer sai vì theo reference, đơn hàng trên 50 triệu phải do Tổng Giám đốc (CEO) phê duyệt, không phải Giám đốc phòng ban. |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | 1 | True | Answer nêu đúng mức thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là 1 tháng lương, phù hợp với reference và không bỏ qua điều kiện quan trọng. |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | 1 | True | Answer correctly states 18 days off (15 basic + 3 seniority for 9 years) and salary range for Senior is 20-35 million, matching the reference. No essential information is missing or incorrect. |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | 1 | True | Answer đúng theo reference: nghỉ sau 8 tháng là trước hạn cam kết 1 năm, phải hoàn trả toàn bộ 25 triệu. Không thiếu ý nào, không sai điều kiện. |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | 0 | True | Answer thiếu Kế toán trưởng trong phê duyệt (theo reference cần cả Trưởng phòng và Kế toán trưởng). Phí phạt trả đúng 2%/tháng trên 8 triệu nhưng không nêu rõ tính theo số ngày quá hạn (15 ngày), và không đề cập điều kiện không được tạm ứng mới khi chưa hoàn ứng. |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | 1 | True | Answer đã nêu đúng số ngày phép năm (19 ngày) và tổng phụ cấp hàng tháng (1.500.000 VNĐ), phù hợp với reference: phép năm gồm 15 ngày cơ bản + 4 ngày thâm niên, phụ cấp gồm ăn trưa và điện thoại Manager. Không thiếu ý thiết yếu, không sai phiên bản. |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | 0 | True | Answer dùng số ngày phép năm theo chính sách cũ (12 ngày), trong khi reference yêu cầu dùng chính sách v2024 hiện hành là 15 ngày cơ bản (+1 ngày/3 năm thâm niên). |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | 1 | True | Answer đúng theo reference: nhân viên thử việc không được nghỉ phép năm, nếu cần nghỉ phải xin nghỉ không lương. Đã dùng đúng phủ định, không bỏ qua điều kiện quan trọng. |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | 0 | True | Answer cho phép dùng VPN cá nhân (NordVPN) khi WFH, nhưng reference khẳng định KHÔNG được dùng VPN cá nhân, bắt buộc dùng VPN WireGuard của công ty. Answer đã đảo phủ định quan trọng, không đúng chính sách. |

Observed agreement = 1.00 (10/10); judge positive = 0.60; human positive = 0.60.
Chance agreement = 0.60×0.60 + 0.40×0.40 = 0.52.
Cohen’s κ = (1.00−0.52)/(1−0.52) = 1.000.

## Giới hạn và cách dùng judge

10/10 nhãn đồng ý với human và κ=1.0 trong bộ calibration nhỏ này, vượt mốc bonus >0.6. Không có case lệch để phân tích trong lần chạy này. Câu 41 nhận sai vì dùng 12 ngày phiên bản cũ; câu 50 nhận sai vì đảo phủ định về VPN. Câu 29 nhận sai vì thiếu Kế toán trưởng; lý do judge còn thêm chi tiết ngoài câu hỏi nên vẫn cần người kiểm chứng reasoning, kể cả khi nhãn đúng.

Prompt dùng reference, JSON có kiểm tra schema và temperature=0. Generation và judge đều là cùng họ gpt-4.1, có nguy cơ sai lệch chung; không coi judge là đáp án tuyệt đối. Tăng bộ calibration độc lập, bao phủ version/negation/đáp án từ chối, và dùng người đánh giá mù candidate/model trước khi áp dụng production. Không đổi fixture hoặc nhãn để cải thiện κ.
