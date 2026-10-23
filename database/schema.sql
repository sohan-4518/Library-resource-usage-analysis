CREATE TABLE IF NOT EXISTS categories (
 category_id SERIAL PRIMARY KEY,
 category_name VARCHAR(80) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS books (
 book_id SERIAL PRIMARY KEY,
 isbn VARCHAR(20) UNIQUE,
 title VARCHAR(200) NOT NULL,
 author VARCHAR(160) NOT NULL,
 category_id INTEGER REFERENCES categories(category_id) ON DELETE SET NULL,
 publisher VARCHAR(160),
 publication_year INTEGER CHECK (publication_year IS NULL OR publication_year BETWEEN 1450 AND 2100),
 total_copies INTEGER NOT NULL DEFAULT 1 CHECK(total_copies >= 0),
 available_copies INTEGER NOT NULL DEFAULT 1 CHECK(available_copies >= 0 AND available_copies <= total_copies),
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS students (
 student_id SERIAL PRIMARY KEY,
 usn VARCHAR(30) NOT NULL UNIQUE,
 full_name VARCHAR(140) NOT NULL,
 department VARCHAR(100) NOT NULL DEFAULT 'CSE',
 email VARCHAR(180),
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS borrow_records (
 borrow_id SERIAL PRIMARY KEY,
 book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE RESTRICT,
 student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE RESTRICT,
 issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
 due_date DATE NOT NULL,
 return_date DATE,
 status VARCHAR(12) NOT NULL DEFAULT 'ISSUED' CHECK(status IN ('ISSUED','RETURNED')),
 CHECK(due_date >= issue_date),
 CHECK((status='ISSUED' AND return_date IS NULL) OR (status='RETURNED' AND return_date IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_borrow_due_status ON borrow_records(due_date,status);
CREATE INDEX IF NOT EXISTS idx_borrow_issue_date ON borrow_records(issue_date);
