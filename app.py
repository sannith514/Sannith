from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user
from flask_login import LoginManager
from flask_login import current_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images')


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)  

    def set_password(self, password):
        """Create hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Provide helpful representation when printed."""
        return f'<User {self.username}>'
    

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    publish_date = db.Column(db.String(20), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    image_filename = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)  
    page_count = db.Column(db.Integer, nullable=True)  
    language = db.Column(db.String(50), nullable=True)  
    is_available = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'
    
    def set_attributes(self, form_data):
        for field in ['title', 'author', 'genre', 'publish_date', 'isbn', 'description', 'page_count', 'language']:
            if field in form_data:
                setattr(self, field, form_data[field])

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        publish_date = request.form.get('publish_date')
        isbn = request.form.get('isbn')
        image = request.files['image']
        description = request.form.get('description')
        page_count = request.form.get('page_count')
        language = request.form.get('language')
        is_available = bool(int(request.form.get('is_available')))

        
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))

        
        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            publish_date=publish_date,
            isbn=isbn,
            image_filename=image.filename,
            description=description,
            page_count=page_count,
            language=language,
            is_available=is_available
        )

        
        db.session.add(new_book)
        db.session.commit()

        flash('Book added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_book.html')

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.genre = request.form.get('genre')
        book.publish_date = request.form.get('publish_date')
        book.isbn = request.form.get('isbn')
        
        
        if 'image' in request.files and request.files['image'].filename != '':
            new_image = request.files['image']
            filename = secure_filename(new_image.filename)
            if filename != '':  
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                try:
                    new_image.save(image_path)
                    book.image_filename = filename
                except Exception as e:
                    flash(f'An error occurred while saving the file: {e}', 'error')
                    app.logger.error(f'File save error: {e}')
                    return render_template('edit_book.html', book=book)


        book.description = request.form.get('description')
        book.page_count = request.form.get('page_count')
        book.language = request.form.get('language')
        book.is_available = bool(int(request.form.get('is_available')))

        
        db.session.commit()

        flash('Book updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    
    book = Book.query.get_or_404(book_id)

    
    db.session.delete(book)
    db.session.commit()

    return jsonify({'message': 'Book deleted successfully'})

@app.route('/adminregister', methods=['GET', 'POST'])
def admin_register():
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.')
            return redirect(url_for('admin_register'))
        
        
        new_admin = User(username=username, email=email, is_admin=True)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        
        flash('Admin registration successful!')
        return redirect(url_for('admin_login'))

    return render_template('admin_register.html')

@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, is_admin=True).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Admin logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password or not an admin.', 'error')
            return render_template('admin_login.html')

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have access to the admin dashboard.', 'error')
        return redirect(url_for('index'))
    
    
    genre_tuples = Book.query.with_entities(Book.genre).distinct()
    genres = [genre[0] for genre in genre_tuples]  
    books = Book.query.all()
    return render_template('admin_dashboard.html', books=books, genres=genres)

@app.route('/admin/borrow_requests')
def borrow_requests():
    
    requests = BorrowRequest.query.all()
    return render_template('partials/borrow_requests.html', requests=requests)

@app.route('/admin/user_fines')
def user_fines():
    
    fines = Fine.query.all()
    return render_template('partials/user_fines.html', fines=fines)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')  
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.')
            return redirect(url_for('register'))
        
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        
        if user and user.is_admin:
            flash('Admins must log in through the admin portal.', 'error')
            return redirect(url_for('login'))

        if user is None or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.', 'error')
        else:
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('query', '')
    filter_by = request.args.get('filter_by', 'title')  
    genre_filter = request.args.get('genre', None)  

    query = Book.query

    
    if search_query:
        if filter_by == 'title':
            query = query.filter(Book.title.ilike(f'%{search_query}%'))
        elif filter_by == 'author':
            query = query.filter(Book.author.ilike(f'%{search_query}%'))
        elif filter_by == 'publish_date':
            query = query.filter(Book.publish_date.ilike(f'%{search_query}%'))
        
    
    if genre_filter:
        query = query.filter(Book.genre.ilike(f'%{genre_filter}%'))

    books = query.all()

    if books:
        
        return jsonify([{
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'publish_date': book.publish_date,
            'isbn': book.isbn,
            'image_filename': book.image_filename
        } for book in books])

    return jsonify([])  

@app.route('/')
def index():
    return render_template('index.html', books=Book.query.all())

@app.route('/explore_library')
def explore():
    
    genre_tuples = Book.query.with_entities(Book.genre).distinct()
    genres = [genre[0] for genre in genre_tuples]  
    books = Book.query.all()
    return render_template('explore.html', books=books, genres=genres)

@app.route('/borrow')
def borrow():
    
    genre_tuples = Book.query.with_entities(Book.genre).distinct()
    genres = [genre[0] for genre in genre_tuples]  
    books = Book.query.all()
    flash('The book is available in the library! You can visit and borrow it.', 'success')
    return render_template('explore.html', books=books, genres=genres)


if __name__ == '__main__':
    app.run(debug=True)
