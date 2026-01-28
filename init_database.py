"""
Database Initialization Script
Creates all tables and populates initial data including Super Admin
"""

from app import app, db
from models import (
    User, Role, Department, Team, QuestionPool, Question,
    SystemConfiguration, CustomEntityType, OrganizationHistory
)
from encryption import hash_password
import json


def init_system_roles():
    """Initialize default system roles"""
    roles_data = [
        {
            'name': 'super_admin',
            'display_name': 'Super Administrator',
            'description': 'Full system access with configuration capabilities',
            'level': 100,
            'is_system_role': True,
            'permissions': {
                'manage_users': True,
                'manage_roles': True,
                'manage_departments': True,
                'manage_teams': True,
                'view_all_data': True,
                'delete_data': True,
                'manage_system_config': True,
                'create_custom_entities': True,
                'view_audit_logs': True,
                'manage_question_pools': True,
                'create_surveys': True,
                'view_all_surveys': True,
                'manage_checklists': True,
                'view_all_locations': True,
                'send_notifications': True,
                'broadcast_messages': True,
            }
        },
        {
            'name': 'admin',
            'display_name': 'Administrator',
            'description': 'Department/organizational management',
            'level': 80,
            'is_system_role': True,
            'permissions': {
                'manage_users': True,
                'manage_departments': True,
                'manage_teams': True,
                'view_department_data': True,
                'manage_question_pools': True,
                'create_surveys': True,
                'view_department_surveys': True,
                'manage_checklists': True,
                'view_department_locations': True,
                'send_notifications': True,
            }
        },
        {
            'name': 'department_head',
            'display_name': 'Department Head',
            'description': 'Manage department operations and question pools',
            'level': 60,
            'is_system_role': True,
            'permissions': {
                'view_department_data': True,
                'manage_question_pools': True,
                'create_surveys': True,
                'view_department_surveys': True,
                'assign_checklists': True,
                'view_team_locations': True,
                'send_team_notifications': True,
            }
        },
        {
            'name': 'team_leader',
            'display_name': 'Team Leader',
            'description': 'Manage team members and assignments',
            'level': 40,
            'is_system_role': True,
            'permissions': {
                'view_team_data': True,
                'assign_checklists': True,
                'view_team_surveys': True,
                'view_team_locations': True,
                'send_team_notifications': True,
            }
        },
        {
            'name': 'operator',
            'display_name': 'Operator',
            'description': 'Field worker with survey and checklist access',
            'level': 20,
            'is_system_role': True,
            'permissions': {
                'submit_surveys': True,
                'complete_checklists': True,
                'view_own_data': True,
                'update_location': True,
                'send_messages': True,
            }
        },
        {
            'name': 'viewer',
            'display_name': 'Viewer',
            'description': 'Read-only access',
            'level': 10,
            'is_system_role': True,
            'permissions': {
                'view_own_data': True,
            }
        },
    ]
    
    created_roles = []
    for role_data in roles_data:
        existing_role = Role.query.filter_by(name=role_data['name']).first()
        if not existing_role:
            role = Role(**role_data)
            db.session.add(role)
            created_roles.append(role)
            print(f"✓ Created role: {role.display_name}")
        else:
            print(f"  Role already exists: {role_data['display_name']}")
    
    db.session.commit()
    return created_roles


def init_super_admin():
    """Create default Super Admin user"""
    super_admin_role = Role.query.filter_by(name='super_admin').first()
    
    if not super_admin_role:
        print("✗ Super Admin role not found. Please run init_system_roles() first.")
        return None
    
    # Check if super admin already exists
    existing_admin = User.query.filter_by(username='superadmin').first()
    if existing_admin:
        print("  Super Admin already exists")
        return existing_admin
    
    # Create super admin
    super_admin = User(
        username='superadmin',
        email='admin@mobility.app',
        password_hash=hash_password('Admin@123'),  # CHANGE THIS IN PRODUCTION!
        company_number='SA001',
        first_name='Super',
        last_name='Administrator',
        full_name='Super Administrator',
        role_id=super_admin_role.id,
        is_active=True,
        is_verified=True
    )
    
    db.session.add(super_admin)
    db.session.commit()
    
    print(f"✓ Created Super Admin user")
    print(f"  Username: superadmin")
    print(f"  Password: Admin@123 (CHANGE THIS IMMEDIATELY!)")
    
    return super_admin


def init_system_configuration():
    """Initialize default system configurations"""
    configs = [
        {
            'key': 'app_name',
            'value': 'Mobility Application',
            'description': 'Application display name',
            'category': 'general',
            'data_type': 'string',
            'is_sensitive': False
        },
        {
            'key': 'require_location_for_surveys',
            'value': True,
            'description': 'Require location data when submitting surveys',
            'category': 'surveys',
            'data_type': 'boolean',
            'is_sensitive': False
        },
        {
            'key': 'require_location_for_checklists',
            'value': True,
            'description': 'Require location data when submitting checklists',
            'category': 'checklists',
            'data_type': 'boolean',
            'is_sensitive': False
        },
        {
            'key': 'location_update_interval_seconds',
            'value': 300,
            'description': 'How often to update user locations (in seconds)',
            'category': 'location',
            'data_type': 'number',
            'is_sensitive': False
        },
        {
            'key': 'session_timeout_minutes',
            'value': 60,
            'description': 'User session timeout in minutes',
            'category': 'security',
            'data_type': 'number',
            'is_sensitive': False
        },
        {
            'key': 'max_file_upload_mb',
            'value': 10,
            'description': 'Maximum file upload size in MB',
            'category': 'general',
            'data_type': 'number',
            'is_sensitive': False
        },
        {
            'key': 'enable_notifications',
            'value': True,
            'description': 'Enable system notifications',
            'category': 'notifications',
            'data_type': 'boolean',
            'is_sensitive': False
        },
        {
            'key': 'enable_messaging',
            'value': True,
            'description': 'Enable private messaging between users',
            'category': 'messaging',
            'data_type': 'boolean',
            'is_sensitive': False
        },
        {
            'key': 'audit_retention_days',
            'value': 365,
            'description': 'Number of days to retain audit logs',
            'category': 'audit',
            'data_type': 'number',
            'is_sensitive': False
        },
    ]
    
    for config_data in configs:
        existing_config = SystemConfiguration.query.filter_by(key=config_data['key']).first()
        if not existing_config:
            config = SystemConfiguration(**config_data)
            db.session.add(config)
            print(f"✓ Created config: {config.key}")
        else:
            print(f"  Config already exists: {config_data['key']}")
    
    db.session.commit()


def init_sample_departments():
    """Create sample department structure"""
    # Root Department
    root_dept = Department.query.filter_by(name='Rand Refinery').first()
    if not root_dept:
        root_dept = Department(
            name='Rand Refinery',
            code='RR001',
            description='Root organization',
            level=0,
            is_active=True
        )
        db.session.add(root_dept)
        db.session.commit()
        print(f"✓ Created root department: {root_dept.name}")
    
    # Sample Sub-Departments
    sample_depts = [
        {'name': 'Operations', 'code': 'OPS001', 'parent': root_dept},
        {'name': 'Safety', 'code': 'SAF001', 'parent': root_dept},
        {'name': 'Maintenance', 'code': 'MNT001', 'parent': root_dept},
        {'name': 'Quality Control', 'code': 'QC001', 'parent': root_dept},
    ]
    
    for dept_data in sample_depts:
        existing = Department.query.filter_by(code=dept_data['code']).first()
        if not existing:
            dept = Department(
                name=dept_data['name'],
                code=dept_data['code'],
                parent_id=dept_data['parent'].id,
                level=1,
                is_active=True
            )
            db.session.add(dept)
            print(f"✓ Created department: {dept.name}")
    
    db.session.commit()


def init_sample_question_types():
    """Create sample custom entity types for questions"""
    entity_types = [
        {
            'name': 'safety_inspection',
            'display_name': 'Safety Inspection',
            'description': 'Safety-related inspection questions',
            'icon': 'shield',
            'color': '#FF5722',
            'field_definitions': [
                {'name': 'severity', 'type': 'select', 'options': ['Low', 'Medium', 'High', 'Critical']},
                {'name': 'requires_immediate_action', 'type': 'boolean'},
                {'name': 'responsible_department', 'type': 'text'},
            ]
        },
        {
            'name': 'equipment_check',
            'display_name': 'Equipment Check',
            'description': 'Equipment maintenance and status checks',
            'icon': 'build',
            'color': '#2196F3',
            'field_definitions': [
                {'name': 'equipment_id', 'type': 'text'},
                {'name': 'last_maintenance_date', 'type': 'date'},
                {'name': 'next_maintenance_due', 'type': 'date'},
            ]
        },
    ]
    
    for entity_data in entity_types:
        existing = CustomEntityType.query.filter_by(name=entity_data['name']).first()
        if not existing:
            entity_type = CustomEntityType(**entity_data)
            db.session.add(entity_type)
            print(f"✓ Created custom entity type: {entity_type.display_name}")
    
    db.session.commit()


def initialize_database(create_samples=True):
    """
    Main initialization function
    
    Args:
        create_samples: If True, creates sample data
    """
    print("\n" + "="*60)
    print("Mobility Application - Database Initialization")
    print("="*60 + "\n")
    
    try:
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ All tables created successfully\n")
        
        # Initialize system data
        print("Initializing system roles...")
        init_system_roles()
        print()
        
        print("Creating Super Admin...")
        init_super_admin()
        print()
        
        print("Initializing system configuration...")
        init_system_configuration()
        print()
        
        if create_samples:
            print("Creating sample departments...")
            init_sample_departments()
            print()
            
            print("Creating sample entity types...")
            init_sample_question_types()
            print()
        
        print("="*60)
        print("Database initialization completed successfully!")
        print("="*60)
        print("\nIMPORTANT: Please change the Super Admin password immediately!")
        print("Login at: http://localhost:5000/login")
        print("Username: superadmin")
        print("Password: Admin@123")
        print()
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        db.session.rollback()
        raise


if __name__ == '__main__':
    with app.app_context():
        initialize_database(create_samples=True)
