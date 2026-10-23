-- Most borrowed titles
SELECT b.title,b.author,COUNT(br.borrow_id) AS times_borrowed
FROM books b LEFT JOIN borrow_records br ON br.book_id=b.book_id
GROUP BY b.book_id ORDER BY times_borrowed DESC,b.title;
-- Category usage
SELECT c.category_name,COUNT(br.borrow_id) AS borrowing_count
FROM categories c LEFT JOIN books b ON b.category_id=c.category_id
LEFT JOIN borrow_records br ON br.book_id=b.book_id
GROUP BY c.category_id ORDER BY borrowing_count DESC;
-- Monthly borrowing
SELECT date_trunc('month',issue_date)::date AS month,COUNT(*) AS borrowing_count
FROM borrow_records WHERE issue_date>=CURRENT_DATE-INTERVAL '12 months'
GROUP BY 1 ORDER BY 1;
-- Overdue loans
SELECT br.borrow_id,s.usn,s.full_name,b.title,br.due_date,CURRENT_DATE-br.due_date AS days_overdue
FROM borrow_records br JOIN students s USING(student_id) JOIN books b USING(book_id)
WHERE br.status='ISSUED' AND br.due_date<CURRENT_DATE ORDER BY br.due_date;
