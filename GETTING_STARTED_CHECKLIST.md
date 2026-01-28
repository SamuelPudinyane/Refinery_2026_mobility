# 🎯 Getting Started Checklist

Use this checklist to set up and deploy your dynamic mobility application database.

## ✅ Phase 1: Initial Setup (15 minutes)

### Prerequisites
- [ ] PostgreSQL 12+ installed and running
- [ ] Python 3.8+ installed
- [ ] Virtual environment activated (`.\myvenv\Scripts\Activate.ps1`)
- [ ] `.env` file configured with database credentials
- [ ] All dependencies installed (`pip install -r requirements.txt`)

### Database Connection
- [ ] Verify PostgreSQL is running
  ```bash
  # Test with:
  psql -U postgres -c "SELECT version();"
  ```
- [ ] Database `mobility_rand_v2` exists
  ```bash
  # Create if needed:
  psql -U postgres -c "CREATE DATABASE mobility_rand_v2;"
  ```
- [ ] Connection string in `.env` is correct
  ```env
  DATABASE_URL=postgresql://postgres:malvapudding78*@localhost:5432/mobility_rand_v2
  ```
- [ ] Test database connection
  ```bash
  python -c "from dbqueries import get_db_connection; print('✓ Connected' if get_db_connection() else '✗ Failed')"
  ```

## ✅ Phase 2: Database Initialization (5 minutes)

### Run Initialization Script
- [ ] Execute `python init_database.py`
- [ ] Verify output shows:
  - [ ] ✓ All tables created successfully
  - [ ] ✓ System roles initialized (6 roles)
  - [ ] ✓ Super Admin user created
  - [ ] ✓ System configuration initialized
  - [ ] ✓ Sample departments created (if opted in)

### Verify Installation
- [ ] Check tables created in database
  ```bash
  python -c "from app import app; from models import db; from sqlalchemy import inspect; \
  with app.app_context(): print(f'{len(inspect(db.engine).get_table_names())} tables created')"
  ```
- [ ] Expected: 25+ tables created

### Test Super Admin Login
- [ ] Start application: `python app.py`
- [ ] Navigate to: http://localhost:5000/login
- [ ] Login with:
  - Username: `superadmin`
  - Password: `Admin@123`
- [ ] **IMMEDIATELY change password** after first login

## ✅ Phase 3: Data Migration (Optional - 10 minutes)

### If Migrating from Old System
- [ ] Backup old database first
  ```bash
  pg_dump -U postgres -d old_database -F c -f backup_before_migration.dump
  ```
- [ ] Review old data in tables:
  - [ ] `rand_refinary_registration` (users)
  - [ ] `assigsections` (sections/departments)
  - [ ] `checklistquestions` (questions)
  - [ ] `sectionlocation` (locations)

### Run Migration
- [ ] Full migration: `python migrate_database.py`
- [ ] OR incremental:
  - [ ] Migrate users: `python migrate_database.py users`
  - [ ] Migrate departments: `python migrate_database.py departments`
  - [ ] Migrate questions: `python migrate_database.py questions`
  - [ ] Migrate locations: `python migrate_database.py locations`

### Verify Migration
- [ ] Run verification: `python migrate_database.py verify`
- [ ] Check migrated record counts match expectations
- [ ] Test login with migrated user account

## ✅ Phase 4: Configure System (20 minutes)

### Create Organizational Structure
- [ ] Create root/main departments
- [ ] Create sub-departments if needed
- [ ] Create teams within departments
- [ ] Assign department heads
- [ ] Assign team leaders

### Create Users
- [ ] Create Admin users
- [ ] Create Department Head users
- [ ] Create Team Leader users
- [ ] Create Operator users (field workers)
- [ ] Verify each user can login

### Set Up Roles & Permissions
- [ ] Review default role permissions
- [ ] Customize permissions if needed
- [ ] Create custom roles if required
- [ ] Assign users to appropriate roles

### Configure System Settings
- [ ] Set location update interval
  ```python
  from admin_helpers import set_config
  set_config('location_update_interval_seconds', 300, modified_by_id=1)
  ```
- [ ] Configure location requirements for surveys
- [ ] Set session timeout
- [ ] Configure file upload limits
- [ ] Set notification preferences

## ✅ Phase 5: Create Content (30 minutes)

### Create Question Pools
- [ ] Department heads create question pools
- [ ] Add questions to pools (various types):
  - [ ] Text questions
  - [ ] Choice questions (single/multiple)
  - [ ] Yes/No questions
  - [ ] Number/rating questions
  - [ ] Date/time questions
  - [ ] Location questions
  - [ ] File upload questions
- [ ] Categorize questions
- [ ] Set validation rules

### Create Surveys
- [ ] Create surveys from question pools
- [ ] Set survey dates (start/end)
- [ ] Configure survey settings:
  - [ ] Require location
  - [ ] Allow multiple submissions
  - [ ] Anonymous vs identified
- [ ] Assign surveys to departments/teams
- [ ] Test survey on mobile device

### Create Checklists
- [ ] Create checklist templates
- [ ] Add checklist items
- [ ] Configure evidence requirements (photos, signatures)
- [ ] Set item requirements (mandatory/optional)
- [ ] Assign checklists to users/teams
- [ ] Test checklist completion

## ✅ Phase 6: Testing (20 minutes)

### User Login Testing
- [ ] Test Super Admin login
- [ ] Test Admin login
- [ ] Test Department Head login
- [ ] Test Team Leader login
- [ ] Test Operator login
- [ ] Verify role-based access working

### Survey Testing
- [ ] Create test survey
- [ ] Assign to test user
- [ ] Complete survey on device
- [ ] Verify location captured
- [ ] Check response saved correctly
- [ ] Review response in admin interface

### Checklist Testing
- [ ] Create test checklist
- [ ] Assign to test user
- [ ] Complete checklist with evidence
- [ ] Verify location captured
- [ ] Check submission saved
- [ ] Review checklist results

### Location Tracking Testing
- [ ] Enable location tracking
- [ ] Verify locations updating
- [ ] Check location history
- [ ] Test location zones (if configured)

### Communication Testing
- [ ] Send test notification
- [ ] Send test message
- [ ] Verify delivery
- [ ] Test read receipts

### Audit Trail Testing
- [ ] Make organizational changes
- [ ] Check OrganizationHistory records
- [ ] Review AuditLog entries
- [ ] Verify before/after states preserved

## ✅ Phase 7: Advanced Configuration (Optional - 30 minutes)

### Create Custom Entity Types
- [ ] Identify needed custom entities (e.g., Equipment Register)
- [ ] Define field definitions
- [ ] Create entity types via admin helpers
- [ ] Test creating entity instances
- [ ] Link to surveys/checklists if needed

### Add Custom Fields
- [ ] Identify entities needing custom fields
- [ ] Define field specifications
- [ ] Add fields using admin helpers
- [ ] Test field functionality
- [ ] Update forms to include new fields

### Configure Location Zones
- [ ] Define geographical zones
- [ ] Set zone boundaries (circle/polygon)
- [ ] Link zones to departments
- [ ] Test zone-based features

### Set Up Reporting
- [ ] Configure report parameters
- [ ] Test hierarchy statistics
- [ ] Test activity summaries
- [ ] Export sample reports

## ✅ Phase 8: Production Preparation (30 minutes)

### Security Hardening
- [ ] Change all default passwords
- [ ] Review and customize role permissions
- [ ] Enable HTTPS (if not already)
- [ ] Configure firewall rules
- [ ] Set up SSL for PostgreSQL
- [ ] Review audit log settings

### Database Optimization
- [ ] Analyze query performance
- [ ] Add additional indexes if needed
- [ ] Configure connection pooling
- [ ] Set up database monitoring
- [ ] Configure automatic backups

### Backup Strategy
- [ ] Set up automated daily backups
  ```bash
  # Example cron job:
  0 2 * * * pg_dump -U postgres mobility_rand_v2 -F c -f /backups/mobility_$(date +\%Y\%m\%d).dump
  ```
- [ ] Test backup restoration
- [ ] Document backup procedure
- [ ] Set up off-site backup storage

### Documentation
- [ ] Document custom configurations
- [ ] Create user guides for each role
- [ ] Document custom entity types
- [ ] Document custom fields added
- [ ] Create troubleshooting guide

### Monitoring Setup
- [ ] Set up database monitoring
- [ ] Configure application logging
- [ ] Set up error alerting
- [ ] Monitor disk space usage
- [ ] Track performance metrics

## ✅ Phase 9: User Training (Variable Time)

### Admin Training
- [ ] System overview
- [ ] Managing users and roles
- [ ] Creating departments and teams
- [ ] Viewing audit trails
- [ ] Running reports

### Department Head Training
- [ ] Creating question pools
- [ ] Building surveys
- [ ] Creating checklists
- [ ] Reviewing responses
- [ ] Managing team members

### Operator Training
- [ ] Mobile app usage
- [ ] Completing surveys
- [ ] Submitting checklists
- [ ] Location tracking
- [ ] Messaging system

## ✅ Phase 10: Go Live (Variable Time)

### Pre-Launch Checklist
- [ ] All users created and verified
- [ ] All content (surveys/checklists) ready
- [ ] Mobile devices configured
- [ ] Backup system tested
- [ ] Monitoring active
- [ ] Support plan in place

### Launch Day
- [ ] Start application in production
- [ ] Monitor initial usage
- [ ] Be available for support
- [ ] Track any issues
- [ ] Collect user feedback

### Post-Launch
- [ ] Review first day activity
- [ ] Address any issues found
- [ ] Gather user feedback
- [ ] Make adjustments as needed
- [ ] Schedule follow-up training if needed

## 📊 Success Metrics

Track these metrics to measure success:
- [ ] User login rate (target: 90%+ of users logging in within first week)
- [ ] Survey completion rate (target: 80%+ completion)
- [ ] Checklist compliance (target: 90%+ completion)
- [ ] Location tracking accuracy (target: 95%+ successful captures)
- [ ] System uptime (target: 99%+)
- [ ] User satisfaction (target: 4+/5 rating)

## 🆘 Troubleshooting Quick Reference

### Common Issues

**Database connection fails**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -U postgres -d mobility_rand_v2
```

**Tables not created**
```bash
# Re-run initialization
python init_database.py

# Check for errors in output
```

**Migration fails**
```bash
# Run verification
python migrate_database.py verify

# Run specific migration
python migrate_database.py users
```

**Location not capturing**
- Check browser location permissions
- Verify HTTPS is enabled (required for geolocation)
- Check `require_location_for_surveys` configuration

**Permissions not working**
- Check user's role assignment
- Review role permissions in database
- Clear user session and re-login

## 📚 Reference Documents

Quick links to documentation:
- [README_DATABASE.md](README_DATABASE.md) - System overview
- [DATABASE_ARCHITECTURE.md](DATABASE_ARCHITECTURE.md) - Technical details
- [QUICKSTART_DATABASE.md](QUICKSTART_DATABASE.md) - Setup guide
- [DATABASE_DIAGRAM.md](DATABASE_DIAGRAM.md) - Visual schema
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - What was built
- [models.py](models.py) - Database models (commented)
- [admin_helpers.py](admin_helpers.py) - Admin utilities
- [init_database.py](init_database.py) - Initialization script
- [migrate_database.py](migrate_database.py) - Migration utilities

## ✨ Congratulations!

Once all checkboxes are complete, your dynamic mobility application database is fully operational!

**Key Achievements:**
- ✅ Modern, flexible database architecture
- ✅ Dynamic field system (no code changes needed)
- ✅ Complete audit trail
- ✅ Hierarchical organization support
- ✅ Survey and checklist workflows
- ✅ Real-time location tracking
- ✅ Communication systems
- ✅ Production-ready with backups and monitoring

**You now have a enterprise-grade mobility application! 🚀**

---

**Need Help?**
- Review documentation in markdown files
- Check code comments in Python files
- Run verification scripts
- Contact system administrator

**Last Updated**: January 28, 2026
