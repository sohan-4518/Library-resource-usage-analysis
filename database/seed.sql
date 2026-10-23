INSERT INTO categories(category_name) VALUES
('Computer Science'),('Electronics'),('Mathematics'),('Literature')
ON CONFLICT DO NOTHING;
INSERT INTO books(isbn,title,author,category_id,publisher,publication_year,total_copies,available_copies)
SELECT v.isbn,v.title,v.author,c.category_id,v.publisher,v.year,v.total,v.available
FROM (VALUES
('9780132350884','Clean Code','Robert C. Martin','Computer Science','Prentice Hall',2008,5,4),
('9780131103627','The C Programming Language','Brian Kernighan','Computer Science','Prentice Hall',1988,4,3),
('9780262033848','Introduction to Algorithms','Thomas Cormen','Computer Science','MIT Press',2009,6,5),
('9780073523323','Database System Concepts','Abraham Silberschatz','Computer Science','McGraw Hill',2019,5,5),
('9780198066231','Engineering Mathematics','B. S. Grewal','Mathematics','Khanna',2017,4,4),
('9780071070041','Basic Electrical Engineering','D. P. Kothari','Electronics','McGraw Hill',2010,3,3),
('9780140449136','The Odyssey','Homer','Literature','Penguin Classics',2003,3,3),
('9780321765723','Computer Networks','Andrew Tanenbaum','Computer Science','Pearson',2010,5,4)
) AS v(isbn,title,author,category,publisher,year,total,available)
JOIN categories c ON c.category_name=v.category
ON CONFLICT(isbn) DO NOTHING;
INSERT INTO students(usn,full_name,department,email) VALUES
('4MW23CS101','Aarav Shetty','CSE','aarav@example.edu'),
('4MW23CS122','Roshni Rao','CSE','roshni@example.edu'),
('4MW23CS162','Sohan S Salian','CSE','sohan@example.edu'),
('4MW23EC105','Nisha Bhat','ECE','nisha@example.edu')
ON CONFLICT(usn) DO NOTHING;
INSERT INTO borrow_records(book_id,student_id,issue_date,due_date,return_date,status)
SELECT b.book_id,s.student_id,CURRENT_DATE-40,CURRENT_DATE-26,CURRENT_DATE-28,'RETURNED'
FROM books b,students s WHERE b.isbn='9780132350884' AND s.usn='4MW23CS101'
AND NOT EXISTS(SELECT 1 FROM borrow_records br WHERE br.book_id=b.book_id AND br.student_id=s.student_id);
INSERT INTO borrow_records(book_id,student_id,issue_date,due_date,status)
SELECT b.book_id,s.student_id,CURRENT_DATE-12,CURRENT_DATE+2,'ISSUED'
FROM books b,students s WHERE b.isbn='9780131103627' AND s.usn='4MW23CS162'
AND NOT EXISTS(SELECT 1 FROM borrow_records br WHERE br.book_id=b.book_id AND br.student_id=s.student_id AND br.status='ISSUED');
