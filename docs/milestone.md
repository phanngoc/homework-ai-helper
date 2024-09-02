## Các tính năng cần hoàn thiện.

- Giáo viên và học sinh có thể trò chuyện tương tác thông qua mỗi lời giải (của học sinh hoặc AI suggest) của một bài toán.

- Giáo viên 
  + Được phép upload bài giải viết đè bài giải của AI.
  + Được phép tạo bài toán mới.
  + Có thể comment trên mỗi bài giải chính thức câu hỏi.
  + Có thể comment trên bài giải của học sinh.
  + Có thể xem được số lượng học sinh đã làm bài.  

- Học sinh:
  + Submit bài giải.    
  + Trò chuyện với giáo viên về bài giải của mình.

- Bài toán:
  + Được phân loại dựa thêm vào độ khó của bài toán:
    Thể loại: [hình học , giải tích, số học],
    Lớp mấy [lớp 10, lớp 11, lớp 12].
    Mục tiêu: [đề thi thử luyện thi Đại học, bài luyện tập, toán tốt nghiệp].
- Đề xuất (recommendation):
  + Dựa trên số lượng bài mà học sinh đã làm, hệ thống sẽ đề xuất các bài toán phù hợp với năng lực của học sinh.
    Thể loại: [hình học , giải tích, số học],
    Lớp mấy [lớp 10, lớp 11, lớp 12].
 
  + Đề xuất số lương bài toán [có thể 1 bài, 5 bài, 10 bài] toán mỗi ngày.

- Các tài liệu được đánh level, dựa trên số bài học sinh làm được trong một khoảng thời gian.

### Các tính năng phụ.
- Build job clean các file upload người dùng tải lên.

### Tính năng crawling các đề thi thử luyện thi Đại học từ các trang web uy tín.
- Website ni open, không cần login.
https://thcs.toanmath.com/2024/06/de-tuyen-sinh-lop-10-chuyen-mon-toan-co-so-nam-2024-2025-so-gddt-dong-thap.html


## Đánh giá tính khả thi của việc chấm bài tự động.
    - Học sinh viết ra giấy lời giải, chụp lại để hệ thống AI tự động chấm.
    => Cần xây dựng mô hình AI chấm bài tự động.
    - Giáo viên có quyền tải lên bài giải của mình, viết đè bài giải của AI.


```sql
-- Users Table
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    role ENUM('Teacher', 'Student')
);

-- Problems Table
CREATE TABLE Problems (
    problem_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255),
    description TEXT,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES Users(user_id)
);

-- Solutions Table
CREATE TABLE Solutions (
    solution_id INT PRIMARY KEY AUTO_INCREMENT,
    problem_id INT,
    user_id INT,
    content TEXT,
    is_ai_generated BOOLEAN,
    FOREIGN KEY (problem_id) REFERENCES Problems(problem_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Comments Table
CREATE TABLE Comments (
    comment_id INT PRIMARY KEY AUTO_INCREMENT,
    solution_id INT,
    user_id INT,
    content TEXT,
    FOREIGN KEY (solution_id) REFERENCES Solutions(solution_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Assignments Table
CREATE TABLE Assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    problem_id INT,
    student_id INT,
    assigned_date DATE,
    FOREIGN KEY (problem_id) REFERENCES Problems(problem_id),
    FOREIGN KEY (student_id) REFERENCES Users(user_id)
);

-- Performance Table
CREATE TABLE Performance (
    performance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    problem_id INT,
    score INT,
    submission_date DATE,
    FOREIGN KEY (student_id) REFERENCES Users(user_id),
    FOREIGN KEY (problem_id) REFERENCES Problems(problem_id)
);
```

```
+-----------------+       +-----------------+       +-----------------+
|     Users       |       |    Problems     |       |    Solutions    |
+-----------------+       +-----------------+       +-----------------+
| user_id (PK)    |<------| problem_id (PK) |<------| solution_id (PK)|
| name            |       | title           |       | problem_id (FK) |
| email           |       | description     |       | user_id (FK)    |
| role            |       | created_by (FK) |       | content         |
+-----------------+       +-----------------+       | is_ai_generated |
                                                    +-----------------+
                                                          |
                                                          |
                                                          v
                                                +-----------------+
                                                |    Comments     |
                                                +-----------------+
                                                | comment_id (PK) |
                                                | solution_id (FK)|
                                                | user_id (FK)    |
                                                | content         |
                                                +-----------------+

+-----------------+       +-----------------+
|   Assignments   |       |   Performance   |
+-----------------+       +-----------------+
| assignment_id (PK)|     | performance_id (PK)|
| problem_id (FK)  |      | student_id (FK)   |
| student_id (FK)  |      | problem_id (FK)   |
| assigned_date    |      | score             |
+-----------------+      | submission_date   |
                         +-----------------+

```

