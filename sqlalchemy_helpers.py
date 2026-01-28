"""
SQLAlchemy Helper Functions for app.py
Replaces old dbqueries.py functions with SQLAlchemy ORM equivalents
"""

from models import (
    db, User, Role, Department, Team, QuestionPool, Question,
    Survey, SurveyQuestion, SurveyResponse, SurveyAnswer,
    ChecklistTemplate, ChecklistItem, ChecklistAssignment, ChecklistSubmission,
    ChecklistItemResponse, UserLocation, AuditLog
)
from sqlalchemy import and_, or_, func
from datetime import datetime
import json


# ============================================================================
# USER & AUTHENTICATION HELPERS
# ============================================================================

def get_user_by_company_number(company_number):
    """Get user by company number"""
    return User.query.filter_by(
        company_number=company_number,
        is_deleted=False
    ).first()


def get_all_operators():
    """Get all users with operator role"""
    operator_role = Role.query.filter_by(name='operator').first()
    if not operator_role:
        return []
    
    return User.query.filter_by(
        role_id=operator_role.id,
        is_deleted=False
    ).all()


def get_all_administrators():
    """Get all users with admin or higher roles"""
    admin_roles = Role.query.filter(Role.level >= 60).all()
    admin_role_ids = [r.id for r in admin_roles]
    
    return User.query.filter(
        User.role_id.in_(admin_role_ids),
        User.is_deleted == False
    ).all()


# ============================================================================
# DEPARTMENT & TEAM HELPERS
# ============================================================================

def get_all_plant_sections():
    """Get all active departments (plant sections)"""
    return Department.query.filter_by(
        is_deleted=False,
        is_active=True
    ).order_by(Department.name).all()


def get_user_departments(user_id):
    """Get departments where user is assigned"""
    user = User.query.get(user_id)
    if not user or not user.department:
        return []
    
    # Return user's department and all its sub-departments
    departments = [user.department]
    if user.department.sub_departments:
        departments.extend(user.department.sub_departments)
    
    return departments


# ============================================================================
# QUESTION & QUESTION POOL HELPERS
# ============================================================================

def get_questions_by_department(department_name):
    """Get all questions for a specific department"""
    department = Department.query.filter_by(name=department_name).first()
    if not department:
        return []
    
    # Get questions from all pools in this department
    questions = db.session.query(Question).join(
        QuestionPool
    ).filter(
        QuestionPool.department_id == department.id,
        QuestionPool.is_deleted == False,
        Question.is_deleted == False,
        Question.is_active == True
    ).order_by(Question.order_index).all()
    
    return questions


def get_question_by_id(question_id):
    """Get a single question by ID"""
    return Question.query.filter_by(
        id=question_id,
        is_deleted=False
    ).first()


def check_question_exists(department_name, question_text):
    """Check if a question already exists in a department"""
    department = Department.query.filter_by(name=department_name).first()
    if not department:
        return False
    
    exists = db.session.query(Question).join(
        QuestionPool
    ).filter(
        QuestionPool.department_id == department.id,
        Question.question_text == question_text,
        Question.is_deleted == False
    ).first()
    
    return exists is not None


def create_question(department_name, question_text, question_type, options, reasoning, user_id):
    """Create a new question in a department's question pool"""
    # Get or create department
    department = Department.query.filter_by(name=department_name).first()
    if not department:
        department = Department(
            name=department_name,
            code=department_name.upper().replace(' ', '_')[:50],
            level=1,
            is_active=True
        )
        db.session.add(department)
        db.session.flush()
    
    # Get or create question pool for this department
    pool = QuestionPool.query.filter_by(
        department_id=department.id,
        is_deleted=False
    ).first()
    
    if not pool:
        pool = QuestionPool(
            name=f"{department_name} Questions",
            department_id=department.id,
            created_by_id=user_id,
            is_active=True
        )
        db.session.add(pool)
        db.session.flush()
    
    # Create question
    question = Question(
        pool_id=pool.id,
        question_text=question_text,
        question_type=question_type,
        options=options if options else None,
        custom_fields={'reasoning': reasoning} if reasoning else {},
        is_required=False,
        is_active=True
    )
    
    db.session.add(question)
    db.session.commit()
    
    return question


def update_question(question_id, question_text, question_type, options, reasoning):
    """Update an existing question"""
    question = Question.query.get(question_id)
    if not question:
        return False
    
    question.question_text = question_text
    question.question_type = question_type
    question.options = options if options else None
    
    custom_fields = question.custom_fields or {}
    if reasoning:
        custom_fields['reasoning'] = reasoning
    question.custom_fields = custom_fields
    
    question.updated_at = datetime.utcnow()
    db.session.commit()
    
    return True


def delete_question(question_id):
    """Soft delete a question"""
    question = Question.query.get(question_id)
    if not question:
        return False
    
    question.is_deleted = True
    question.deleted_at = datetime.utcnow()
    db.session.commit()
    
    return True


# ============================================================================
# CHECKLIST HELPERS
# ============================================================================

def get_questions_for_operator(company_number):
    """Get checklist questions assigned to an operator"""
    user = User.query.filter_by(
        company_number=company_number,
        is_deleted=False
    ).first()
    
    if not user:
        return []
    
    # Get active checklist assignments for this user
    assignments = ChecklistAssignment.query.filter(
        or_(
            ChecklistAssignment.assigned_to_user_id == user.id,
            ChecklistAssignment.assigned_to_team_id == user.team_id
        ),
        ChecklistAssignment.status.in_(['pending', 'in_progress']),
        ChecklistAssignment.is_deleted == False
    ).all()
    
    return assignments


def create_checklist_assignment(template_id, user_id, location_data, created_by_id):
    """Create a new checklist assignment"""
    assignment = ChecklistAssignment(
        template_id=template_id,
        assigned_to_user_id=user_id,
        assigned_by_id=created_by_id,
        status='pending',
        custom_fields={'location': location_data}
    )
    
    db.session.add(assignment)
    db.session.commit()
    
    return assignment


def submit_checklist_answers(assignment_id, answers, user_location):
    """Submit checklist answers"""
    assignment = ChecklistAssignment.query.get(assignment_id)
    if not assignment:
        return False
    
    # Create submission
    submission = ChecklistSubmission(
        assignment_id=assignment_id,
        user_id=assignment.assigned_to_user_id,
        department_id_at_submission=assignment.assigned_to_user.department_id,
        team_id_at_submission=assignment.assigned_to_user.team_id,
        status='completed',
        custom_fields={'answers': answers, 'location': user_location}
    )
    
    db.session.add(submission)
    
    # Update assignment status
    assignment.status = 'completed'
    assignment.completed_date = datetime.utcnow()
    
    db.session.commit()
    
    return True


def delete_checklist(checklist_id):
    """Delete a checklist assignment"""
    assignment = ChecklistAssignment.query.get(checklist_id)
    if not assignment:
        return False
    
    assignment.is_deleted = True
    assignment.deleted_at = datetime.utcnow()
    db.session.commit()
    
    return True


# ============================================================================
# LOCATION HELPERS
# ============================================================================

def get_locations_by_department(department_name):
    """Get all location zones for a department"""
    department = Department.query.filter_by(name=department_name).first()
    if not department:
        return []
    
    from models import LocationZone
    return LocationZone.query.filter_by(
        department_id=department.id,
        is_active=True
    ).all()


def save_user_location(user_id, latitude, longitude, location_type='manual'):
    """Save user's location"""
    from models import UserLocation
    
    # Mark previous locations as not current
    UserLocation.query.filter_by(user_id=user_id).update({'is_current': False})
    
    # Create new location
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


# ============================================================================
# SURVEY & ANSWERS HELPERS
# ============================================================================

def get_all_answered_checklists():
    """Get all completed checklist submissions"""
    return ChecklistSubmission.query.filter_by(
        status='completed'
    ).order_by(ChecklistSubmission.submission_date.desc()).all()


def get_answered_checklists_by_department(department_name):
    """Get completed checklists for a specific department"""
    department = Department.query.filter_by(name=department_name).first()
    if not department:
        return []
    
    return ChecklistSubmission.query.filter_by(
        department_id_at_submission=department.id,
        status='completed'
    ).order_by(ChecklistSubmission.submission_date.desc()).all()


# ============================================================================
# STATISTICS & REPORTING
# ============================================================================

def get_checklist_count():
    """Get count of active checklist assignments"""
    return ChecklistAssignment.query.filter_by(
        is_deleted=False
    ).count()


def get_user_stats():
    """Get user statistics"""
    total_users = User.query.filter_by(is_deleted=False).count()
    active_users = User.query.filter_by(is_deleted=False, is_active=True).count()
    
    return {
        'total': total_users,
        'active': active_users,
        'inactive': total_users - active_users
    }


# ============================================================================
# COMPATIBILITY FUNCTIONS (for easier migration)
# ============================================================================

def convert_question_to_dict(question):
    """Convert Question object to dictionary (for backwards compatibility)"""
    return {
        'id': question.id,
        'question': question.question_text,
        'question_text': question.question_text,
        'type': question.question_type,
        'options': question.options or [],
        'required': question.is_required,
        'reasoning': question.custom_fields.get('reasoning') if question.custom_fields else None,
        'plant_section': question.pool.department.name if question.pool and question.pool.department else None,
        'created_at': question.created_at.isoformat() if question.created_at else None
    }


def convert_user_to_dict(user):
    """Convert User object to dictionary (for session storage)"""
    return {
        'id': user.id,
        'username': user.username,
        'company_number': user.company_number,
        'name': user.full_name or user.username,
        'email': user.email,
        'role': user.role.name if user.role else None,
        'role_id': user.role_id,
        'department_id': user.department_id,
        'team_id': user.team_id
    }


def convert_checklist_assignment_to_dict(assignment):
    """Convert ChecklistAssignment to dict for compatibility"""
    template = assignment.template
    location_data = assignment.custom_fields.get('location', []) if assignment.custom_fields else []
    
    # Get items from template
    items = ChecklistItem.query.filter_by(
        template_id=template.id,
        is_active=True
    ).order_by(ChecklistItem.order_index).all()
    
    checklist_questions = []
    for item in items:
        checklist_questions.append({
            'id': item.id,
            'question': item.title,
            'description': item.description,
            'required': item.is_required,
            'requires_evidence': item.requires_evidence,
            'evidence_type': item.evidence_type
        })
    
    return {
        'id': assignment.id,
        'checklist_questions': json.dumps(checklist_questions),
        'location': json.dumps(location_data),
        'status': assignment.status,
        'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
        'assigned_to': assignment.assigned_to_user.full_name if assignment.assigned_to_user else None,
        'company_number': assignment.assigned_to_user.company_number if assignment.assigned_to_user else None
    }
