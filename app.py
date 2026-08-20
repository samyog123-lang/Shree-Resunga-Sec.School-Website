from flask import Flask
from models import db, User
from flask_login import LoginManager
import secrets
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# ---------------- CONFIG ----------------
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ---------------- DATABASE ----------------
db.init_app(app)

# ---------------- LOGIN MANAGER ----------------
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ---------------- BLUEPRINTS ----------------
from auth_bp import auth_bp
from views_bp import views_bp
from admin_bp import admin_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(views_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

# ---------------- CREATE TABLES & DEFAULT ADMIN ----------------
with app.app_context():
    db.create_all()

    # Create default admin if not exists
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        new_admin = User(
            username="Super Admin",
            email="admin@example.com",
            password_hash=generate_password_hash("admin123", method="pbkdf2:sha256"),
            role="admin"
        )
        db.session.add(new_admin)
        db.session.commit()
        print("Admin user created: admin@example.com / admin123")
    else:
        print("Admin user already exists.")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
