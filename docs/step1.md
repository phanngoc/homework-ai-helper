# File mô tả các bước thực hiện trong quá trình xây dựng hệ thống học trực tuyến.

## Phân loại các bài học
- Phân loại các bài luyện tập cho học sinh lớp 10, lớp 11, lớp 12, đề thi thử luyện thi Đại học
- Phân loại dựa trên môn học (ưu tiên Toán, Lý, Hóa)
- Phân loại dựa trên độ khó của bài luyện tập

## Tính năng search
- Tìm kiếm bài luyện tập theo môn học
- Tìm kiếm bài luyện tập theo độ khó

## Feature using crewAI
- Tính năng giải bài tập toán học nếu phát hiện trong bài luyện tập có 
chứa công thức toán học thì sẽ gọi API của crewAI để giải bài tập đó.


Math Response:
Explanation: Sử dụng quy tắc trừ của logarithm: ln(a) - ln(b) = ln(a/b).

Output: ln(7a) - ln(3a) = ln(\frac{7a}{3a})

Explanation: Rút gọn biểu thức: \frac{7a}{3a} = \frac{7}{3}, nên: ln(\frac{7a}{3a}) = ln(\frac{7}{3}).

Output: ln(\frac{7}{3})

Explanation: Ta thấy ln(\frac{7}{3}) tương đương với đáp án C.

Output: Vậy, đáp án đúng là C: ln(\frac{7}{3}).

Final Answer:
C: ln(\frac{7}{3})