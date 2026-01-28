"""
Migration Utility - Old System to New Dynamic Models
Migrates data from old database structure to new SQLAlchemy models
"""

from models import (
    db, User, Role, Department, Team, QuestionPool, Question,
    Survey, SurveyQuestion, SurveyResponse, SurveyAnswer,
    UserLocation, Notification, OrganizationHistory, AuditLog
)
from dbqueries import get_db_connection
from encryption import hash_password
from datetime import datetime
import json


# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

def migrate_users():
    """
    Migrate users from rand_refinary_registration to new User model
    """
    print("\n" + "="*60)
    print("Migrating Users")
    print("="*60)
    
    try:
        # Get old users
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, company_number, password, role, name, created_at
            FROM rand_refinary_registration
            ORDER BY id
        """)
        old_users = cur.fetchall()
        
        # Role mapping
        role_map = {
            'super_admin': 'super_admin',
            'admin': 'admin',
            'operator': 'operator',
            'viewer': 'viewer'
        }
        
        migrated_count = 0
        skipped_count = 0
        
        for old_user in old_users:
            user_id, company_num, password, old_role, name, created_at = old_user
            
            # Check if already migrated
            existing = User.query.filter_by(company_number=company_num).first()
            if existing:
                print(f"  Skipping {company_num} - already exists")
                skipped_count += 1
                continue
            
            # Get role
            role_name = role_map.get(old_role, 'operator')
            role = Role.query.filter_by(name=role_name).first()
            
            if not role:
                print(f"  ✗ Role '{role_name}' not found, using 'operator'")
                role = Role.query.filter_by(name='operator').first()
            
            # Create new user
            new_user = User(
                username=company_num or f'user_{user_id}',
                company_number=company_num,
                password_hash=password,  # Already hashed
                full_name=name,
                role_id=role.id,
                is_active=True,
                is_verified=True,
                created_at=created_at or datetime.utcnow()
            )
            
            db.session.add(new_user)
            migrated_count += 1
            print(f"  ✓ Migrated: {company_num} ({name})")
        
        db.session.commit()
        cur.close()
        conn.close()
        
        print(f"\nUsers Migration Complete:")
        print(f"  Migrated: {migrated_count}")
        print(f"  Skipped: {skipped_count}")
        
        return migrated_count
        
    except Exception as e:
        print(f"✗ Error migrating users: {e}")
        db.session.rollback()
        return 0


def migrate_sections_to_departments():
    """
    Migrate plant sections to Department model
    """
    print("\n" + "="*60)
    print("Migrating Sections to Departments")
    print("="*60)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get unique sections
        cur.execute("""
            SELECT DISTINCT plant_section
            FROM assigsections
            WHERE plant_section IS NOT NULL
            ORDER BY plant_section
        """)
        sections = cur.fetchall()
        
        migrated_count = 0
        
        for (section_name,) in sections:
            # Check if already exists
            existing = Department.query.filter_by(name=section_name).first()
            if existing:
                print(f"  Skipping {section_name} - already exists")
                continue
            
            # Create department
            dept = Department(
                name=section_name,
                code=section_name.upper().replace(' ', '_')[:50],
                description=f'Migrated from {section_name}',
                level=1,
                is_active=True
            )
            
            db.session.add(dept)
            migrated_count += 1
            print(f"  ✓ Created department: {section_name}")
        
        db.session.commit()
        cur.close()
        conn.close()
        
        print(f"\nDepartments Migration Complete: {migrated_count} created")
        return migrated_count
        
    except Exception as e:
        print(f"✗ Error migrating departments: {e}")
        db.session.rollback()
        return 0


def migrate_questions_to_pools():
    """
    Migrate questions from checklistquestions to QuestionPool and Question models
    """
    print("\n" + "="*60)
    print("Migrating Questions to Question Pools")
    print("="*60)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get all questions grouped by section
        cur.execute("""
            SELECT id, plant_section, question, company_number, created_at
            FROM checklistquestions
            ORDER BY plant_section, id
        """)
        old_questions = cur.fetchall()
        
        # Group by section
        sections_questions = {}
        for q_id, section, question_text, company_num, created_at in old_questions:
            if section not in sections_questions:
                sections_questions[section] = []
            sections_questions[section].append({
                'id': q_id,
                'text': question_text,
                'company_number': company_num,
                'created_at': created_at
            })
        
        pools_created = 0
        questions_created = 0
        
        # Get super admin for created_by
        super_admin = User.query.filter_by(username='superadmin').first()
        if not super_admin:
            super_admin = User.query.first()
        
        for section, questions in sections_questions.items():
            # Get or create department
            dept = Department.query.filter_by(name=section).first()
            if not dept:
                dept = Department(
                    name=section,
                    code=section.upper().replace(' ', '_')[:50],
                    level=1,
                    is_active=True
                )
                db.session.add(dept)
                db.session.flush()
            
            # Check if pool exists
            pool = QuestionPool.query.filter_by(
                department_id=dept.id,
                name=f'{section} Questions'
            ).first()
            
            if not pool:
                # Create question pool
                pool = QuestionPool(
                    name=f'{section} Questions',
                    description=f'Migrated questions for {section}',
                    department_id=dept.id,
                    created_by_id=super_admin.id if super_admin else 1,
                    category='migrated',
                    is_active=True
                )
                db.session.add(pool)
                db.session.flush()
                pools_created += 1
                print(f"  ✓ Created pool: {pool.name}")
            
            # Add questions to pool
            for idx, q_data in enumerate(questions):
                # Check if question already exists
                existing_q = Question.query.filter_by(
                    pool_id=pool.id,
                    question_text=q_data['text']
                ).first()
                
                if existing_q:
                    continue
                
                question = Question(
                    pool_id=pool.id,
                    question_text=q_data['text'],
                    question_type='text',  # Default type
                    is_required=False,
                    order_index=idx,
                    is_active=True,
                    created_at=q_data['created_at'] or datetime.utcnow()
                )
                
                db.session.add(question)
                questions_created += 1
        
        db.session.commit()
        cur.close()
        conn.close()
        
        print(f"\nQuestions Migration Complete:")
        print(f"  Pools Created: {pools_created}")
        print(f"  Questions Created: {questions_created}")
        
        return questions_created
        
    except Exception as e:
        print(f"✗ Error migrating questions: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return 0


def migrate_locations():
    """
    Migrate location data from sectionlocation to UserLocation
    """
    print("\n" + "="*60)
    print("Migrating Locations")
    print("="*60)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get locations
        cur.execute("""
            SELECT id, company_number, plant_section, latitude, longitude, created_at
            FROM sectionlocation
            ORDER BY created_at
        """)
        old_locations = cur.fetchall()
        
        migrated_count = 0
        skipped_count = 0
        
        for loc_data in old_locations:
            loc_id, company_num, section, lat, lon, created_at = loc_data
            
            # Find user
            user = User.query.filter_by(company_number=company_num).first()
            if not user:
                skipped_count += 1
                continue
            
            # Create location record
            location = UserLocation(
                user_id=user.id,
                latitude=lat,
                longitude=lon,
                location_type='migrated',
                is_current=False,  # Historical data
                created_at=created_at or datetime.utcnow()
            )
            
            db.session.add(location)
            migrated_count += 1
        
        db.session.commit()
        cur.close()
        conn.close()
        
        print(f"\nLocations Migration Complete:")
        print(f"  Migrated: {migrated_count}")
        print(f"  Skipped: {skipped_count}")
        
        return migrated_count
        
    except Exception as e:
        print(f"✗ Error migrating locations: {e}")
        db.session.rollback()
        return 0


def migrate_answered_questions():
    """
    Migrate answered questions to SurveyResponse and SurveyAnswer models
    Note: This is complex and requires manual survey creation first
    """
    print("\n" + "="*60)
    print("Migrating Answered Questions (Survey Responses)")
    print("="*60)
    print("\n⚠️  WARNING: This requires surveys to be created first!")
    print("This migration should be run after:")
    print("  1. Questions are migrated to pools")
    print("  2. Surveys are created from those pools")
    print("  3. Survey questions are linked")
    print("\nSkipping for now - manual migration recommended.")
    print("="*60)
    
    return 0


def create_audit_entries_for_migrations():
    """
    Create audit log entries for all migrations
    """
    print("\n" + "="*60)
    print("Creating Audit Entries")
    print("="*60)
    
    try:
        super_admin = User.query.filter_by(username='superadmin').first()
        
        audit_entry = AuditLog(
            user_id=super_admin.id if super_admin else None,
            action='data_migration',
            entity_type='system',
            entity_id=0,
            description='Migrated data from old database structure to new dynamic models',
            success=True,
            ip_address='127.0.0.1'
        )
        
        db.session.add(audit_entry)
        db.session.commit()
        
        print("✓ Audit entry created")
        
    except Exception as e:
        print(f"✗ Error creating audit entry: {e}")


# ============================================================================
# MAIN MIGRATION FUNCTION
# ============================================================================

def run_full_migration():
    """
    Run complete migration from old to new system
    """
    print("\n" + "="*70)
    print("MOBILITY APPLICATION - DATABASE MIGRATION")
    print("Old System → New Dynamic Models")
    print("="*70)
    
    print("\n⚠️  IMPORTANT:")
    print("  - Ensure init_database.py has been run first")
    print("  - Ensure you have a backup of the old database")
    print("  - This process will NOT delete old tables")
    print("  - Review results carefully after migration")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    results = {
        'users': 0,
        'departments': 0,
        'questions': 0,
        'locations': 0
    }
    
    # Run migrations in order
    results['users'] = migrate_users()
    results['departments'] = migrate_sections_to_departments()
    results['questions'] = migrate_questions_to_pools()
    results['locations'] = migrate_locations()
    
    # Create audit trail
    create_audit_entries_for_migrations()
    
    # Summary
    print("\n" + "="*70)
    print("MIGRATION SUMMARY")
    print("="*70)
    print(f"Users Migrated:        {results['users']}")
    print(f"Departments Created:   {results['departments']}")
    print(f"Questions Migrated:    {results['questions']}")
    print(f"Locations Migrated:    {results['locations']}")
    print("="*70)
    
    print("\n✓ Migration Complete!")
    print("\nNext Steps:")
    print("  1. Verify migrated data in database")
    print("  2. Create surveys from question pools")
    print("  3. Assign users to departments and teams")
    print("  4. Test application functionality")
    print("  5. Backup new database structure")
    
    return results


def verify_migration():
    """
    Verify migration results
    """
    print("\n" + "="*60)
    print("MIGRATION VERIFICATION")
    print("="*60)
    
    checks = []
    
    # Check users
    user_count = User.query.filter_by(is_deleted=False).count()
    checks.append(f"Users in new system: {user_count}")
    
    # Check departments
    dept_count = Department.query.filter_by(is_deleted=False).count()
    checks.append(f"Departments: {dept_count}")
    
    # Check question pools
    pool_count = QuestionPool.query.filter_by(is_deleted=False).count()
    checks.append(f"Question Pools: {pool_count}")
    
    # Check questions
    question_count = Question.query.filter_by(is_deleted=False).count()
    checks.append(f"Questions: {question_count}")
    
    # Check locations
    location_count = UserLocation.query.count()
    checks.append(f"Location Records: {location_count}")
    
    # Check roles
    role_count = Role.query.filter_by(is_active=True).count()
    checks.append(f"Active Roles: {role_count}")
    
    for check in checks:
        print(f"  ✓ {check}")
    
    print("\n" + "="*60)
    
    return checks


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def rollback_migration():
    """
    Rollback migration (use with caution!)
    """
    print("\n⚠️  WARNING: This will delete ALL data in new tables!")
    print("Old tables will NOT be affected.")
    
    confirm = input("\nType 'ROLLBACK' to confirm: ")
    if confirm != 'ROLLBACK':
        print("Cancelled.")
        return
    
    print("\nRolling back migration...")
    
    try:
        # Delete in reverse order of foreign keys
        SurveyAnswer.query.delete()
        SurveyResponse.query.delete()
        SurveyQuestion.query.delete()
        Survey.query.delete()
        Question.query.delete()
        QuestionPool.query.delete()
        UserLocation.query.delete()
        Team.query.delete()
        User.query.filter(User.username != 'superadmin').delete()
        Department.query.delete()
        
        db.session.commit()
        
        print("✓ Rollback complete")
        
    except Exception as e:
        print(f"✗ Error during rollback: {e}")
        db.session.rollback()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    from app import app
    
    with app.app_context():
        import sys
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == 'verify':
                verify_migration()
            elif command == 'rollback':
                rollback_migration()
            elif command == 'users':
                migrate_users()
            elif command == 'departments':
                migrate_sections_to_departments()
            elif command == 'questions':
                migrate_questions_to_pools()
            elif command == 'locations':
                migrate_locations()
            else:
                print(f"Unknown command: {command}")
                print("\nAvailable commands:")
                print("  python migrate_database.py           - Run full migration")
                print("  python migrate_database.py verify    - Verify migration results")
                print("  python migrate_database.py users     - Migrate users only")
                print("  python migrate_database.py departments - Migrate departments only")
                print("  python migrate_database.py questions - Migrate questions only")
                print("  python migrate_database.py locations - Migrate locations only")
                print("  python migrate_database.py rollback  - Rollback migration (DANGEROUS!)")
        else:
            # Run full migration
            results = run_full_migration()
            
            # Verify
            print("\n")
            verify_migration()
