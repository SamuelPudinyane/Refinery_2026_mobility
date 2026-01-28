"""
Dynamic Database Models for Mobility Application
Supports hierarchical organizations, dynamic fields, surveys, checklists, messaging, and geolocation tracking
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy import event, Index
import uuid

db = SQLAlchemy()


# ============================================================================
# MIXIN CLASSES - Reusable Components
# ============================================================================

class TimestampMixin:
    """Adds created_at and updated_at timestamp fields"""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class SoftDeleteMixin:
    """Adds soft delete capability with is_deleted and deleted_at fields"""
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


class DynamicFieldsMixin:
    """Adds support for custom fields using JSONB (PostgreSQL)"""
    custom_fields = db.Column(JSONB, nullable=True, default={})


# ============================================================================
# CORE USER & AUTHENTICATION MODELS
# ============================================================================

class User(db.Model, TimestampMixin, SoftDeleteMixin, DynamicFieldsMixin):
    """
    Core user model supporting hierarchical relationships
    Supports multiple roles and flexible authentication
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())

    # Authentication
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    company_number = db.Column(db.String(50), unique=True, nullable=True, index=True)

    # Profile Information
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    full_name = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)

    # Role & Status
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)

    # Hierarchical Structure (Adjacency List Pattern)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)

    # Last Activity Tracking
    last_login = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)

    # Relationships
    role = db.relationship('Role', backref='users', lazy='joined', foreign_keys=[role_id])
    parent = db.relationship('User', remote_side=[id], foreign_keys=[parent_id], backref='subordinates')
    department = db.relationship('Department', backref='members', foreign_keys=[department_id])
    team = db.relationship('Team', backref='members', foreign_keys=[team_id])

    # Reverse Relationships
    locations = db.relationship('UserLocation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    survey_responses = db.relationship('SurveyResponse', backref='user', lazy='dynamic')
    checklist_submissions = db.relationship('ChecklistSubmission', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username} - {self.role.name if self.role else "No Role"}>'

    def get_full_hierarchy(self):
        """Returns list of all users in hierarchy (self and all subordinates)"""
        result = [self]
        for subordinate in self.subordinates:
            result.extend(subordinate.get_full_hierarchy())
        return result

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'username': self.username,
            'email': self.email,
            'company_number': self.company_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'profile_picture': self.profile_picture,
            'role': self.role.to_dict() if self.role else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'department': self.department.name if self.department else None,
            'team': self.team_id,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
        }
    """
    Core user model supporting hierarchical relationships
    Supports multiple roles and flexible authentication
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    # Authentication
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    company_number = db.Column(db.String(50), unique=True, nullable=True, index=True)
    
    # Profile Information
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    full_name = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)
    
    # Role & Status
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    
    # Hierarchical Structure (Adjacency List Pattern)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    
    # Last Activity Tracking
    last_login = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    role = db.relationship('Role', backref='users', lazy='joined', foreign_keys=[role_id])
    parent = db.relationship('User', remote_side=[id], foreign_keys=[parent_id], backref='subordinates')
    department = db.relationship('Department', backref='members', foreign_keys=[department_id])
    team = db.relationship('Team', backref='members', foreign_keys=[team_id])
    
    # Reverse Relationships
    locations = db.relationship('UserLocation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    notifications = db.relationship('Notification', foreign_keys='Notification.user_id', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    survey_responses = db.relationship('SurveyResponse', backref='user', lazy='dynamic')
    checklist_submissions = db.relationship('ChecklistSubmission', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username} - {self.role.name if self.role else "No Role"}>'
    
    def get_full_hierarchy(self):
        """Returns list of all users in hierarchy (self and all subordinates)"""
        result = [self]
        for subordinate in self.subordinates:
            result.extend(subordinate.get_full_hierarchy())
        return result
    
    def get_hierarchy_path(self):
        """Returns path from root to current user"""
        path = [self]
        current = self.parent
        while current:
            path.insert(0, current)
            current = current.parent
        return path



class Role(db.Model, TimestampMixin, SoftDeleteMixin, DynamicFieldsMixin):
    """
    Flexible role-based access control
    Supports custom permissions and hierarchical roles
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Permission System (stored as JSONB for flexibility)
    permissions = db.Column(JSONB, nullable=False, default={})

    # Hierarchy
    parent_role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)

    # Status
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_system_role = db.Column(db.Boolean, nullable=False, default=False)  # Cannot be deleted

    # Relationships
    parent_role = db.relationship('Role', remote_side=[id], backref='child_roles')

    def __repr__(self):
        return f'<Role {self.name}>'

    def has_permission(self, permission_key):
        """Check if role has specific permission"""
        return self.permissions.get(permission_key, False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'permissions': self.permissions,
            'parent_role_id': self.parent_role_id,
            'is_active': self.is_active,
            'is_system_role': self.is_system_role,
        }


# ============================================================================
# ORGANIZATIONAL STRUCTURE MODELS
# ============================================================================

class Department(db.Model, TimestampMixin, SoftDeleteMixin, DynamicFieldsMixin):
    """
    Department/Division structure with hierarchical support
    """
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    name = db.Column(db.String(200), nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Hierarchical Structure
    parent_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True, index=True)
    
    # Department Head
    head_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    parent = db.relationship('Department', remote_side=[id], backref='sub_departments')
    head = db.relationship('User', foreign_keys=[head_user_id], backref='headed_departments')
    teams = db.relationship('Team', backref='department', lazy='dynamic')
    
    def __repr__(self):
        return f'<Department {self.name}>'


class Team(db.Model, TimestampMixin, SoftDeleteMixin, DynamicFieldsMixin):
    """
    Teams within departments
    """
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    name = db.Column(db.String(200), nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    leader = db.relationship('User', foreign_keys=[leader_id], backref='led_teams')
    
    def __repr__(self):
        return f'<Team {self.name}>'


# ============================================================================
# HISTORICAL TRACKING MODELS
# ============================================================================

class OrganizationHistory(db.Model, TimestampMixin):
    """
    Tracks all changes to organizational structure
    Maintains complete audit trail
    """
    __tablename__ = 'organization_history'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # What changed
    entity_type = db.Column(db.String(50), nullable=False)  # 'user', 'department', 'team', 'role'
    entity_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'create', 'update', 'delete', 'move'
    
    # Previous and new state (stored as JSONB)
    previous_state = db.Column(JSONB, nullable=True)
    new_state = db.Column(JSONB, nullable=True)
    changes = db.Column(JSONB, nullable=True)  # Specific fields that changed
    
    # Who made the change
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_by = db.relationship('User', foreign_keys=[changed_by_id])
    
    # Additional context
    reason = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    
    __table_args__ = (
        Index('idx_org_history_entity', 'entity_type', 'entity_id'),
        Index('idx_org_history_timestamp', 'created_at'),
    )
    
    def __repr__(self):
        return f'<OrgHistory {self.entity_type}:{self.entity_id} - {self.action}>'


# ============================================================================
# GEOLOCATION TRACKING MODELS
# ============================================================================

class UserLocation(db.Model, TimestampMixin, DynamicFieldsMixin):
    """
    Real-time and historical location tracking for users
    """
    __tablename__ = 'user_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Geographic Coordinates
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    altitude = db.Column(db.Numeric(10, 2), nullable=True)
    accuracy = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Location Details
    address = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    
    # Context
    location_type = db.Column(db.String(50), nullable=True)  # 'checkin', 'checkout', 'survey', 'manual', 'automatic'
    is_current = db.Column(db.Boolean, nullable=False, default=True)
    
    # Related Activity
    related_entity_type = db.Column(db.String(50), nullable=True)  # 'survey', 'checklist', 'message'
    related_entity_id = db.Column(db.Integer, nullable=True)
    
    __table_args__ = (
        Index('idx_user_location_current', 'user_id', 'is_current'),
        Index('idx_user_location_coords', 'latitude', 'longitude'),
        Index('idx_user_location_timestamp', 'created_at'),
    )
    
    def __repr__(self):
        return f'<UserLocation {self.user_id} @ {self.latitude}, {self.longitude}>'


class LocationZone(db.Model, TimestampMixin, DynamicFieldsMixin):
    """
    Predefined zones/areas for location-based operations
    """
    __tablename__ = 'location_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Zone Boundaries (can be circle or polygon)
    zone_type = db.Column(db.String(20), nullable=False)  # 'circle', 'polygon', 'address'
    
    # For circular zones
    center_latitude = db.Column(db.Numeric(10, 8), nullable=True)
    center_longitude = db.Column(db.Numeric(11, 8), nullable=True)
    radius_meters = db.Column(db.Numeric(10, 2), nullable=True)
    
    # For polygon zones (stored as array of coordinates)
    polygon_coordinates = db.Column(JSONB, nullable=True)
    
    # For address-based zones
    address = db.Column(db.String(500), nullable=True)
    
    # Department/Team Association
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f'<LocationZone {self.name}>'


# ============================================================================
# NOTIFICATION & MESSAGING MODELS
# ============================================================================

class Notification(db.Model, TimestampMixin, DynamicFieldsMixin):
    """
    System-wide notification center
    """
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'info', 'warning', 'error', 'success', 'alert'
    priority = db.Column(db.String(20), nullable=False, default='normal')  # 'low', 'normal', 'high', 'urgent'
    
    # Status
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Action/Link
    action_url = db.Column(db.String(500), nullable=True)
    action_label = db.Column(db.String(100), nullable=True)
    
    # Related Entity
    related_entity_type = db.Column(db.String(50), nullable=True)
    related_entity_id = db.Column(db.Integer, nullable=True)
    
    # Sender (optional - for user-generated notifications)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    sender = db.relationship('User', foreign_keys=[sender_id])
    
    __table_args__ = (
        Index('idx_notification_user_unread', 'user_id', 'is_read'),
    )
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.title}>'


class Message(db.Model, TimestampMixin, SoftDeleteMixin, DynamicFieldsMixin):
    """
    Private messaging between users
    """
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    # Participants
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Content
    subject = db.Column(db.String(200), nullable=True)
    body = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), nullable=False, default='direct')  # 'direct', 'broadcast', 'system'
    
    # Status
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Threading
    parent_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True)
    thread_id = db.Column(db.Integer, nullable=True, index=True)
    
    # Attachments (stored as JSONB array)
    attachments = db.Column(JSONB, nullable=True)
    
    # Priority
    priority = db.Column(db.String(20), nullable=False, default='normal')
    
    # Relationships
    parent_message = db.relationship('Message', remote_side=[id], backref='replies')
    
    __table_args__ = (
        Index('idx_message_participants', 'sender_id', 'recipient_id'),
        Index('idx_message_recipient_unread', 'recipient_id', 'is_read'),
    )
    
    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id} to {self.recipient_id}>'


# ============================================================================
# SURVEY & QUESTION POOL MODELS
# ============================================================================

class QuestionPool(db.Model, TimestampMixin, SoftDeleteMixin, DynamicFieldsMixin):
    """
    Repository of questions maintained by department heads
    Questions can be reused across multiple surveys
    """
    __tablename__ = 'question_pools'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    # Pool Information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Ownership
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Categorization
    category = db.Column(db.String(100), nullable=True)
    tags = db.Column(JSONB, nullable=True, default=[])
    
    # Status
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    department = db.relationship('Department', backref='question_pools')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    questions = db.relationship('Question', backref='pool', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<QuestionPool {self.name}>'


class Question(db.Model, TimestampMixin, SoftDeleteMixin, DynamicFieldsMixin):
    """
    Individual questions in the pool
    Supports multiple question types and validation rules
    """
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    # Question Content
    pool_id = db.Column(db.Integer, db.ForeignKey('question_pools.id'), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    help_text = db.Column(db.Text, nullable=True)
    
    # Question Type
    question_type = db.Column(db.String(50), nullable=False)  
    # Types: 'text', 'number', 'date', 'time', 'datetime', 'single_choice', 
    #        'multiple_choice', 'rating', 'yes_no', 'file_upload', 'signature', 'location'
    
    # Options for choice-based questions (stored as JSONB)
    options = db.Column(JSONB, nullable=True)
    
    # Validation Rules
    is_required = db.Column(db.Boolean, nullable=False, default=False)
    validation_rules = db.Column(JSONB, nullable=True)  # min, max, pattern, etc.
    
    # Display Settings
    order_index = db.Column(db.Integer, nullable=False, default=0)
    display_conditions = db.Column(JSONB, nullable=True)  # Conditional display logic
    
    # Categorization
    category = db.Column(db.String(100), nullable=True)
    tags = db.Column(JSONB, nullable=True, default=[])
    
    # Status
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    __table_args__ = (
        Index('idx_question_pool', 'pool_id', 'is_active'),
    )
    
    def __repr__(self):
        return f'<Question {self.id} - {self.question_type}>'


class Survey(db.Model, TimestampMixin, SoftDeleteMixin, DynamicFieldsMixin):
    """
    Survey assignments created from question pool
    """
    __tablename__ = 'surveys'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    # Survey Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    
    # Assignment Details
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    
    # Timing
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    
    # Settings
    allow_multiple_submissions = db.Column(db.Boolean, nullable=False, default=False)
    require_location = db.Column(db.Boolean, nullable=False, default=True)
    is_anonymous = db.Column(db.Boolean, nullable=False, default=False)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='draft')  # 'draft', 'active', 'closed', 'archived'
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    department = db.relationship('Department', backref='surveys')
    team = db.relationship('Team', backref='surveys')
    survey_questions = db.relationship('SurveyQuestion', backref='survey', lazy='dynamic', cascade='all, delete-orphan')
    responses = db.relationship('SurveyResponse', backref='survey', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Survey {self.title}>'


class SurveyQuestion(db.Model):
    """
    Link table between surveys and questions with order and customization
    """
    __tablename__ = 'survey_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    
    # Override settings from original question
    order_index = db.Column(db.Integer, nullable=False, default=0)
    is_required_override = db.Column(db.Boolean, nullable=True)  # null = use question default
    custom_text = db.Column(db.Text, nullable=True)  # Override question text if needed
    
    # Relationships
    question = db.relationship('Question', backref='survey_assignments')
    
    __table_args__ = (
        Index('idx_survey_question', 'survey_id', 'question_id'),
        db.UniqueConstraint('survey_id', 'question_id', name='uq_survey_question'),
    )


class SurveyResponse(db.Model, TimestampMixin, DynamicFieldsMixin):
    """
    User responses to surveys - linked to organizational hierarchy at time of submission
    """
    __tablename__ = 'survey_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    # Survey & User
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Organizational Context (captured at submission time)
    department_id_at_submission = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    team_id_at_submission = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    role_id_at_submission = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    hierarchy_path = db.Column(JSONB, nullable=True)  # Full hierarchy at submission time
    
    # Location at Submission
    location_id = db.Column(db.Integer, db.ForeignKey('user_locations.id'), nullable=True)
    
    # Response Data
    submission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion_time_seconds = db.Column(db.Integer, nullable=True)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='completed')  # 'in_progress', 'completed', 'reviewed'
    
    # Relationships
    department_at_submission = db.relationship('Department', foreign_keys=[department_id_at_submission])
    team_at_submission = db.relationship('Team', foreign_keys=[team_id_at_submission])
    role_at_submission = db.relationship('Role', foreign_keys=[role_id_at_submission])
    location = db.relationship('UserLocation', foreign_keys=[location_id])
    answers = db.relationship('SurveyAnswer', backref='response', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_survey_response_user', 'survey_id', 'user_id'),
        Index('idx_survey_response_date', 'submission_date'),
    )
    
    def __repr__(self):
        return f'<SurveyResponse {self.id} by User {self.user_id}>'


class SurveyAnswer(db.Model, TimestampMixin):
    """
    Individual answers to survey questions
    """
    __tablename__ = 'survey_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    
    # Answer Storage (supports all question types)
    answer_text = db.Column(db.Text, nullable=True)
    answer_number = db.Column(db.Numeric(15, 4), nullable=True)
    answer_date = db.Column(db.Date, nullable=True)
    answer_time = db.Column(db.Time, nullable=True)
    answer_datetime = db.Column(db.DateTime, nullable=True)
    answer_json = db.Column(JSONB, nullable=True)  # For complex answers (multi-select, file refs, etc.)
    
    # Relationships
    question = db.relationship('Question', backref='answers')
    
    def __repr__(self):
        return f'<SurveyAnswer {self.id}>'


# ============================================================================
# CHECKLIST WORKFLOW MODELS
# ============================================================================

class ChecklistTemplate(db.Model, TimestampMixin, SoftDeleteMixin, DynamicFieldsMixin):
    """
    Reusable checklist templates
    """
    __tablename__ = 'checklist_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Ownership
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Settings
    require_location = db.Column(db.Boolean, nullable=False, default=True)
    require_all_items = db.Column(db.Boolean, nullable=False, default=True)
    
    # Status
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    department = db.relationship('Department', backref='checklist_templates')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    items = db.relationship('ChecklistItem', backref='template', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChecklistTemplate {self.name}>'


class ChecklistItem(db.Model, TimestampMixin, DynamicFieldsMixin):
    """
    Items in checklist templates
    """
    __tablename__ = 'checklist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_templates.id'), nullable=False, index=True)
    
    # Item Content
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Settings
    order_index = db.Column(db.Integer, nullable=False, default=0)
    is_required = db.Column(db.Boolean, nullable=False, default=True)
    requires_evidence = db.Column(db.Boolean, nullable=False, default=False)  # Photo, signature, etc.
    evidence_type = db.Column(db.String(50), nullable=True)  # 'photo', 'signature', 'note', 'file'
    
    # Status
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f'<ChecklistItem {self.title}>'


class ChecklistAssignment(db.Model, TimestampMixin, SoftDeleteMixin, DynamicFieldsMixin):
    """
    Assignment of checklist to users/teams
    """
    __tablename__ = 'checklist_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    template_id = db.Column(db.Integer, db.ForeignKey('checklist_templates.id'), nullable=False)
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_to_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timing
    due_date = db.Column(db.DateTime, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'in_progress', 'completed', 'overdue'
    
    # Relationships
    template = db.relationship('ChecklistTemplate', backref='assignments')
    assigned_to_user = db.relationship('User', foreign_keys=[assigned_to_user_id], backref='checklist_assignments')
    assigned_to_team = db.relationship('Team', foreign_keys=[assigned_to_team_id], backref='checklist_assignments')
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id])
    submissions = db.relationship('ChecklistSubmission', backref='assignment', lazy='dynamic')
    
    def __repr__(self):
        return f'<ChecklistAssignment {self.id}>'


class ChecklistSubmission(db.Model, TimestampMixin, DynamicFieldsMixin):
    """
    User submission of completed checklist
    """
    __tablename__ = 'checklist_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    assignment_id = db.Column(db.Integer, db.ForeignKey('checklist_assignments.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Organizational Context
    department_id_at_submission = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    team_id_at_submission = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    
    # Location
    location_id = db.Column(db.Integer, db.ForeignKey('user_locations.id'), nullable=True)
    
    # Submission Info
    submission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completion_time_seconds = db.Column(db.Integer, nullable=True)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='completed')
    
    # Relationships
    location = db.relationship('UserLocation', foreign_keys=[location_id])
    item_responses = db.relationship('ChecklistItemResponse', backref='submission', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChecklistSubmission {self.id}>'


class ChecklistItemResponse(db.Model, TimestampMixin):
    """
    Response to individual checklist items
    """
    __tablename__ = 'checklist_item_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('checklist_submissions.id'), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey('checklist_items.id'), nullable=False)
    
    # Response
    is_checked = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text, nullable=True)
    evidence_data = db.Column(JSONB, nullable=True)  # Photos, signatures, files
    
    # Relationships
    item = db.relationship('ChecklistItem', backref='responses')
    
    def __repr__(self):
        return f'<ChecklistItemResponse {self.id}>'


# ============================================================================
# DYNAMIC CONFIGURATION MODELS (Super Admin Configurable)
# ============================================================================

class CustomEntityType(db.Model, TimestampMixin):
    """
    Allows Super Admin to create custom entity types
    """
    __tablename__ = 'custom_entity_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Entity Settings
    icon = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(20), nullable=True)
    
    # Field Definitions
    field_definitions = db.Column(JSONB, nullable=False, default=[])
    
    # Status
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    entities = db.relationship('CustomEntity', backref='entity_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<CustomEntityType {self.name}>'


class CustomEntity(db.Model, TimestampMixin, SoftDeleteMixin):
    """
    Instances of custom entity types
    """
    __tablename__ = 'custom_entities'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False, default=lambda: uuid.uuid4())
    
    entity_type_id = db.Column(db.Integer, db.ForeignKey('custom_entity_types.id'), nullable=False, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Dynamic Data
    data = db.Column(JSONB, nullable=False, default={})
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    __table_args__ = (
        Index('idx_custom_entity_type', 'entity_type_id', 'is_deleted'),
    )
    
    def __repr__(self):
        return f'<CustomEntity {self.id}>'


class SystemConfiguration(db.Model, TimestampMixin):
    """
    System-wide configuration settings (Super Admin only)
    """
    __tablename__ = 'system_configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(JSONB, nullable=False)
    
    # Metadata
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    data_type = db.Column(db.String(20), nullable=False)  # 'string', 'number', 'boolean', 'json'
    
    # Security
    is_sensitive = db.Column(db.Boolean, nullable=False, default=False)
    requires_restart = db.Column(db.Boolean, nullable=False, default=False)
    
    # Last Modified
    modified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    modified_by = db.relationship('User', foreign_keys=[modified_by_id])
    
    def __repr__(self):
        return f'<SystemConfiguration {self.key}>'


# ============================================================================
# AUDIT & LOGGING MODELS
# ============================================================================

class AuditLog(db.Model, TimestampMixin):
    """
    Comprehensive audit logging for all system activities
    """
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Actor
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    user_email = db.Column(db.String(255), nullable=True)  # Snapshot in case user deleted
    
    # Action Details
    action = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    
    # Context
    description = db.Column(db.Text, nullable=True)
    old_values = db.Column(JSONB, nullable=True)
    new_values = db.Column(JSONB, nullable=True)
    
    # Request Context
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    request_url = db.Column(db.String(500), nullable=True)
    request_method = db.Column(db.String(10), nullable=True)
    
    # Result
    success = db.Column(db.Boolean, nullable=False, default=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_timestamp', 'created_at'),
    )
    
    def __repr__(self):
        return f'<AuditLog {self.action} by User {self.user_id}>'


# ============================================================================
# DATABASE EVENTS - Automatic History Tracking
# ============================================================================

def create_organization_history(mapper, connection, target):
    """Automatically create history record when organization changes"""
    # This would be implemented to automatically track changes
    pass


def update_location_current_flag(mapper, connection, target):
    """Automatically set is_current=False for old locations when new one is added"""
    if target.is_current:
        connection.execute(
            UserLocation.__table__.update().where(
                (UserLocation.user_id == target.user_id) &
                (UserLocation.id != target.id)
            ).values(is_current=False)
        )


# Register event listeners
event.listen(User, 'after_update', create_organization_history)
event.listen(Department, 'after_update', create_organization_history)
event.listen(Team, 'after_update', create_organization_history)
event.listen(UserLocation, 'before_insert', update_location_current_flag)
