# Mobility Application - Quick Start Guide

## Initial Setup (5 Minutes)

### Step 1: Verify Database Connection

Your database is already configured:
```
Database: mobility_rand_v2
User: postgres
Host: localhost:5432
```

### Step 2: Initialize Database

```bash
# Activate virtual environment
.\myvenv\Scripts\Activate.ps1

# Initialize database with default data
python init_database.py
```

This creates:
- All database tables
- 6 system roles
- Super Admin account
- Default system configuration
- Sample departments

### Step 3: Login as Super Admin

**URL**: http://localhost:5000/login

**Credentials**:
- Username: `superadmin`
- Password: `Admin@123`

**⚠️ IMPORTANT**: Change this password immediately after first login!

### Step 4: Run Application

```bash
python app.py
```

## Super Admin First Steps

### 1. Change Default Password

Navigate to Profile Settings and update your password.

### 2. Create Departments

Example hierarchy:
```
Rand Refinery (Root)
├── Operations
│   ├── Production Team A
│   └── Production Team B
├── Safety
│   └── Safety Inspection Team
├── Maintenance
│   └── Equipment Team
└── Quality Control
    └── QC Team
```

### 3. Create Admin Users

Create department heads and administrators:

```python
# Example: Create Department Head
from models import db, User, Role, Department
from encryption import hash_password

# Get role and department
dept_head_role = Role.query.filter_by(name='department_head').first()
operations_dept = Department.query.filter_by(name='Operations').first()

# Create user
new_admin = User(
    username='ops_head',
    email='ops@mobility.app',
    password_hash=hash_password('SecurePass123!'),
    first_name='Operations',
    last_name='Head',
    full_name='Operations Head',
    role_id=dept_head_role.id,
    department_id=operations_dept.id,
    is_active=True,
    is_verified=True
)

db.session.add(new_admin)
db.session.commit()
```

### 4. Create Question Pools

Department heads can create question repositories:

```python
from models import db, QuestionPool, Question
from datetime import datetime

# Create a question pool
pool = QuestionPool(
    name='Safety Inspection Questions',
    description='Standard safety inspection questions',
    department_id=2,  # Safety department
    created_by_id=1,   # Super admin
    category='safety'
)
db.session.add(pool)
db.session.flush()

# Add questions to pool
questions = [
    {
        'question_text': 'Are all fire extinguishers accessible and inspected?',
        'question_type': 'yes_no',
        'is_required': True,
        'category': 'fire_safety'
    },
    {
        'question_text': 'PPE Status',
        'question_type': 'single_choice',
        'options': ['All Present', 'Partial', 'Missing', 'Damaged'],
        'is_required': True,
        'category': 'ppe'
    },
    {
        'question_text': 'Additional Notes',
        'question_type': 'text',
        'is_required': False
    }
]

for idx, q_data in enumerate(questions):
    question = Question(
        pool_id=pool.id,
        order_index=idx,
        **q_data
    )
    db.session.add(question)

db.session.commit()
```

### 5. Configure System Settings

```python
from admin_helpers import set_config

# Location tracking interval (seconds)
set_config('location_update_interval_seconds', 300, modified_by_id=1)

# Require location for surveys
set_config('require_location_for_surveys', True, modified_by_id=1)

# Session timeout (minutes)
set_config('session_timeout_minutes', 60, modified_by_id=1)

# Max file upload size (MB)
set_config('max_file_upload_mb', 10, modified_by_id=1)
```

## Common Admin Tasks

### Creating a Survey

```python
from models import db, Survey, SurveyQuestion, QuestionPool
from datetime import datetime, timedelta

# Get questions from pool
pool = QuestionPool.query.filter_by(name='Safety Inspection Questions').first()
questions = Question.query.filter_by(pool_id=pool.id, is_active=True).all()

# Create survey
survey = Survey(
    title='Weekly Safety Inspection',
    description='Weekly safety compliance check',
    created_by_id=1,
    department_id=2,  # Safety department
    start_date=datetime.utcnow(),
    end_date=datetime.utcnow() + timedelta(days=7),
    allow_multiple_submissions=False,
    require_location=True,
    status='active'
)
db.session.add(survey)
db.session.flush()

# Add questions to survey
for idx, question in enumerate(questions):
    sq = SurveyQuestion(
        survey_id=survey.id,
        question_id=question.id,
        order_index=idx
    )
    db.session.add(sq)

db.session.commit()
print(f"Survey created with {len(questions)} questions")
```

### Creating a Checklist

```python
from models import db, ChecklistTemplate, ChecklistItem

# Create template
template = ChecklistTemplate(
    name='Equipment Startup Checklist',
    description='Standard equipment startup procedure',
    department_id=3,  # Maintenance
    created_by_id=1,
    require_location=True,
    require_all_items=True
)
db.session.add(template)
db.session.flush()

# Add checklist items
items = [
    {
        'title': 'Visual inspection completed',
        'description': 'Check for visible damage or leaks',
        'is_required': True,
        'requires_evidence': True,
        'evidence_type': 'photo'
    },
    {
        'title': 'Safety guards in place',
        'is_required': True,
        'requires_evidence': False
    },
    {
        'title': 'Pre-start checks logged',
        'is_required': True,
        'requires_evidence': True,
        'evidence_type': 'signature'
    }
]

for idx, item_data in enumerate(items):
    item = ChecklistItem(
        template_id=template.id,
        order_index=idx,
        **item_data
    )
    db.session.add(item)

db.session.commit()
```

### Assigning Users to Hierarchy

```python
from models import db, User, Department, Team

# Create team
team = Team(
    name='Production Team A',
    code='PROD-A',
    department_id=1,  # Operations
    leader_id=5,  # Team leader user ID
    is_active=True
)
db.session.add(team)
db.session.commit()

# Assign operators to team
operator_ids = [10, 11, 12, 13, 14]
for user_id in operator_ids:
    user = User.query.get(user_id)
    if user:
        user.team_id = team.id
        user.department_id = team.department_id

db.session.commit()
```

### Viewing Survey Responses

```python
from models import Survey, SurveyResponse, SurveyAnswer
from sqlalchemy import func

# Get survey
survey = Survey.query.filter_by(title='Weekly Safety Inspection').first()

# Get all responses
responses = SurveyResponse.query.filter_by(survey_id=survey.id).all()

for response in responses:
    print(f"\n Response by: {response.user.full_name}")
    print(f"Department: {response.department_at_submission.name}")
    print(f"Location: {response.location.latitude}, {response.location.longitude}")
    print(f"Submitted: {response.submission_date}")
    
    # Get answers
    for answer in response.answers:
        question = answer.question
        print(f"Q: {question.question_text}")
        
        # Display answer based on type
        if question.question_type == 'yes_no':
            print(f"A: {answer.answer_text}")
        elif question.question_type == 'number':
            print(f"A: {answer.answer_number}")
        elif question.question_type == 'single_choice':
            print(f"A: {answer.answer_text}")
        else:
            print(f"A: {answer.answer_text}")
```

## Adding Custom Fields

### To Question Pools

```python
from admin_helpers import add_custom_field_to_question_pool

# Add a custom field to all questions in a pool
add_custom_field_to_question_pool(
    pool_id=1,
    field_name='risk_level',
    field_config={
        'type': 'select',
        'label': 'Risk Level',
        'options': ['Low', 'Medium', 'High', 'Critical'],
        'required': False
    }
)
```

### Creating Custom Entity Types

```python
from admin_helpers import create_custom_entity_type

# Create custom entity for equipment tracking
equipment_type = create_custom_entity_type(
    name='equipment_register',
    display_name='Equipment Register',
    description='Track equipment inventory and maintenance',
    field_definitions=[
        {
            'name': 'asset_number',
            'type': 'text',
            'label': 'Asset Number',
            'required': True
        },
        {
            'name': 'equipment_name',
            'type': 'text',
            'label': 'Equipment Name',
            'required': True
        },
        {
            'name': 'manufacturer',
            'type': 'text',
            'label': 'Manufacturer',
            'required': False
        },
        {
            'name': 'install_date',
            'type': 'date',
            'label': 'Installation Date',
            'required': False
        },
        {
            'name': 'maintenance_schedule',
            'type': 'select',
            'label': 'Maintenance Schedule',
            'options': ['Weekly', 'Monthly', 'Quarterly', 'Annually'],
            'required': True
        },
        {
            'name': 'status',
            'type': 'select',
            'label': 'Status',
            'options': ['Operational', 'Under Maintenance', 'Out of Service', 'Decommissioned'],
            'required': True
        }
    ],
    icon='settings',
    color='#FF9800'
)
```

## Monitoring & Reports

### Get System Statistics

```python
from admin_helpers import get_hierarchy_stats, get_activity_summary

# Organizational statistics
stats = get_hierarchy_stats()
print("="*50)
print("SYSTEM STATISTICS")
print("="*50)
print(f"Total Users: {stats['total_users']}")
print(f"Active Users: {stats['active_users']}")
print(f"Total Departments: {stats['total_departments']}")
print(f"Active Departments: {stats['active_departments']}")
print("\nUsers by Role:")
for role, count in stats['users_by_role'].items():
    print(f"  {role}: {count}")

# Recent activity (last 30 days)
activity = get_activity_summary(days=30)
print("\n" + "="*50)
print("ACTIVITY SUMMARY (Last 30 Days)")
print("="*50)
print(f"Survey Responses: {activity['survey_responses']}")
print(f"Checklist Submissions: {activity['checklist_submissions']}")
print(f"Messages Sent: {activity['messages_sent']}")
print(f"Location Updates: {activity['location_updates']}")
```

### View Audit History

```python
from models import OrganizationHistory, User
from datetime import datetime, timedelta

# Get recent organizational changes
recent_changes = OrganizationHistory.query.filter(
    OrganizationHistory.created_at >= datetime.utcnow() - timedelta(days=7)
).order_by(OrganizationHistory.created_at.desc()).limit(50).all()

print("RECENT ORGANIZATIONAL CHANGES")
print("="*70)
for change in recent_changes:
    user = User.query.get(change.changed_by_id)
    print(f"\n{change.created_at} | {change.action.upper()}")
    print(f"Entity: {change.entity_type} (ID: {change.entity_id})")
    print(f"Changed by: {user.full_name if user else 'Unknown'}")
    if change.changes:
        print(f"Fields changed: {', '.join(change.changes.keys())}")
```

## Backup & Restore

### Database Backup

```bash
# Full backup
pg_dump -U postgres -h localhost -d mobility_rand_v2 -F c -f backup_$(date +%Y%m%d).dump

# Schema only
pg_dump -U postgres -h localhost -d mobility_rand_v2 --schema-only -f schema_backup.sql

# Data only
pg_dump -U postgres -h localhost -d mobility_rand_v2 --data-only -f data_backup.sql
```

### Restore Database

```bash
# Restore from custom format
pg_restore -U postgres -h localhost -d mobility_rand_v2 -c backup_20260128.dump

# Restore from SQL
psql -U postgres -h localhost -d mobility_rand_v2 -f backup.sql
```

## Troubleshooting

### Reset Database

```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS mobility_rand_v2;"
psql -U postgres -c "CREATE DATABASE mobility_rand_v2;"

# Reinitialize
python init_database.py
```

### Check Database Connection

```python
from dbqueries import get_db_connection

conn = get_db_connection()
if conn:
    print("✓ Database connection successful!")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(f"PostgreSQL version: {cur.fetchone()[0]}")
    conn.close()
else:
    print("✗ Database connection failed!")
```

### Verify Tables Created

```python
from models import db
from app import app

with app.app_context():
    # Get all table names
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"Total tables created: {len(tables)}")
    print("\nTables:")
    for table in sorted(tables):
        print(f"  - {table}")
```

## Next Steps

1. **Customize Roles**: Add specific permissions for your organization
2. **Create Departments**: Set up your organizational hierarchy
3. **Add Users**: Create accounts for all personnel
4. **Build Question Pools**: Department heads create question repositories
5. **Configure Workflows**: Set up surveys and checklists
6. **Test Mobile Access**: Ensure location tracking works
7. **Train Users**: Provide training on survey and checklist completion
8. **Monitor Activity**: Review audit logs and activity reports

## Support

For technical support or questions:
- Review [DATABASE_ARCHITECTURE.md](DATABASE_ARCHITECTURE.md) for detailed schema information
- Check [models.py](models.py) for model definitions
- Use [admin_helpers.py](admin_helpers.py) for administrative functions

---

**Ready to start!** 🚀

Your database is configured and ready for initialization. Run `python init_database.py` to begin.
