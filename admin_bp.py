from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, User, StudentRegistration

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Decorator to restrict to admin
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return func(*args, **kwargs)
    return wrapper

from flask_login import current_user
from models import StudentRegistration, User
from flask import session
from datetime import datetime

@admin_bp.route("/dashboard")
@login_required
@admin_required
def admin_dashboard():
    students = StudentRegistration.query.all()
    teachers = User.query.filter_by(role="teacher").all()

    # Stats
    total_students = len(students)
    total_teachers = len(teachers)

    # Count registered students today or recently
    new_students = StudentRegistration.query.filter(
        StudentRegistration.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()

    # Count logged-in users (using Flask-Login session tracking)
    # For simplicity, assuming you track login in session or User.is_authenticated
    logged_in_students = User.query.filter_by(role="student").filter_by(is_authenticated=True).count()
    logged_in_teachers = User.query.filter_by(role="teacher").filter_by(is_authenticated=True).count()
    logged_in_admins = User.query.filter_by(role="admin").filter_by(is_authenticated=True).count()

    return render_template(
        "admin_dashboard.html",
        students=students,
        teachers=teachers,
        total_students=total_students,
        total_teachers=total_teachers,
        new_students=new_students,
        logged_in_students=logged_in_students,
        logged_in_teachers=logged_in_teachers,
        logged_in_admins=logged_in_admins
    )



# View Student
@admin_bp.route("/student/<int:id>")
@login_required
@admin_required
def view_student(id):
    student = StudentRegistration.query.get_or_404(id)
    return render_template("view_student.html", student=student)

# Delete Student
@admin_bp.route("/student/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_student(id):
    student = StudentRegistration.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully!", "success")
    return redirect(url_for("admin.admin_dashboard"))

# Edit Teacher
@admin_bp.route("/teacher/edit/<int:id>", methods=["GET","POST"])
@login_required
@admin_required
def edit_teacher(id):
    teacher = User.query.get_or_404(id)
    if request.method == "POST":
        teacher.username = request.form["username"]
        teacher.email = request.form["email"]
        db.session.commit()
        flash("Teacher updated successfully!", "success")
        return redirect(url_for("admin.admin_dashboard"))
    return render_template("edit_teacher.html", teacher=teacher)
