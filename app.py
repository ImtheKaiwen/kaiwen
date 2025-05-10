from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import markdown2
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    profile_image = db.Column(db.String(200))
    bio = db.Column(db.Text)
    full_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    github = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    education = db.Column(db.String(200))  # Okul adı
    education_year = db.Column(db.String(50))  # Mezuniyet yılı
    education_field = db.Column(db.String(100))  # Bölüm
    skills = db.Column(db.Text)  # Yetenekler (virgülle ayrılmış)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    link = db.Column(db.String(200))
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))  # Comma-separated tags

class Research(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    research_id = db.Column(db.Integer, db.ForeignKey('research.id'), nullable=False)

# Routes
@app.route('/')
def home():
    projects = Project.query.order_by(Project.date_posted.desc()).limit(3).all()
    research_items = Research.query.order_by(Research.date_posted.desc()).limit(3).all()
    return render_template('home.html', projects=projects, research_items=research_items)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    projects = Project.query.order_by(Project.date_posted.desc()).all()
    return render_template('projects.html', projects=projects)

@app.route('/research')
def research():
    research_items = Research.query.order_by(Research.date_posted.desc()).all()
    return render_template('research.html', research_items=research_items)

@app.route('/research/<int:research_id>')
def research_detail(research_id):
    research = Research.query.get_or_404(research_id)
    
    # Kod bloklarını işle
    content = research.content
    
    # Markdown içeriğini HTML'e dönüştür
    html_content = markdown2.markdown(
        content,
        extras=[
            'fenced-code-blocks',  # ``` ile başlayan kod blokları için
            'tables',              # Tablolar için
            'header-ids',          # Başlık ID'leri için
            'code-friendly',       # Kod blokları için daha iyi destek
            'cuddled-lists',       # Liste formatlaması için
            'markdown-in-html',    # HTML içinde Markdown desteği
            'break-on-newline'     # Yeni satırları <br> olarak işle
        ]
    )
    
    # Kod bloklarına dil sınıfı ekle
    html_content = re.sub(
        r'<pre><code>', 
        '<pre><code class="language-plaintext">', 
        html_content
    )
    html_content = re.sub(
        r'<pre><code class="(.*?)">', 
        lambda m: f'<pre><code class="language-{m.group(1)}">', 
        html_content
    )
    
    research.content = html_content
    notes = Note.query.filter_by(research_id=research_id).all()
    return render_template('research_detail.html', research=research, notes=notes)

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    projects = Project.query.order_by(Project.date_posted.desc()).all()
    research_items = Research.query.order_by(Research.date_posted.desc()).all()
    return render_template('admin/dashboard.html', projects=projects, research_items=research_items)

@app.route('/admin/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.link = request.form.get('link')
        project.category = request.form.get('category')
        project.tags = request.form.get('tags')
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to make it unique
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                project.image_url = f"/static/uploads/{filename}"
        
        db.session.commit()
        flash('Proje başarıyla güncellendi', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_project.html', project=project)

@app.route('/admin/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Proje başarıyla silindi', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/research/<int:research_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_research(research_id):
    research = Research.query.get_or_404(research_id)
    if request.method == 'POST':
        research.title = request.form.get('title')
        research.content = request.form.get('content')
        research.category = request.form.get('category')
        db.session.commit()
        flash('Araştırma başarıyla güncellendi', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_research.html', research=research)

@app.route('/admin/research/<int:research_id>/delete', methods=['POST'])
@login_required
def delete_research(research_id):
    research = Research.query.get_or_404(research_id)
    db.session.delete(research)
    db.session.commit()
    flash('Araştırma başarıyla silindi', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/research/<int:research_id>/note/new', methods=['GET', 'POST'])
@login_required
def new_note(research_id):
    research = Research.query.get_or_404(research_id)
    if request.method == 'POST':
        note = Note(
            title=request.form.get('title'),
            content=request.form.get('content'),
            research_id=research_id
        )
        db.session.add(note)
        db.session.commit()
        flash('Not başarıyla eklendi', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/new_note.html', research=research)

@app.route('/admin/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        # Handle image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to make it unique
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = f"/static/uploads/{filename}"
        
        project = Project(
            title=request.form.get('title'),
            description=request.form.get('description'),
            image_url=image_url,
            link=request.form.get('link'),
            category=request.form.get('category'),
            tags=request.form.get('tags')
        )
        db.session.add(project)
        db.session.commit()
        flash('Proje başarıyla eklendi', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/new_project.html')

@app.route('/admin/research/new', methods=['GET', 'POST'])
@login_required
def new_research():
    if request.method == 'POST':
        research = Research(
            title=request.form.get('title'),
            content=request.form.get('content'),
            category=request.form.get('category')
        )
        db.session.add(research)
        db.session.commit()
        flash('Araştırma başarıyla eklendi', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/new_research.html')

@app.route('/api/project/<int:project_id>')
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify({
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'image_url': project.image_url,
        'link': project.link,
        'category': project.category,
        'tags': project.tags,
        'date_posted': project.date_posted.strftime('%d %B %Y')
    })

@app.route('/api/research/<int:research_id>')
def get_research(research_id):
    research = Research.query.get_or_404(research_id)
    return jsonify({
        'id': research.id,
        'title': research.title,
        'content': research.content,
        'category': research.category,
        'date_posted': research.date_posted.strftime('%d %B %Y')
    })

@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        current_user.full_name = request.form.get('full_name')
        current_user.bio = request.form.get('bio')
        current_user.location = request.form.get('location')
        current_user.website = request.form.get('website')
        current_user.github = request.form.get('github')
        current_user.linkedin = request.form.get('linkedin')
        current_user.education = request.form.get('education')
        current_user.education_field = request.form.get('education_field')
        current_user.education_year = request.form.get('education_year')
        current_user.skills = request.form.get('skills')
        
        # Handle password change
        new_password = request.form.get('new_password')
        if new_password:
            current_user.set_password(new_password)
        
        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"profile_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_image = f"/static/uploads/{filename}"
        
        db.session.commit()
        flash('Profil bilgileriniz başarıyla güncellendi', 'success')
        return redirect(url_for('admin_profile'))
    
    return render_template('admin/profile.html')

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                full_name='Admin User',
                bio='Site yöneticisi'
            )
            admin.set_password('admin123')  # Change this password!
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True) 