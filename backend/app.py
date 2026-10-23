import os
from datetime import date,timedelta
from flask import Flask,jsonify,request,render_template
from psycopg.errors import UniqueViolation
from backend.db import connect, all_rows, one_row
app=Flask(__name__,template_folder="../frontend",static_folder="../frontend/static")
def err(msg,code=400): return jsonify({"error":str(msg)}),code
@app.get("/")
def home(): return render_template("index.html")
@app.get("/api/health")
def health():
    try:
        r=one_row("SELECT current_database() AS db")
        return jsonify({"status":"ok","database":r["db"]})
    except Exception as e: return err("Database connection failed. Check PostgreSQL and .env: "+e.__str__(),503)
@app.get("/api/dashboard")
def dashboard():
    try:
        s=one_row("""SELECT (SELECT COUNT(*) FROM books) titles,
          (SELECT COALESCE(SUM(total_copies),0) FROM books) copies,
          (SELECT COALESCE(SUM(available_copies),0) FROM books) available,
          (SELECT COUNT(*) FROM borrow_records WHERE status='ISSUED') active,
          (SELECT COUNT(*) FROM borrow_records WHERE status='ISSUED' AND due_date<CURRENT_DATE) overdue,
          (SELECT COUNT(*) FROM students) students""")
        popular=all_rows("""SELECT b.title label,COUNT(br.borrow_id)::int count FROM books b
          LEFT JOIN borrow_records br USING(book_id) GROUP BY b.book_id ORDER BY count DESC,label LIMIT 5""")
        cats=all_rows("""SELECT c.category_name label,COUNT(br.borrow_id)::int count FROM categories c
          LEFT JOIN books b USING(category_id) LEFT JOIN borrow_records br USING(book_id)
          GROUP BY c.category_id ORDER BY count DESC,label""")
        monthly=all_rows("""SELECT TO_CHAR(m,'Mon YY') label,COALESCE(x.n,0)::int count FROM
          generate_series(date_trunc('month',CURRENT_DATE)-INTERVAL '5 months',date_trunc('month',CURRENT_DATE),INTERVAL '1 month') m
          LEFT JOIN (SELECT date_trunc('month',issue_date) m,COUNT(*) n FROM borrow_records GROUP BY 1) x USING(m) ORDER BY m""")
        return jsonify({"stats":s,"popular":popular,"categories":cats,"monthly":monthly})
    except Exception as e:return err(e,500)
@app.get("/api/books")
def books():
    q=(request.args.get("q") or "").strip()
    return jsonify(all_rows("""SELECT b.book_id,b.isbn,b.title,b.author,b.total_copies,b.available_copies,
      c.category_name FROM books b LEFT JOIN categories c USING(category_id)
      WHERE %s='' OR b.title ILIKE %s OR b.author ILIKE %s OR COALESCE(b.isbn,'') ILIKE %s
      ORDER BY b.title LIMIT 500""",(q,f"%{q}%",f"%{q}%",f"%{q}%")))
@app.post("/api/books")
def add_book():
    d=request.get_json(silent=True) or {}
    title=(d.get("title") or "").strip(); author=(d.get("author") or "").strip()
    try: copies=int(d.get("total_copies",1))
    except (ValueError,TypeError): return err("Total copies must be a whole number.")
    if not title or not author or copies<1:return err("Title, author and at least one copy are required.")
    try:
        with connect() as c:
            with c.cursor() as cur:
                cat=(d.get("category_name") or "Computer Science").strip()
                cur.execute("INSERT INTO categories(category_name) VALUES(%s) ON CONFLICT(category_name) DO UPDATE SET category_name=EXCLUDED.category_name RETURNING category_id",(cat,))
                cid=cur.fetchone()["category_id"]
                cur.execute("""INSERT INTO books(isbn,title,author,category_id,publisher,publication_year,total_copies,available_copies)
                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s) RETURNING book_id""",
                  ((d.get("isbn") or "").strip() or None,title,author,cid,(d.get("publisher") or "").strip() or None,
                   int(d["publication_year"]) if d.get("publication_year") else None,copies,copies))
                bid=cur.fetchone()["book_id"]
        return jsonify({"message":"Book added successfully","book_id":bid}),201
    except UniqueViolation:return err("That ISBN already exists.",409)
    except Exception as e:return err(e,400)
@app.get("/api/students")
def students():
    q=(request.args.get("q") or "").strip()
    return jsonify(all_rows("""SELECT student_id,usn,full_name,department,email FROM students
      WHERE %s='' OR usn ILIKE %s OR full_name ILIKE %s ORDER BY full_name LIMIT 500""",(q,f"%{q}%",f"%{q}%")))
@app.post("/api/students")
def add_student():
    d=request.get_json(silent=True) or {}; usn=(d.get("usn") or "").strip().upper(); name=(d.get("full_name") or "").strip()
    if not usn or not name:return err("USN and full name are required.")
    try:
        r=one_row("INSERT INTO students(usn,full_name,department,email) VALUES(%s,%s,%s,%s) RETURNING student_id",
          (usn,name,(d.get("department") or "CSE").strip(),(d.get("email") or "").strip() or None))
        return jsonify({"message":"Student registered","student_id":r["student_id"]}),201
    except UniqueViolation:return err("That USN is already registered.",409)
    except Exception as e:return err(e,400)
@app.get("/api/loans")
def loans():
    status=(request.args.get("status") or "").upper()
    return jsonify(all_rows("""SELECT br.borrow_id,b.title,s.usn,s.full_name,br.issue_date,br.due_date,br.return_date,br.status,
      CASE WHEN br.status='ISSUED' AND br.due_date<CURRENT_DATE THEN CURRENT_DATE-br.due_date ELSE 0 END days_overdue
      FROM borrow_records br JOIN books b USING(book_id) JOIN students s USING(student_id)
      WHERE %s='' OR br.status=%s ORDER BY br.issue_date DESC,br.borrow_id DESC LIMIT 500""",(status,status)))
@app.post("/api/loans")
def issue():
    d=request.get_json(silent=True) or {}
    try: bid=int(d["book_id"]); sid=int(d["student_id"]); due=date.fromisoformat(d.get("due_date") or (date.today()+timedelta(days=14)).isoformat())
    except Exception:return err("Select a valid book, student and due date.")
    if due<date.today():return err("Due date cannot be in the past.")
    try:
        with connect() as c:
            with c.cursor() as cur:
                cur.execute("SELECT available_copies FROM books WHERE book_id=%s FOR UPDATE",(bid,)); b=cur.fetchone()
                if not b:return err("Book not found.",404)
                if b["available_copies"]<1:return err("No copies available.",409)
                cur.execute("SELECT student_id FROM students WHERE student_id=%s",(sid,))
                if not cur.fetchone():return err("Student not found.",404)
                cur.execute("INSERT INTO borrow_records(book_id,student_id,issue_date,due_date,status) VALUES(%s,%s,CURRENT_DATE,%s,'ISSUED') RETURNING borrow_id",(bid,sid,due))
                lid=cur.fetchone()["borrow_id"]
                cur.execute("UPDATE books SET available_copies=available_copies-1 WHERE book_id=%s",(bid,))
        return jsonify({"message":"Book issued","borrow_id":lid}),201
    except Exception as e:return err(e,400)
@app.post("/api/loans/<int:lid>/return")
def return_book(lid):
    try:
        with connect() as c:
            with c.cursor() as cur:
                cur.execute("SELECT book_id,status FROM borrow_records WHERE borrow_id=%s FOR UPDATE",(lid,)); r=cur.fetchone()
                if not r:return err("Borrow record not found.",404)
                if r["status"]=="RETURNED":return err("Already returned.",409)
                cur.execute("UPDATE borrow_records SET status='RETURNED',return_date=CURRENT_DATE WHERE borrow_id=%s",(lid,))
                cur.execute("UPDATE books SET available_copies=LEAST(total_copies,available_copies+1) WHERE book_id=%s",(r["book_id"],))
        return jsonify({"message":"Book returned"})
    except Exception as e:return err(e,500)
@app.get("/api/analytics")
def analytics():
    return jsonify({
      "popular":all_rows("""SELECT b.title,b.author,COUNT(br.borrow_id)::int times_borrowed FROM books b LEFT JOIN borrow_records br USING(book_id) GROUP BY b.book_id ORDER BY times_borrowed DESC,b.title LIMIT 10"""),
      "categories":all_rows("""SELECT c.category_name,COUNT(br.borrow_id)::int borrowing_count FROM categories c LEFT JOIN books b USING(category_id) LEFT JOIN borrow_records br USING(book_id) GROUP BY c.category_id ORDER BY borrowing_count DESC"""),
     "monthly": all_rows("""
    SELECT
        TO_CHAR(DATE_TRUNC('month', issue_date), 'YYYY-MM') AS month_label,
        COUNT(*)::int AS borrowing_count
    FROM borrow_records
    WHERE issue_date >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY 1
    ORDER BY 1
"""),
      "overdue":all_rows("""SELECT s.usn,s.full_name,b.title,br.due_date,(CURRENT_DATE-br.due_date)::int days_overdue FROM borrow_records br JOIN students s USING(student_id) JOIN books b USING(book_id) WHERE br.status='ISSUED' AND br.due_date<CURRENT_DATE ORDER BY br.due_date""")})
if __name__=="__main__":
    app.run(host=os.getenv("FLASK_HOST","127.0.0.1"),port=int(os.getenv("FLASK_PORT","5000")),debug=os.getenv("FLASK_DEBUG","1")=="1")
