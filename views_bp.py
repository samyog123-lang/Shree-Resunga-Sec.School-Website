from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from flask_login import login_required, current_user
from models import db, StudentRegistration
from datetime import datetime
import requests
import os,uuid,re
from werkzeug.utils import secure_filename
views_bp = Blueprint('views', __name__)
import uuid
from sqlalchemy import func
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, StudentRegistration
from werkzeug.utils import secure_filename
from datetime import datetime
import os

ADMISSION_FEE = 1500
ESEWA_MERCHANT_ID = "9769296077"  


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views_bp.route("/")
def homepage():
    return render_template("homepage.html")


@views_bp.route("/admin-dashboard")
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('views.homepage'))

    total_students = StudentRegistration.query.count()
    today = datetime.utcnow().date()
    today_count = StudentRegistration.query.filter(
        db.func.date(StudentRegistration.created_at) == today
    ).count()

    students = StudentRegistration.query.order_by(StudentRegistration.created_at.desc()).all()

    return render_template("admin_dashboard.html",
                           total_students=total_students,
                           today_count=today_count,
                           students=students)


@views_bp.route("/teacher-dashboard")
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash("Access denied!", "danger")
        return redirect(url_for('views.homepage'))

    return render_template("teacher_dashboard.html")

@views_bp.route("/student-dashboard")
@login_required
def student_dashboard():
    if current_user.is_authenticated and current_user.role != 'student':
        flash("Access denied!", "danger")
        return redirect(url_for('views.homepage'))


return render_template("student_dashboard.html")

UPLOAD_FOLDER = "static/uploads/certificates"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@views_bp.route("/admission_form", methods=["GET", "POST"])
def admissions():
    current_year = datetime.utcnow().year

    if request.method == "POST":
        try:
            name = request.form.get("name").strip()
            email = request.form.get("email").strip().lower()
            address = request.form.get("address").strip()
            contact = request.form.get("contact").strip()
            applying_class = request.form.get("applying_class").strip()
            previous_batch_year = int(request.form.get("batch"))

            if not re.match(r'^[a-zA-Z ]{3,}$', name):
                flash("Enter a valid full name.", "danger")
                return redirect(url_for("views.admissions"))

            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                flash("Invalid email address.", "danger")
                return redirect(url_for("views.admissions"))

            if StudentRegistration.query.filter(func.lower(StudentRegistration.email) == email).first():
                flash("Email already registered.", "danger")
                return redirect(url_for("views.admissions"))

            if not re.match(r'^(98|97)\d{8}$', contact):
                flash("Enter a valid 10-digit Nepali mobile number.", "danger")
                return redirect(url_for("views.admissions"))


            certificate = request.files.get("certificate")
            if not certificate or certificate.filename == "":
                flash("Upload previous certificate.", "danger")
                return redirect(url_for("views.admissions"))

            if not allowed_file(certificate.filename):
                flash("Only PDF, JPG, PNG allowed.", "danger")
                return redirect(url_for("views.admissions"))

            ext = certificate.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            certificate.save(filepath)

            transaction_uuid = str(uuid.uuid4())
            student = StudentRegistration(
                name=name,
                email=email,
                address=address,
                contact=contact,
                applying_class=applying_class,
                previous_batch_year=previous_batch_year,
                certificate_filename=filename,
                payment_method="eSewa",
                payment_status="pending",
                transaction_uuid=transaction_uuid,
                amount_paid=ADMISSION_FEE
            )
            db.session.add(student)
            db.session.commit()

            return render_template(
                "esewa_payment.html",
                tAmt=ADMISSION_FEE,
                amt=ADMISSION_FEE,
                txAmt=0,
                scAmt=0,
                pid=transaction_uuid,
                su=url_for("views.esewa_success", _external=True),
                fu=url_for("views.esewa_failure", _external=True),
                merchant_id=ESEWA_MERCHANT_ID
            )

        except Exception as e:
            print("ADMISSION ERROR:", e)
            flash("Something went wrong. Try again.", "danger")
            return redirect(url_for("views.admissions"))

    return render_template("admission_form.html", current_year=current_year)


@views_bp.route("/payment/success")
def esewa_success():
    transaction_uuid = request.args.get("pid")
    ref_id = request.args.get("refId")

    if not transaction_uuid or not ref_id:
        flash("Invalid payment response.", "danger")
        return redirect(url_for("views.admissions"))

    student = StudentRegistration.query.filter_by(transaction_uuid=transaction_uuid).first()
    if student:
        student.payment_status = "paid"
        student.payment_reference = ref_id
        db.session.commit()
        flash("Payment successful! Admission completed.", "success")
    else:
        flash("Payment received but student record not found.", "danger")

    return redirect(url_for("views.student_dashboard"))

@views_bp.route("/payment/failure")
def esewa_failure():
    flash("Payment failed or cancelled.", "danger")
    return redirect(url_for("views.admissions"))



@views_bp.route("/about-us")
def about_us():
    return render_template("aboutus.html")
@views_bp.route("/teacher_about-us")
def teacherabout_us():
    return render_template("teacheraboutus.html")
@views_bp.route("/student_about-us")
def studentabout_us():
    return render_template("studentaboutus.html")


@views_bp.route("/academics")
@login_required
def academics():
    return render_template("academics.html")
@views_bp.route("/teacher_academics")
@login_required
def teacheracademics():
    return render_template("teacheracademics.html")
@views_bp.route("/student_academics")
@login_required
def studentacademics():
    return render_template("studentacademics.html")


@views_bp.route("/chairmanssms")
@login_required
def chairmanssms():
    return render_template("chairmanssms.html")
@views_bp.route("/teacher_chairmanssms")
@login_required
def teacherchairmanssms():
    return render_template("teacherchairmanssms.html")
@views_bp.route("/student_chairmanssms")
@login_required
def studentchairmanssms():
    return render_template("studentchairmanssms.html")


@views_bp.route("/achievements")
@login_required
def achievements():
    return render_template("achievements.html")
@views_bp.route("/teacher_achievements")
@login_required
def teacherachievements():
    return render_template("teacherachievements.html")
@views_bp.route("/student_achievements")
@login_required
def studentachievements():
    return render_template("studentachievements.html")


@views_bp.route("/childclub")
@login_required
def childclub():
    return render_template("childclub.html")
@views_bp.route("/teacher_childclub")
@login_required
def teacherchildclub():
    return render_template("teacherchildclub.html")
@views_bp.route("/student_childclub")
@login_required
def studentchildclub():
    return render_template("studentchildclub.html")


@views_bp.route("/community")
@login_required
def community():
    return render_template("community.html")
@views_bp.route("/teacher_community")
@login_required
def teachercommunity():
    return render_template("teachercommunity.html")
@views_bp.route("/student_community")
@login_required
def studentcommunity():
    return render_template("studentcommunity.html")


@views_bp.route("/creativeworks")
@login_required
def creativeworks():
    return render_template("creativeworks.html")
@views_bp.route("/teacher_creativeworks")
@login_required
def teachercreativeworks():
    return render_template("teachercreativeworks.html")
@views_bp.route("/student_creativeworks")
@login_required
def studentcreativeworks():
    return render_template("studentcreativeworks.html")


@views_bp.route("/events")
@login_required
def events():
    return render_template("events.html")
@views_bp.route("/teacher_events")
@login_required
def teacherevents():
    return render_template("teacherevents.html")
@views_bp.route("/student_events")
@login_required
def studentevents():
    return render_template("studentevents.html")


@views_bp.route("/facilities")
@login_required
def facilities():
    return render_template("facilities.html")
@views_bp.route("/teacher_facilities")
@login_required
def teacherfacilities():
    return render_template("teacherfacilities.html")
@views_bp.route("/student_facilities")
@login_required
def studentfacilities():
    return render_template("studentfacilities.html")

@views_bp.route("/festivals")
@login_required
def festivals():
    return render_template("festivals.html")
@views_bp.route("/teacher_festivals")
@login_required
def teacherfestivals():
    return render_template("teacherfestivals.html")
@views_bp.route("/student_festivals")
@login_required
def studentfestivals():
    return render_template("studentfestivals.html")


@views_bp.route("/foundingstory")
@login_required
def foundingstory():
    return render_template("foundingstory.html")
@views_bp.route("/teacher_foundingstory")
@login_required
def teacherfoundingstory():
    return render_template("teacherfoundingstory.html")
@views_bp.route("/student_foundingstory")
@login_required
def studentfoundingstory():
    return render_template("studentfoundingstory.html")



@views_bp.route("/Galleryacademics")
@login_required
def Galleryacademics():
    return render_template("galleryacademics.html")
@views_bp.route("/teacher_Galleryacademics")
@login_required
def teacherGalleryacademics():
    return render_template("teachergalleryacademics.html")
@views_bp.route("/student_Galleryacademics")
@login_required
def studentGalleryacademics():
    return render_template("studentgalleryacademics.html")

@views_bp.route("/holistic")
@login_required
def holistic():
    return render_template("Holistic.html")
@views_bp.route("/teacher_holistic")
@login_required
def teacherholistic():
    return render_template("teacherHolistic.html")
@views_bp.route("/student_holistic")
@login_required
def studentholistic():
    return render_template("studentHolistic.html")

@views_bp.route("/infastucture")
@login_required
def infastucture():
    return render_template("infastucture.html")
@views_bp.route("/teacher_infastucture")
@login_required
def teacherinfastucture():
    return render_template("teacherinfastucture.html")
@views_bp.route("/student_infastucture")
@login_required
def studentinfastucture():
    return render_template("studentinfastucture.html")

@views_bp.route("/introduction")
@login_required
def introduction():
    return render_template("introduction.html")
@views_bp.route("/teacher_introduction")
@login_required
def teacherintroduction():
    return render_template("teacherintroduction.html")
@views_bp.route("/student_introduction")
@login_required
def studentintroduction():
    return render_template("studentintroduction.html")


@views_bp.route("/milestone")
@login_required
def milestone():
    return render_template("milestone.html")
@views_bp.route("/teacher_milestone")
@login_required
def teachermilestone():
    return render_template("teachermilestone.html")
@views_bp.route("/student_milestone")
@login_required
def studentmilestone():
    return render_template("studentmilestone.html")

@views_bp.route("/ourteam")
@login_required
def ourteam():
    return render_template("ourteam.html")
@views_bp.route("/teacher_ourteam")
@login_required
def teacherourteam():
    return render_template("teacherourteam.html")
@views_bp.route("/student_ourteam")
@login_required
def studentourteam():
    return render_template("studentourteam.html")

@views_bp.route("/principalssms")
@login_required
def principalssms():
    return render_template("principalssms.html")
@views_bp.route("/teacher_principalssms")
@login_required
def teacherprincipalssms():
    return render_template("teacherprincipalssms.html")
@views_bp.route("/student_principalssms")
@login_required
def studentprincipalssms():
    return render_template("studentprincipalssms.html")


@views_bp.route("/viceprincipalssms")
@login_required
def viceprincipalssms():
    return render_template("viceprincipalssms.html")
@views_bp.route("/teacher_viceprincipalssms")
@login_required
def teacherviceprincipalssms():
    return render_template("teacherviceprincipalssms.html")
@views_bp.route("/student_viceprincipalssms")
@login_required
def studentviceprincipalssms():
    return render_template("studentviceprincipalssms.html")


@views_bp.route("/redcross")
@login_required
def redcross():
    return render_template("redcross.html")
@views_bp.route("/teacher_redcross")
@login_required
def teacherredcross():
    return render_template("teacherredcross.html")
@views_bp.route("/studentredcross")
@login_required
def studentredcross():
    return render_template("studentredcross.html")


@views_bp.route("/scouting")
@login_required
def scouting():
    return render_template("scouting.html")
@views_bp.route("/teacher_scouting")
@login_required
def teacherscouting():
    return render_template("teacherscouting.html")
@views_bp.route("/studentscouting")
@login_required
def studentscouting():
    return render_template("studentscouting.html")


@views_bp.route("/sports")
@login_required
def sports():
    return render_template("sports.html")
@views_bp.route("/teacher_sports")
@login_required
def teachersports():
    return render_template("teachersports.html")
@views_bp.route("/studentsports")
@login_required
def studentsports():
    return render_template("studentsports.html")


@views_bp.route("/tour")
@login_required
def tour():
    return render_template("tour.html")
@views_bp.route("/teacher_tour")
@login_required
def teachertour():
    return render_template("teachertour.html")
@views_bp.route("/studenttour")
@login_required
def studenttour():
    return render_template("studenttour.html")



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

@views_bp.route('/news')
def news():
    return render_template("news.html")
# Single news detail pag
@views_bp.route('/news/<int:news_id>')
def news_detail(news_id):
    return render_template('news_detail.html', news_id=news_id)
@views_bp.route("/student_news")
def studentnews():
    return render_template("studentnews.html")
@views_bp.route("/teacher_news")
def teachernews():
    return render_template("teachernews.html")

@views_bp.route("/contacts")
def contact():
    return render_template("contact.html")
@views_bp.route("/teacher_contacts")
def teachercontact():
    return render_template("teachercontact.html")
@views_bp.route("/Student_contacts")
def studentcontact():
    return render_template("studentcontact.html")


# -------------------
# Gallery Pages
# -------------------
@views_bp.route("/gallery")
def Gallery():
    return render_template("Gallery.html")
@views_bp.route("/teacher_gallery")
def teacherGallery():
    return render_template("teacherGallery.html")
@views_bp.route("/studentgallery")
def studentGallery():
    return render_template("studentGallery.html")

@views_bp.route("/gallery/<string:section>")
@login_required
def gallery_detail(section):
    # Frontend-only content mapping
    sections = {
        "events": {"title": "School Events", "image": "Images/01vision.jpg", "description": "All school events and celebrations."},
        "academics": {"title": "Academic Highlights", "image": "Images/10latest.jpg", "description": "Highlights from academic achievements."},
        "team": {"title": "Our Team", "image": "Images/logo1.jpg", "description": "Meet our dedicated teachers and staff."},
        "infrastructure": {"title": "Infrastructure", "image": "Images/labs.jpg", "description": "State-of-the-art school facilities."},
        "facilities": {"title": "Facilities", "image": "Images/lab.jpg", "description": "Library, labs, sports & more."},
        "sports": {"title": "Sports Activities", "image": "Images/volley.jpg", "description": "All sports events and teams."},
        "festivals": {"title": "Festivals", "image": "Images/puja.jpg", "description": "Cultural and religious festivals."},
        "creativeworks": {"title": "Creative Works", "image": "Images/creative.jpg", "description": "Student creative projects."},
        "tours": {"title": "Trips & Tours", "image": "Images/tour.jpg", "description": "Educational and recreational trips."}
    }

    section_data = sections.get(section)
    if not section_data:
        return "Section not found", 404

    return render_template("gallery_detail.html", section=section_data)

@views_bp.route('/members')
def members():
    # Teachers
    teachers = [
        {"name": f"Teacher {i+1}", "post": "Subject Teacher", "img": f"teachers/t{i+1}.jpg"}
        for i in range(50)
    ]

    # Management
    management = [
        {"name": f"Member {i+1}", "post": "Position", "img": f"management/m{i+1}.jpg"}
        for i in range(50)
    ]

    # Guardians
    guardians = [
        {"name": f"Guardian {i+1}", "post": "Parent Representative", "img": f"guardian/g{i+1}.jpg"}
        for i in range(50)
    ]

    return render_template('members.html', teachers=teachers, management=management, guardians=guardians)
# --- API route for books ---
@views_bp.route("/api/books")
@login_required
def api_books():
    query = request.args.get("q", "")
    if not query:
        return jsonify([])

    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=12"
    try:
        r = requests.get(url)
        data = r.json()
        items = data.get("items", [])
        books = []
        for item in items:
            info = item.get("volumeInfo", {})
            books.append({
                "title": info.get("title", "No title"),
                "authors": ", ".join(info.get("authors", ["Unknown author"])),
                "description": (info.get("description") or "")[:100],
                "thumbnail": info.get("imageLinks", {}).get("thumbnail", ""),
                "link": info.get("previewLink", "#")
            })
        return jsonify(books)
    except Exception as e:
        print(e)
        return jsonify([])
