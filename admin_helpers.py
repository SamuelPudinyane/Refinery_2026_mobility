"""
Helper Functions for Super Admin Configuration
Allows dynamic management of fields, entities, and system configuration
"""

from models import (
    db, CustomEntityType, CustomEntity, SystemConfiguration,
    QuestionPool, Question, Role, User, Department
)
from datetime import datetime
import json


# ============================================================================
# CUSTOM ENTITY MANAGEMENT
# ============================================================================

def create_custom_entity_type(name, display_name, description, field_definitions, icon=None, color=None, created_by_id=None):
    """
    Create a new custom entity type
    
    Args:
        name: Internal name (snake_case)
        display_name: User-facing name
        description: Description of the entity type
        field_definitions: List of field definitions
            Example: [
                {'name': 'field1', 'type': 'text', 'required': True, 'label': 'Field 1'},
                {'name': 'field2', 'type': 'number', 'required': False, 'label': 'Field 2'},
            ]
        icon: Icon identifier (optional)
        color: Color code (optional)
    
    Returns:
        CustomEntityType object or None if error
    """
    try:
        entity_type = CustomEntityType(
            name=name,
            display_name=display_name,
            description=description,
            field_definitions=field_definitions,
            icon=icon,
            color=color,
            is_active=True
        )
        
        db.session.add(entity_type)
        db.session.commit()
        
        print(f"✓ Created custom entity type: {display_name}")
        return entity_type
        
    except Exception as e:
        print(f"✗ Error creating entity type: {e}")
        db.session.rollback()
        return None


def add_field_to_entity_type(entity_type_id, field_definition):
    """
    Add a new field to an existing entity type
    
    Args:
        entity_type_id: ID of the entity type
        field_definition: Field definition dict
            Example: {'name': 'new_field', 'type': 'text', 'required': False}
    
    Returns:
        Updated CustomEntityType or None
    """
    try:
        entity_type = CustomEntityType.query.get(entity_type_id)
        if not entity_type:
            print(f"✗ Entity type {entity_type_id} not found")
            return None
        
        # Add new field to definitions
        current_fields = entity_type.field_definitions or []
        
        # Check if field already exists
        if any(f['name'] == field_definition['name'] for f in current_fields):
            print(f"✗ Field '{field_definition['name']}' already exists")
            return None
        
        current_fields.append(field_definition)
        entity_type.field_definitions = current_fields
        entity_type.updated_at = datetime.utcnow()
        
        db.session.commit()
        print(f"✓ Added field '{field_definition['name']}' to {entity_type.display_name}")
        
        return entity_type
        
    except Exception as e:
        print(f"✗ Error adding field: {e}")
        db.session.rollback()
        return None


def remove_field_from_entity_type(entity_type_id, field_name):
    """Remove a field from an entity type"""
    try:
        entity_type = CustomEntityType.query.get(entity_type_id)
        if not entity_type:
            return None
        
        current_fields = entity_type.field_definitions or []
        updated_fields = [f for f in current_fields if f['name'] != field_name]
        
        if len(updated_fields) == len(current_fields):
            print(f"✗ Field '{field_name}' not found")
            return None
        
        entity_type.field_definitions = updated_fields
        entity_type.updated_at = datetime.utcnow()
        
        db.session.commit()
        print(f"✓ Removed field '{field_name}' from {entity_type.display_name}")
        
        return entity_type
        
    except Exception as e:
        print(f"✗ Error removing field: {e}")
        db.session.rollback()
        return None


def create_custom_entity(entity_type_id, data, created_by_id):
    """
    Create an instance of a custom entity
    
    Args:
        entity_type_id: ID of the entity type
        data: Dictionary of field values
        created_by_id: User ID creating the entity
    
    Returns:
        CustomEntity object or None
    """
    try:
        entity_type = CustomEntityType.query.get(entity_type_id)
        if not entity_type:
            print(f"✗ Entity type {entity_type_id} not found")
            return None
        
        # Validate data against field definitions
        field_defs = {f['name']: f for f in entity_type.field_definitions}
        
        for field_name, field_def in field_defs.items():
            if field_def.get('required', False) and field_name not in data:
                print(f"✗ Required field '{field_name}' missing")
                return None
        
        # Create entity
        entity = CustomEntity(
            entity_type_id=entity_type_id,
            created_by_id=created_by_id,
            data=data
        )
        
        db.session.add(entity)
        db.session.commit()
        
        print(f"✓ Created {entity_type.display_name} entity")
        return entity
        
    except Exception as e:
        print(f"✗ Error creating entity: {e}")
        db.session.rollback()
        return None


# ============================================================================
# SYSTEM CONFIGURATION MANAGEMENT
# ============================================================================

def get_config(key, default=None):
    """Get a system configuration value"""
    config = SystemConfiguration.query.filter_by(key=key).first()
    if config:
        return config.value
    return default


def set_config(key, value, modified_by_id=None, description=None, category='general', data_type='string'):
    """
    Set a system configuration value
    
    Args:
        key: Configuration key
        value: Configuration value
        modified_by_id: User ID making the change
        description: Description of the config (for new configs)
        category: Category of the config
        data_type: Data type ('string', 'number', 'boolean', 'json')
    
    Returns:
        SystemConfiguration object or None
    """
    try:
        config = SystemConfiguration.query.filter_by(key=key).first()
        
        if config:
            # Update existing
            config.value = value
            config.modified_by_id = modified_by_id
            config.updated_at = datetime.utcnow()
        else:
            # Create new
            config = SystemConfiguration(
                key=key,
                value=value,
                description=description,
                category=category,
                data_type=data_type,
                modified_by_id=modified_by_id
            )
            db.session.add(config)
        
        db.session.commit()
        print(f"✓ Set config: {key} = {value}")
        
        return config
        
    except Exception as e:
        print(f"✗ Error setting config: {e}")
        db.session.rollback()
        return None


def get_all_configs(category=None):
    """Get all system configurations, optionally filtered by category"""
    query = SystemConfiguration.query
    
    if category:
        query = query.filter_by(category=category)
    
    configs = query.order_by(SystemConfiguration.category, SystemConfiguration.key).all()
    
    return {
        config.key: {
            'value': config.value,
            'description': config.description,
            'category': config.category,
            'data_type': config.data_type
        }
        for config in configs
    }


# ============================================================================
# DYNAMIC QUESTION FIELD MANAGEMENT
# ============================================================================

def add_custom_field_to_question_pool(pool_id, field_name, field_config):
    """
    Add a custom field to all questions in a pool
    
    Args:
        pool_id: Question pool ID
        field_name: Name of the custom field
        field_config: Configuration for the field
            Example: {'type': 'text', 'label': 'Custom Field', 'required': False}
    
    Returns:
        Number of questions updated
    """
    try:
        pool = QuestionPool.query.get(pool_id)
        if not pool:
            print(f"✗ Question pool {pool_id} not found")
            return 0
        
        # Update pool's custom fields
        current_fields = pool.custom_fields or {}
        current_fields[field_name] = field_config
        pool.custom_fields = current_fields
        
        # Update all questions in pool
        questions = Question.query.filter_by(pool_id=pool_id).all()
        for question in questions:
            q_fields = question.custom_fields or {}
            if field_name not in q_fields:
                q_fields[field_name] = None  # Initialize with null value
                question.custom_fields = q_fields
        
        db.session.commit()
        print(f"✓ Added custom field '{field_name}' to {len(questions)} questions")
        
        return len(questions)
        
    except Exception as e:
        print(f"✗ Error adding custom field: {e}")
        db.session.rollback()
        return 0


# ============================================================================
# ROLE & PERMISSION MANAGEMENT
# ============================================================================

def update_role_permissions(role_id, permissions, modified_by_id=None):
    """
    Update permissions for a role
    
    Args:
        role_id: Role ID
        permissions: Dictionary of permissions
        modified_by_id: User ID making the change
    
    Returns:
        Updated Role or None
    """
    try:
        role = Role.query.get(role_id)
        if not role:
            print(f"✗ Role {role_id} not found")
            return None
        
        role.permissions = permissions
        role.updated_at = datetime.utcnow()
        
        db.session.commit()
        print(f"✓ Updated permissions for role: {role.display_name}")
        
        return role
        
    except Exception as e:
        print(f"✗ Error updating permissions: {e}")
        db.session.rollback()
        return None


def add_permission_to_role(role_id, permission_key, value=True):
    """Add a single permission to a role"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return None
        
        permissions = role.permissions or {}
        permissions[permission_key] = value
        role.permissions = permissions
        role.updated_at = datetime.utcnow()
        
        db.session.commit()
        print(f"✓ Added permission '{permission_key}' to {role.display_name}")
        
        return role
        
    except Exception as e:
        print(f"✗ Error adding permission: {e}")
        db.session.rollback()
        return None


# ============================================================================
# REPORTING & ANALYTICS HELPERS
# ============================================================================

def get_hierarchy_stats():
    """Get statistics about organizational hierarchy"""
    stats = {
        'total_users': User.query.filter_by(is_deleted=False).count(),
        'active_users': User.query.filter_by(is_deleted=False, is_active=True).count(),
        'total_departments': Department.query.filter_by(is_deleted=False).count(),
        'active_departments': Department.query.filter_by(is_deleted=False, is_active=True).count(),
        'users_by_role': {}
    }
    
    # Users by role
    roles = Role.query.all()
    for role in roles:
        count = User.query.filter_by(role_id=role.id, is_deleted=False).count()
        stats['users_by_role'][role.display_name] = count
    
    return stats


def get_activity_summary(days=30):
    """Get activity summary for recent days"""
    from datetime import timedelta
    from sqlalchemy import func
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    summary = {
        'survey_responses': db.session.query(func.count()).select_from(SurveyResponse).filter(
            SurveyResponse.created_at >= since_date
        ).scalar(),
        'checklist_submissions': db.session.query(func.count()).select_from(ChecklistSubmission).filter(
            ChecklistSubmission.created_at >= since_date
        ).scalar(),
        'messages_sent': db.session.query(func.count()).select_from(Message).filter(
            Message.created_at >= since_date,
            Message.is_deleted == False
        ).scalar(),
        'location_updates': db.session.query(func.count()).select_from(UserLocation).filter(
            UserLocation.created_at >= since_date
        ).scalar(),
    }
    
    return summary


# ============================================================================
# BULK OPERATIONS
# ============================================================================

def bulk_assign_users_to_department(user_ids, department_id, modified_by_id=None):
    """Bulk assign users to a department"""
    try:
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        for user in users:
            user.department_id = department_id
            user.updated_at = datetime.utcnow()
        
        db.session.commit()
        print(f"✓ Assigned {len(users)} users to department {department_id}")
        
        return len(users)
        
    except Exception as e:
        print(f"✗ Error in bulk assignment: {e}")
        db.session.rollback()
        return 0


def export_entity_to_json(entity_type, entity_id):
    """Export an entity and its related data to JSON"""
    model_map = {
        'user': User,
        'department': Department,
        'question_pool': QuestionPool,
        'survey': Survey,
    }
    
    if entity_type not in model_map:
        return None
    
    model = model_map[entity_type]
    entity = model.query.get(entity_id)
    
    if not entity:
        return None
    
    # This would need to be expanded based on requirements
    return {
        'entity_type': entity_type,
        'entity_id': entity_id,
        'exported_at': datetime.utcnow().isoformat(),
        'data': {}  # Serialize entity data here
    }
