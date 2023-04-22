from flask import Flask, render_template , request , redirect, session , make_response , Response
import sqlite3
from werkzeug.utils import secure_filename
app = Flask(__name__, static_url_path='/static')
app.secret_key = "crth5yjt7ynp98un"

@app.route("/")  
def index():
    return render_template("index.html")

@app.route("/login")  
def login():
    return render_template("student/login.html")

@app.route("/signin", methods =["GET", "POST"])  
def student_login():
    if request.method == "POST":
        con = sqlite3.connect("database.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from student WHERE email=? AND password=?",(request.form["email"],request.form["password"]))  
        rows = cur.fetchall()
        if len(rows)>0:
            for row in rows:
                session["id"]=row["id"]
                session["name"]=row["name"]
                session["dept"]=row["dept"]
                session["sem"]=row["sem"]
            return redirect("/student")
        else:
            return redirect("/login?err=email or password is wrong!")
    return redirect("/")

@app.route("/register")  
def register():
    return render_template("student/register.html")

@app.route("/signup", methods =["GET", "POST"])  
def student_register():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("INSERT into student(name , regno , dept,year,sem, email, password) values (?,?,?,?,?,?,?)",(request.form["name"],request.form["regno"],request.form["dept"],request.form["year"],request.form["sem"],request.form["email"],request.form["password"]))
        con.commit()
        return redirect("/login?msg=Signup Successfully!")
    return redirect("/")

@app.route("/student")  
def student():
    name=session["name"]
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from subject WHERE dept=? AND sem=?",(session["dept"],session["sem"]))  
    rows = cur.fetchall()
    return render_template("student/home.html",name=name,rows=rows)

@app.route("/student/add", methods =["GET", "POST"])  
def student_feedback_add():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("INSERT into feedback(data, subjectid ,studentid) values (?,?,?)",(request.form["data"],request.form["subjectid"],session["id"]))
        con.commit()
        return redirect("/student/feedback?msg=Feedback Submitted Successfully!")
    return redirect("/")

@app.route("/student/feedback")  
def student_feedback():
    name=session["name"]
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select feedback.id,feedback.data,subject.subject from feedback INNER JOIN subject ON feedback.subjectid=subject.id WHERE feedback.studentid=?",(str(session["id"])))  
    rows = cur.fetchall()
    return render_template("student/feedback.html",name=name,rows=rows)

@app.route("/student/feedback/delete", methods =["GET", "POST"])  
def student_feedback_delete():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("DELETE FROM feedback WHERE id=?",(request.form["id"]))
        con.commit()
        return redirect("/student/feedback?msg=Feedback Deleted Successfully!")
    return redirect("/")


@app.route("/staff")  
def staff():
    return render_template("staff/login.html")

@app.route("/staff/login", methods =["GET", "POST"])  
def staff_login():
    if request.method == "POST":
        con = sqlite3.connect("database.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from staff WHERE email=? AND password=?",(request.form["email"],request.form["password"]))  
        rows = cur.fetchall()
        if len(rows)>0:
            for row in rows:
                session["staffid"]=row["id"]
                session["staffname"]=row["name"]
            return redirect("/staff/home")
        else:
            return redirect("/staff?err=email or password is wrong!")
    return redirect("/staff?err=email or password is wrong!")

@app.route("/staff/home")  
def staff_home():  
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select feedback.id from feedback INNER JOIN subject ON feedback.subjectid=subject.id WHERE subject.staffid=?",(str(session["staffid"])))  
    rows = cur.fetchall()
    return render_template("staff/home.html",total=len(rows))

@app.route("/staff/feedback")  
def staff_feedback():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select feedback.id,feedback.data,subject.subject from feedback INNER JOIN subject ON feedback.subjectid=subject.id WHERE subject.staffid=?",(str(session["staffid"])))  
    rows = cur.fetchall()
    return render_template("staff/feedback.html",staffname=session["staffname"],rows=rows)

@app.route("/staff/feedback/delete", methods =["GET", "POST"])  
def staff_feedback_delete():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("DELETE FROM feedback WHERE id=?",(request.form["id"]))
        con.commit()
        return redirect("/staff/feedback?msg=Feedback Deleted Successfully!")
    return redirect("/")


@app.route("/admin")  
def admin():
    return render_template("admin/login.html")

@app.route("/admin/login", methods =["GET", "POST"])  
def admin_login():
    if request.method == "POST":
        if request.form["email"]=="admin@gmail.com" and request.form["password"]=="admin":
            return redirect("/admin/home")
        else:
            return redirect("/admin?err=email or password is wrong!")
    return redirect("/admin?err=email or password is wrong!")

@app.route("/admin/home")  
def admin_home():  
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select id from staff")  
    staff = cur.fetchall()
    cur.execute("select id from student")  
    student = cur.fetchall()
    cur.execute("select id from feedback")  
    feedback = cur.fetchall()
    cur.execute("select id from subject")  
    subject = cur.fetchall()
    return render_template("admin/home.html",staff=len(staff),student=len(student),feedback=len(feedback),subject=len(subject))

@app.route("/admin/staff")  
def admin_staff():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from staff ORDER BY id DESC")  
    rows = cur.fetchall()
    return render_template("admin/staff.html",rows = rows)

@app.route("/admin/staff/add", methods =["GET", "POST"])  
def admin_staff_add():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("INSERT into staff(name , staffid , dept, email, password) values (?,?,?,?,?)",(request.form["name"],request.form["staffid"],request.form["dept"],request.form["email"],request.form["password"]))
        con.commit()
        return redirect("/admin/staff?msg=Staff added Successfully!")
    return redirect("/admin")

@app.route("/admin/staff/delete", methods =["GET", "POST"])  
def admin_staff_delete():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("DELETE FROM staff WHERE id=?",(request.form["id"]))
        con.commit()
        return redirect("/admin/staff?msg=Staff Deleted Successfully!")
    return redirect("/admin")

@app.route("/admin/subject")  
def admin_subject():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select subject.id, subject.subject, subject.dept, subject.sem, staff.name from subject INNER JOIN staff ON subject.staffid=staff.id ORDER BY subject.id DESC")
    rows = cur.fetchall()
    cur.execute("select id,name from staff ORDER BY id DESC")  
    staff = cur.fetchall()
    return render_template("admin/subject.html",rows = rows,staff=staff)

@app.route("/admin/subject/add", methods =["GET", "POST"])  
def admin_subject_add():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("INSERT into subject(subject, staffid , dept, sem) values (?,?,?,?)",(request.form["subject"],request.form["staffid"],request.form["dept"],request.form["sem"]))
        con.commit()
        return redirect("/admin/subject?msg=Staff added Successfully!")
    return redirect("/admin")


@app.route("/admin/subject/delete", methods =["GET", "POST"])  
def admin_subject_delete():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("DELETE FROM subject WHERE id=?",(request.form["id"]))
        con.commit()
        return redirect("/admin/subject?msg=Subject Deleted Successfully!")
    return redirect("/admin")

@app.route("/admin/student")  
def admin_student():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select * from student ORDER BY id DESC")  
    rows = cur.fetchall()
    return render_template("admin/student.html",rows = rows)

@app.route("/admin/student/delete", methods =["GET", "POST"])  
def admin_student_delete():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("DELETE FROM student WHERE id=?",(request.form["id"]))
        con.commit()
        return redirect("/admin/student?msg=Student Deleted Successfully!")
    return redirect("/admin")

@app.route("/admin/feedback")  
def admin_feedback():  
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  
    cur.execute("select feedback.id,feedback.data,subject.subject from feedback INNER JOIN subject ON feedback.subjectid=subject.id")  
    rows = cur.fetchall()
    return render_template("admin/feedback.html",rows = rows)

@app.route("/admin/feedback/delete", methods =["GET", "POST"])  
def admin_feedback_delete():
    if request.method == "POST":
        con = sqlite3.connect("database.db")
        con.execute("DELETE FROM feedback WHERE id=?",(request.form["id"]))
        con.commit()
        return redirect("/admin/feedback?msg=Feddback Deleted Successfully!")
    return redirect("/admin")


@app.route("/table")
def table():
    con = sqlite3.connect("database.db")
    con.execute("CREATE TABLE student (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,dept TEXT NOT NULL,year TEXT NOT NULL,sem TEXT NOT NULL,regno TEXT NOT NULL,email TEXT NOT NULL,password TEXT NOT NULL)")
    con.execute("CREATE TABLE staff (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,dept TEXT NOT NULL,staffid TEXT NOT NULL,email TEXT NOT NULL,password TEXT NOT NULL)")
    con.execute("CREATE TABLE subject (id INTEGER PRIMARY KEY AUTOINCREMENT,subject TEXT NOT NULL,staffid TEXT NOT NULL,dept TEXT NOT NULL,sem TEXT NOT NULL)")
    con.execute("CREATE TABLE feedback(id INTEGER PRIMARY KEY AUTOINCREMENT,data INTEGER NOT NULL,subjectid TEXT NOT NULL,studentid TEXT NOT NULL)")
    return "Table Created"