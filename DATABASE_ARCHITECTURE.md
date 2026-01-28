# Mobility Application - Dynamic Database System

## Overview

This mobility application features a comprehensive, dynamic database system built with PostgreSQL and SQLAlchemy ORM. The system supports hierarchical organizational structures, flexible data models, real-time location tracking, surveys, checklists, messaging, and full audit capabilities.

## Key Features

### 1. **Hierarchical Organization Management**
- Multi-level organizational structure (Departments → Teams → Users)
- Flexible parent-child relationships with adjacency list pattern
- Department heads and team leaders with specific permissions
- Complete organizational history tracking

### 2. **Dynamic Field System**
- JSONB-based custom fields on core entities
- Super Admin can add fields without schema migration
- Custom entity types configurable through admin interface
- Field definitions stored as structured JSON

### 3. **Role-Based Access Control (RBAC)**
- Hierarchical role system with permission inheritance
- Flexible permissions stored as JSON
- System roles: Super Admin, Admin, Department Head, Team Leader, Operator, Viewer
- Custom roles can be created by Super Admin

### 4. **Survey & Question Pool System**
- Department heads maintain question repositories
- Reusable questions across multiple surveys
- Support for 12+ question types (text, number, choice, rating, file, location, etc.)
- Survey responses linked to hierarchy at submission time
- Location data captured with each submission

### 5. **Checklist Workflow**
- Template-based checklists
- Assignment to users or teams
- Evidence collection (photos, signatures, notes)
- Status tracking (pending, in_progress, completed, overdue)
- Location-stamped completions

### 6. **Real-Time Location Tracking**
- Automatic location updates
- Location zones and geofencing
- Historical location data
- Location context for activities

### 7. **Communication System**
- System-wide notification center
- Private messaging between users
- Message threading
- Priority levels and read receipts

### 8. **Complete Audit Trail**
- All changes tracked in OrganizationHistory
- Comprehensive audit logs
- Old and new state preservation
- IP address and user agent tracking
- Historical data never deleted (soft delete)

## Database Schema

### Core Tables

#### Users & Authentication
- `users` - User accounts with hierarchical relationships
- `roles` - Role definitions with permissions
- `user_locations` - Real-time and historical location data

#### Organization
- `departments` - Hierarchical department structure
- `teams` - Teams within departments
- `organization_history` - Complete change history

#### Surveys & Questions
- `question_pools` - Question repositories by department
- `questions` - Individual questions with validation rules
- `surveys` - Survey assignments
- `survey_questions` - Link table for survey-question relationships
- `survey_responses` - User responses with organizational context
- `survey_answers` - Individual question answers

#### Checklists
- `checklist_templates` - Reusable checklist templates
- `checklist_items` - Items in templates
- `checklist_assignments` - Assignments to users/teams
- `checklist_submissions` - Completed checklists
- `checklist_item_responses` - Responses to individual items

#### Communication
- `notifications` - System notifications
- `messages` - Private messages between users

#### Location
- `user_locations` - Location tracking
- `location_zones` - Defined zones/areas

#### Configuration
- `custom_entity_types` - Dynamic entity type definitions
- `custom_entities` - Instances of custom entities
- `system_configuration` - System-wide settings

#### Audit
- `audit_logs` - Comprehensive audit trail
- `organization_history` - Organizational change tracking

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database Connection

Update `.env` file with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql://postgres:malvapudding78*@localhost:5432/mobility_rand_v2
SECRET_KEY=your-secret-key-here
```

### 3. Initialize Database

Run the initialization script to create tables and default data:

```bash
python init_database.py
```

This will:
- Create all database tables
- Initialize system roles
- Create Super Admin user
- Set up default configurations
- Create sample departments (optional)

**Default Super Admin Credentials:**
- Username: `superadmin`
- Password: `Admin@123`
- **⚠️ CHANGE THIS IMMEDIATELY IN PRODUCTION!**

### 4. Run Database Migrations (Optional)

For schema changes, use Flask-Migrate:

```bash
# Initialize migrations (first time only)
flask db init

# Create a migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## Super Admin Configuration Guide

### Adding Custom Fields to Entities

```python
from admin_helpers import add_field_to_entity_type

# Add a custom field to a question pool
add_field_to_entity_type(
    entity_type_id=1,
    field_definition={
        'name': 'priority_level',
        'type': 'select',
        'label': 'Priority Level',
        'required': False,
        'options': ['Low', 'Medium', 'High', 'Critical']
    }
)
```

### Creating Custom Entity Types

```python
from admin_helpers import create_custom_entity_type

# Create a new entity type
create_custom_entity_type(
    name='equipment_inspection',
    display_name='Equipment Inspection',
    description='Custom inspection forms for equipment',
    field_definitions=[
        {
            'name': 'equipment_id',
            'type': 'text',
            'label': 'Equipment ID',
            'required': True
        },
        {
            'name': 'inspection_date',
            'type': 'date',
            'label': 'Inspection Date',
            'required': True
        },
        {
            'name': 'condition',
            'type': 'select',
            'label': 'Condition',
            'options': ['Excellent', 'Good', 'Fair', 'Poor'],
            'required': True
        }
    ],
    icon='build',
    color='#2196F3'
)
```

### Managing System Configuration

```python
from admin_helpers import get_config, set_config

# Get a configuration value
location_required = get_config('require_location_for_surveys', default=True)

# Set a configuration value
set_config(
    key='max_file_upload_mb',
    value=20,
    modified_by_id=1,  # Super Admin user ID
    description='Maximum file upload size in megabytes',
    category='general',
    data_type='number'
)
```

### Managing Roles and Permissions

```python
from admin_helpers import add_permission_to_role, update_role_permissions

# Add a single permission
add_permission_to_role(
    role_id=2,
    permission_key='export_reports',
    value=True
)

# Update all permissions for a role
update_role_permissions(
    role_id=3,
    permissions={
        'view_department_data': True,
        'create_surveys': True,
        'assign_checklists': True,
        'view_team_locations': True
    }
)
```

## Question Types Supported

1. **text** - Single line text input
2. **textarea** - Multi-line text input
3. **number** - Numeric input
4. **date** - Date picker
5. **time** - Time picker
6. **datetime** - Date and time picker
7. **single_choice** - Radio buttons
8. **multiple_choice** - Checkboxes
9. **dropdown** - Dropdown select
10. **rating** - Star rating or numeric scale
11. **yes_no** - Boolean choice
12. **file_upload** - File attachment
13. **signature** - Digital signature capture
14. **location** - GPS coordinates

## Data Flow Examples

### Survey Submission Flow

1. Admin creates survey from question pool
2. Survey assigned to department/team
3. User opens survey on mobile device
4. User's current location captured
5. User answers questions
6. Submission stored with:
   - User ID and hierarchy position at submission time
   - Department and team IDs at submission
   - Location data
   - Timestamp
   - Individual answers to each question

### Organizational Change Flow

1. Admin modifies user's department
2. System automatically:
   - Records change in `organization_history`
   - Preserves old state in JSONB
   - Logs change in `audit_logs`
   - Updates user's `updated_at` timestamp
3. Historical surveys/checklists remain linked to old hierarchy

## Performance Optimization

### Indexes

The schema includes strategic indexes on:
- User lookups (`username`, `email`, `company_number`)
- Hierarchical queries (`parent_id`, `department_id`, `team_id`)
- Time-based queries (`created_at`, `submission_date`)
- Location queries (`latitude`, `longitude`)
- Relationship lookups (foreign keys)

### JSONB Benefits

Using PostgreSQL's JSONB type for custom fields provides:
- Fast querying with GIN indexes
- No schema migrations for new fields
- Flexible data structures
- JSON operators for queries

### Query Optimization Tips

```python
# Use joined loading for relationships
user = User.query.options(
    db.joinedload(User.role),
    db.joinedload(User.department)
).get(user_id)

# Filter soft-deleted records
active_users = User.query.filter_by(is_deleted=False, is_active=True).all()

# Use pagination for large result sets
page = SurveyResponse.query.paginate(page=1, per_page=50)
```

## Security Considerations

### Password Security
- All passwords hashed using bcrypt
- No plain text passwords stored
- Configurable password complexity rules

### Data Protection
- Soft delete preserves audit trail
- Role-based access control
- IP address logging
- Session management

### JSONB Validation
- Validate custom field data before saving
- Sanitize user input
- Use parameterized queries

## Migration from Old System

### Steps to Migrate Existing Data

1. **Export existing data** from old tables
2. **Map data** to new schema
3. **Import users** with role assignments
4. **Create departments** and hierarchy
5. **Import questions** into question pools
6. **Migrate historical** survey responses
7. **Preserve timestamps** and relationships

### Migration Script Template

```python
from models import db, User, Department, Role, QuestionPool
from encryption import hash_password

def migrate_users():
    # Import from old rand_refinary_registration table
    old_users = execute_old_query("SELECT * FROM rand_refinary_registration")
    
    for old_user in old_users:
        new_user = User(
            username=old_user['name'],
            company_number=old_user['company_number'],
            password_hash=old_user['password'],  # Already hashed
            role_id=map_old_role_to_new(old_user['role']),
            is_active=True,
            created_at=old_user.get('created_at', datetime.utcnow())
        )
        db.session.add(new_user)
    
    db.session.commit()
```

## API Integration Examples

### Create Survey via API

```python
from models import db, Survey, SurveyQuestion, QuestionPool
from datetime import datetime, timedelta

def create_survey_api(title, department_id, question_ids, created_by_id):
    survey = Survey(
        title=title,
        department_id=department_id,
        created_by_id=created_by_id,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        status='active'
    )
    db.session.add(survey)
    db.session.flush()  # Get survey ID
    
    # Add questions
    for idx, question_id in enumerate(question_ids):
        sq = SurveyQuestion(
            survey_id=survey.id,
            question_id=question_id,
            order_index=idx
        )
        db.session.add(sq)
    
    db.session.commit()
    return survey
```

### Track User Location

```python
from models import db, UserLocation

def update_user_location(user_id, latitude, longitude, location_type='automatic'):
    # Mark previous location as not current
    UserLocation.query.filter_by(user_id=user_id).update({'is_current': False})
    
    # Create new location record
    location = UserLocation(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        location_type=location_type,
        is_current=True
    )
    db.session.add(location)
    db.session.commit()
    
    return location
```

## Maintenance & Monitoring

### Regular Tasks

1. **Backup database** regularly
2. **Monitor disk space** (JSONB and location data can grow)
3. **Archive old audit logs** (based on retention policy)
4. **Review user access** and permissions
5. **Check location tracking** accuracy

### Performance Monitoring

```python
from admin_helpers import get_hierarchy_stats, get_activity_summary

# Get system statistics
stats = get_hierarchy_stats()
print(f"Total users: {stats['total_users']}")
print(f"Active users: {stats['active_users']}")

# Get recent activity
activity = get_activity_summary(days=30)
print(f"Survey responses: {activity['survey_responses']}")
print(f"Location updates: {activity['location_updates']}")
```

## Troubleshooting

### Common Issues

**Issue: Migration fails with "column already exists"**
```bash
# Reset migrations
flask db downgrade base
flask db upgrade
```

**Issue: JSONB queries not working**
```python
# Ensure PostgreSQL version supports JSONB (9.4+)
# Use proper JSONB operators
results = Model.query.filter(Model.custom_fields['key'].astext == 'value').all()
```

**Issue: Soft delete not working**
```python
# Always filter by is_deleted
active_records = Model.query.filter_by(is_deleted=False).all()
```

## Support & Documentation

- **Database Schema**: See [models.py](models.py)
- **Admin Helpers**: See [admin_helpers.py](admin_helpers.py)
- **Initialization**: See [init_database.py](init_database.py)
- **Configuration**: See [config.py](config.py)

## License

This application is proprietary software for Rand Refinery operations.

---

**Last Updated**: January 28, 2026
**Version**: 2.0
**Database**: PostgreSQL 12+
