# Mobility App - Rand Refinery

A Flask-based mobility and checklist management application for Rand Refinery operations. This application allows administrators and operators to manage plant sections, checklists, questions, and track locations.

## Features

- **User Authentication & Authorization**: Role-based access control (Master Admin, Administrator, Operator)
- **Checklist Management**: Create, edit, and manage checklists with questions
- **Location Tracking**: GPS integration for tracking operator locations
- **Plant Section Management**: Organize operations by plant sections
- **Question & Answer System**: Track answered and unanswered questions
- **Admin Panel**: Comprehensive admin interface for system management

## Tech Stack

- **Backend**: Flask (Python 3.11)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy with Flask-Migrate (Alembic)
- **Authentication**: bcrypt for password hashing
- **Location Services**: geopy, gps3, gpsd
- **Web Server**: Gunicorn (Production)
- **Additional Libraries**: 
  - python-dotenv (Environment variables)
  - openpyxl (Excel file handling)
  - requests (HTTP requests)

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 12 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/IDBRSsimulator/Mobility_for-rand_refinery.git
   cd mobility_app
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv myvenv
   .\myvenv\Scripts\Activate.ps1

   # Linux/Mac
   python3 -m venv myvenv
   source myvenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**
   - Create a PostgreSQL database named `rand_refinary`
   - Update database credentials in `.env` file (see Configuration section)

5. **Run Database Migrations**
   ```bash
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   # Development
   python app.py

   # Production
   gunicorn app:app
   ```

## Configuration

### Database Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DB_NAME=rand_refinary
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# For Render.com or other cloud databases (optional)
DATABASE_URL=postgresql://user:password@host:port/database

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### Database Connection Settings

The application uses PostgreSQL with the following default configuration:

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| Database Name | `rand_refinary` | PostgreSQL database name |
| User | `postgres` | Database user |
| Password | *(set in .env)* | Database password |
| Host | `localhost` | Database host |
| Port | `5432` | PostgreSQL default port |

**Note**: For production deployment, use environment variables stored in `.env` file and never commit sensitive credentials to version control.

## Database Schema

The application uses the following main tables:

- `rand_refinary_registration` - User accounts and authentication
- `checklist_questions` - Questions for checklists
- `section_location` - Plant section locations
- `answers` - Stored answers from operators
- `plant_sections` - Plant section definitions
- `administrators` - Administrator assignments

## Project Structure

```
mobility_app/
├── app.py                  # Main Flask application
├── dbqueries.py           # Database query functions
├── encryption.py          # Password hashing utilities
├── requirements.txt       # Python dependencies
├── Procfile              # Gunicorn configuration for deployment
├── .env                  # Environment variables (create this)
├── migrations/           # Alembic database migrations
├── static/              # Static assets (CSS, images)
│   ├── images/
│   └── style/
├── templates/           # HTML templates
└── myvenv/             # Virtual environment

```

## User Roles

1. **Master Administrator**
   - Add/remove administrators
   - View all administrators
   - Full system access

2. **Administrator**
   - Create and manage checklists
   - Create and edit questions
   - View answers
   - Manage plant sections

3. **Operator**
   - Answer checklist questions
   - Update location information
   - View assigned checklists

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Admin Routes
- `/admin_create_checklist` - Create new checklists
- `/admin_create_questions` - Add questions to checklists
- `/admin_view_answers` - View submitted answers
- `/admin_modify_question` - Edit existing questions
- `/admin_delete_questions` - Remove questions

### Master Admin Routes
- `/masterAdmin_addAdmin` - Add new administrators
- `/masterAdmin_removeAdmin` - Remove administrators
- `/masterAdmin_viewAdmin` - View all administrators

### Operator Routes
- `/operator` - Operator dashboard
- `/findme` - Location tracking
- `/getlocation` - Get current location

## Database Migrations

The application uses Flask-Migrate (Alembic) for database migrations:

```bash
# Initialize migrations (first time only)
flask db init

# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## Security

- Passwords are hashed using bcrypt
- Session management with Flask sessions
- Environment variables for sensitive data
- SQL injection protection via parameterized queries

## Deployment

### Deploy to Render.com

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy using the Procfile configuration

### Deploy to Heroku

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

## Development

### Running in Development Mode

```bash
# Activate virtual environment
.\myvenv\Scripts\Activate.ps1  # Windows
source myvenv/bin/activate      # Linux/Mac

# Set Flask environment
set FLASK_ENV=development       # Windows
export FLASK_ENV=development    # Linux/Mac

# Run application
python app.py
```

### Code Structure

- **app.py**: Main application routes and logic
- **dbqueries.py**: Database operations and queries
- **encryption.py**: Password hashing functions
- **templates/**: Jinja2 HTML templates
- **static/**: CSS, JavaScript, and images

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database `rand_refinary` exists
- Verify firewall settings allow port 5432

### Migration Errors
```bash
# Reset migrations (WARNING: This will delete all data)
flask db downgrade base
flask db upgrade
```

### Module Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is proprietary software for Rand Refinery.

## Contact

Project Owner: IDBRSsimulator
Repository: [Mobility_for-rand_refinery](https://github.com/IDBRSsimulator/Mobility_for-rand_refinery)

## Acknowledgments

- Flask framework and community
- PostgreSQL database
- Render.com for hosting services
