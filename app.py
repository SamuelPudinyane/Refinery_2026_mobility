from flask import render_template, Flask, request, session, flash, redirect, url_for, jsonify
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from sqlalchemy import and_, or_
from geopy.distance import geodesic

# Load environment variables
load_dotenv()

# Import configuration
from config import get_config

# Initialize Flask app
app = Flask(__name__)

# Load configuration from config.py based on environment
config_obj = get_config()
app.config.from_object(config_obj)

# Set secret key from environment or config
app.secret_key = os.getenv("SECRET_KEY", config_obj.SECRET_KEY)

# SQLAlchemy ORM setup
app.config["SQLALCHEMY_DATABASE_URI"] = config_obj.get_database_url()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Import models and initialize db
from models import (
    db, User, Role, Department, Team, QuestionPool, Question,
    Survey, SurveyQuestion, SurveyResponse, SurveyAnswer,
    ChecklistTemplate, ChecklistItem, ChecklistAssignment, ChecklistSubmission,
    ChecklistItemResponse, UserLocation, LocationZone, Notification, Message,
    AuditLog, OrganizationHistory
)
from encryption import hash_password, verify_password

# Initialize db with app
db.init_app(app)

# Initialize Flask-Migrate for database migrations
from flask_migrate import Migrate
migrate = Migrate(app, db)

# Print database connection info for debugging (remove in production)
if app.config['DEBUG']:
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Database: {config_obj.DB_NAME}")
    print(f"Host: {config_obj.DB_HOST}:{config_obj.DB_PORT}")


@app.route("/")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user by username or company_number
        user = User.query.filter(
            or_(User.username == username, User.company_number == username),
            User.is_deleted == False,
            User.is_active == True
        ).first()
        
        if not user or not verify_password(password, user.password_hash):
            flash("An error has occurred. Make sure your login credentials are correct", "error")
            return redirect(url_for('login'))
        
        # Store user info in session
        session["user"] = {
            'id': user.id,
            'username': user.username,
            'company_number': user.company_number,
            'name': user.full_name or user.username,
            'role': user.role.name,
            'role_id': user.role_id,
            # 'role_level': user.role.level,  # Removed: no longer used
            'department_id': user.department_id,
            'team_id': user.team_id
        }
        
        # Update last login
        user.last_login = datetime.utcnow()
        user.last_activity = datetime.utcnow()
        db.session.commit()
        
        # Redirect based on role
        role_name = user.role.name
        if role_name == 'super_admin':
            return redirect(url_for("register"))
        elif role_name == 'admin':
            return redirect(url_for('admin_create_checklist'))
        elif role_name == 'department_head':
            return redirect(url_for('master_add'))
        elif role_name == 'operator':
            return redirect(url_for('operator'))
        else:
            return redirect(url_for('admin_create_checklist'))

    return render_template('index.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return render_template("index.html")


@app.route('/master_add',methods=['GET','POST'])
def master_add():
    if is_logged_out():
        return redirect(url_for('login'))
    user=session['user']
    
    # Get all administrators (admin role level 60 and above)
    admin_roles = Role.query.all()
    admin_role_ids = [r.id for r in admin_roles]
    administrator = User.query.filter(
        User.role_id.in_(admin_role_ids),
        User.is_deleted == False
    ).all()
    
    # Get all plant sections (departments)
    plant_section = Department.query.filter_by(
        is_deleted=False,
        is_active=True
    ).order_by(Department.name).all()
    
    if request.method=='POST':
        selected_admins = request.form.getlist("selected_admins[]")
        section = request.form.get("section")
        if section:
            # Get or create department
            department = Department.query.filter_by(name=section).first()
            if not department:
                department = Department(
                    name=section,
                    code=section.upper().replace(' ', '_')[:50],
                    # level removed
                    is_active=True
                )
                db.session.add(department)
                db.session.flush()
            
            for admins in selected_admins:
                admin_id=admins.split(",")[0]
                admin=admins.split(",")[1]
                
                # Check if selected admin exists
                admin_user = User.query.filter_by(
                    id=admin_id,
                    is_deleted=False
                ).first()
                
                if admin_user:
                    # Check if admin already assigned to this department
                    if admin_user.department_id == department.id:
                        flash(f"{admin} already exists in this plant section")
                    else:
                        # Assign admin to department
                        admin_user.department_id = department.id
                        db.session.commit()
                        flash("Administrator added successfully", "success")
        else:
            flash("please select section before you add Administrator")
    return render_template('masterAdmin_addAdmin.html',administrator=administrator,plant_section=plant_section,user=user)

@app.route('/master_remove',methods=['GET','POST'])
def master_remove():

    if is_logged_out():
        return redirect(url_for('login'))
    user=session['user']
    
    # Get all administrators (admin role level 60 and above)
    admin_roles = Role.query.all()
    admin_role_ids = [r.id for r in admin_roles]
    administrator = User.query.filter(
        User.role_id.in_(admin_role_ids),
        User.is_deleted == False
    ).all()
    
    # Get all plant sections (departments)
    plant_section = Department.query.filter_by(
        is_deleted=False,
        is_active=True
    ).order_by(Department.name).all()
    
    if request.method=='POST':
        selected_admins = request.form.getlist("selected_admins[]")
       
        section = request.form.get("section")
        if section:
            # Get department
            department = Department.query.filter_by(name=section).first()
            if department:
                for admins in selected_admins:
                    print(admins.split(",")[0])
                    admin_id=admins.split(",")[0]
                    
                    # Find admin user
                    admin_user = User.query.filter_by(
                        id=admin_id,
                        department_id=department.id,
                        is_deleted=False
                    ).first()
                    
                    if admin_user:
                        print("deleted",admin_user)
                        # Remove department assignment
                        admin_user.department_id = None
                        db.session.commit()
                        flash("You have successfully removed this Administrator", "success")
                        return render_template('masterAdmin_removeAdmin.html',administrator=administrator,plant_section=plant_section,user=user)
                    else:
                        flash(f"This admin does not exists in this plant section")
                        return render_template('masterAdmin_removeAdmin.html',administrator=administrator,plant_section=plant_section,user=user)
        else:
            flash("please select section before you remove administrator","error")
    return render_template('masterAdmin_removeAdmin.html',administrator=administrator,plant_section=plant_section,user=user)

@app.route('/master_view',methods=['GET','POST'])
def master_view():

    if is_logged_out():
        return redirect(url_for('login'))
    user=session['user']
    
    # Get all administrators with their department assignments
    admin_roles = Role.query.all()
    admin_role_ids = [r.id for r in admin_roles]
    administrator = db.session.query(User).join(
        Department, User.department_id == Department.id, isouter=True
    ).filter(
        User.role_id.in_(admin_role_ids),
        User.is_deleted == False
    ).all()
    
    # Convert to list of dicts for template compatibility
    admin_list = []
    for admin in administrator:
        admin_dict = {
            'id': admin.id,
            'admin': f"{admin.company_number}-{admin.username}",
            'company_number': admin.company_number,
            'username': admin.username,
            'plant_section': admin.department.name if admin.department else None
        }
        admin_list.append(admin_dict)
    
    plant_section = Department.query.filter_by(
        is_deleted=False,
        is_active=True
    ).order_by(Department.name).all()

    if request.method=='POST':
        section = request.form.get("section")
        
        # Get department
        department = Department.query.filter_by(name=section).first()
        if department:
            administrators = User.query.filter_by(
                department_id=department.id,
                is_deleted=False
            ).filter(
                User.role_id.in_(admin_role_ids)
            ).all()
            
            # Convert to list of dicts
            admin_list = []
            for admin in administrators:
                admin_dict = {
                    'id': admin.id,
                    'admin': f"{admin.company_number}-{admin.username}",
                    'company_number': admin.company_number,
                    'username': admin.username,
                    'plant_section': section
                }
                admin_list.append(admin_dict)
            
            return render_template('masterAdmin_viewAdmin.html',administrator=admin_list,plant_section=plant_section,user=user)
    return render_template('masterAdmin_viewAdmin.html',administrator=admin_list,plant_section=plant_section,user=user)


@app.route('/admin_create_question',methods=['GET','POST'])
def admin_create_question():

    if is_logged_out():
        return redirect(url_for('login'))
    
    user=session['user']
    plant_sections=[]
    
    # Get current user
    current_user = User.query.get(user['id'])
    if not current_user or not current_user.department:
        flash("you are currently not assigned to any plant section")
        return redirect(url_for('login'))
    
    # Get all departments this admin can access
    # For now, just use their assigned department
    plant_sections.append(current_user.department.name)
    
    if request.method=="POST":
        
        section = request.form.get("section")
        question = request.form.get("question")
        question_type = request.form.get("question_type")
        options = request.form.getlist("options[]")
        reasoning = request.form.get("reasoning")
        
        if not section:
            flash("please select plant section you want to add question to")
            return redirect(url_for("admin_create_question"))
        else:
            # Check if question exists
            department = Department.query.filter_by(name=section).first()
            if department:
                exists = db.session.query(Question).join(
                    QuestionPool
                ).filter(
                    QuestionPool.department_id == department.id,
                    Question.question_text == question,
                    Question.is_deleted == False
                ).first()
                
                if not exists:
                    # Get or create question pool
                    pool = QuestionPool.query.filter_by(
                        department_id=department.id,
                        is_deleted=False
                    ).first()
                    
                    if not pool:
                        pool = QuestionPool(
                            name=f"{section} Questions",
                            department_id=department.id,
                            created_by_id=user['id'],
                            is_active=True
                        )
                        db.session.add(pool)
                        db.session.flush()
                    
                    # Create question
                    new_question = Question(
                        pool_id=pool.id,
                        question_text=question,
                        question_type=question_type or 'text',
                        options=json.dumps(options) if options else None,
                        custom_fields={'reasoning': reasoning} if reasoning else {},
                        is_required=False,
                        is_active=True
                    )
                    db.session.add(new_question)
                    db.session.commit()
                    
                    flash("Your question is successfully created", "success")
                else:
                    flash("this question already exists")
            else:
                flash("Department not found")
    
    return render_template('admin_create_questions.html',plant_sections=plant_sections,user=user)


@app.route('/admin_delete_question',methods=["GET","POST"])
def admin_delete_question():
    
    if is_logged_out():
        return redirect(url_for('login'))

    user=session['user']
    plant_sections=[]
    questions=[]
    
    # Get current user
    current_user = User.query.get(user['id'])
    if not current_user or not current_user.department:
        flash("you are currently not assigned to any plant section")
        return redirect(url_for('login'))
    
    # Get department
    department = current_user.department
    plant_sections.append(department.name)
    
    # Get all questions for this department
    questions_query = db.session.query(Question).join(
        QuestionPool
    ).filter(
        QuestionPool.department_id == department.id,
        Question.is_deleted == False,
        Question.is_active == True
    ).order_by(Question.order_index).all()
    
    # Convert to dicts for template
    questions = [{
        'id': q.id,
        'question': q.question_text,
        'question_text': q.question_text,
        'type': q.question_type,
        'options': json.loads(q.options) if q.options else [],
        'plant_section': department.name
    } for q in questions_query]
            
    if request.method=="POST":
        if request.is_json:
            data = request.get_json()
            selected_section = data.get('section')
            
            # Filter questions based on the selected section
            selected_dept = Department.query.filter_by(name=selected_section).first()
            if selected_dept:
                filtered_questions = db.session.query(Question).join(
                    QuestionPool
                ).filter(
                    QuestionPool.department_id == selected_dept.id,
                    Question.is_deleted == False
                ).all()
                
                filtered_section = [{
                    'id': q.id,
                    'question': q.question_text,
                    'question_text': q.question_text,
                    'type': q.question_type,
                    'options': json.loads(q.options) if q.options else [],
                    'plant_section': selected_section
                } for q in filtered_questions]
                
                print("filter ",filtered_section)
                questions=filtered_section                      
                # Return filtered questions as JSON
                return jsonify({
                    "message": "Section received",
                    "section": selected_section,
                    "filtered_section": filtered_section
                })
        else:
            question_ids = request.form.getlist("question_ids[]")
            print("list od question_ids ",question_ids)
            if question_ids:
                for id in question_ids:
                    # Soft delete the selected questions
                    question = Question.query.get(id)
                    if question:
                        question.is_deleted = True
                        question.deleted_at = datetime.utcnow()
                        db.session.commit()
                        flash("Question successfully deleted", "success")
                return redirect(url_for('admin_delete_question'))
    return render_template('admin_delete_questions.html',questions=questions,plant_sections=plant_sections,user=user)


@app.route('/admin_edit_question',methods=['POST','GET'])
def admin_edit_question():

    if is_logged_out():
        return redirect(url_for('login'))
    
    user=session['user']
    plant_sections=[]
    questions=[]
    
    # Get current user
    current_user = User.query.get(user['id'])
    if not current_user or not current_user.department:
        flash("you are currently not assigned to any plant section")
        return redirect(url_for('login'))
    
    # Get department
    department = current_user.department
    plant_sections.append(department.name)
    
    # Get all questions for this department
    questions_query = db.session.query(Question).join(
        QuestionPool
    ).filter(
        QuestionPool.department_id == department.id,
        Question.is_deleted == False
    ).order_by(Question.order_index).all()
    
    # Convert to dicts for template
    questions = [{
        'id': q.id,
        'question': q.question_text,
        'question_text': q.question_text,
        'type': q.question_type,
        'options': json.loads(q.options) if q.options else [],
        'plant_section': department.name
    } for q in questions_query]

    if request.method=="POST":
        if request.is_json:
            data = request.get_json()
            selected_section = data.get('section')
            
            # Filter questions based on the selected section
            selected_dept = Department.query.filter_by(name=selected_section).first()
            if selected_dept:
                filtered_questions = db.session.query(Question).join(
                    QuestionPool
                ).filter(
                    QuestionPool.department_id == selected_dept.id,
                    Question.is_deleted == False
                ).all()
                
                filtered_section = [{
                    'id': q.id,
                    'question': q.question_text,
                    'question_text': q.question_text,
                    'type': q.question_type,
                    'options': json.loads(q.options) if q.options else [],
                    'plant_section': selected_section
                } for q in filtered_questions]
            else:
                filtered_section = []
      
            print("filter ",filtered_section)
            questions=filtered_section
            # Return filtered questions as JSON
            return jsonify({
                "message": "Section received",
                "section": selected_section,
                "filtered_section": filtered_section
            })
        else:
            question_id = request.form.get("question_id")
            print("this id ",question_id)
            
            # Get question by ID
            question_obj = Question.query.get(question_id)
            if question_obj:
                question = {
                    'id': question_obj.id,
                    'question': question_obj.question_text,
                    'question_text': question_obj.question_text,
                    'type': question_obj.question_type,
                    'options': json.loads(question_obj.options) if question_obj.options else [],
                    'reasoning': question_obj.custom_fields.get('reasoning') if question_obj.custom_fields else None
                }
            else:
                question = None
            
            print("question ",question)
            return render_template('admin_modify_question.html',question=question,plant_sections=plant_sections,user=user)
    
    return render_template('admin_edit_question.html',questions=questions,plant_sections=plant_sections,user=user)

@app.route('/admin_modify_question/<id>',methods=["GET","POST"])
def admin_modify_question(id):
    print("id ",id)
    if is_logged_out():
        return redirect(url_for('login'))
    user=session['user']
    if request.method=="POST":
       
        question_text = request.form.get("question")
        question_type = request.form.get("question_type")
        options = request.form.getlist("options[]")
        reasoning = request.form.get("reasoning")
        
        # Update question using SQLAlchemy
        question_obj = Question.query.get(id)
        if question_obj:
            question_obj.question_text = question_text
            question_obj.question_type = question_type
            question_obj.options = json.dumps(options) if options else None
            
            # Update custom fields
            custom_fields = question_obj.custom_fields or {}
            if reasoning:
                custom_fields['reasoning'] = reasoning
            question_obj.custom_fields = custom_fields
            
            question_obj.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash("Question successfully updated", "success")
        else:
            flash("Question not found", "error")
        
        return redirect(url_for("admin_edit_question"))
    return render_template('admin_modify_question.html',user=user)


@app.route('/admin_create_checklist', methods=['GET', 'POST'])
def admin_create_checklist():

    if is_logged_out():
        return redirect(url_for('login'))
    
    user=session['user']
    print(user)
    plant_sections=[]
    questions=[]
    
    # Get all operators
    operator_role = Role.query.filter_by(name='operator').first()
    if operator_role:
        operators = User.query.filter_by(
            role_id=operator_role.id,
            is_deleted=False
        ).all()
    else:
        operators = []
    
    # Get current user
    current_user = User.query.get(user["id"])
    if not current_user or not current_user.department:
        flash("you are currently not assigned to any plant section")
        return redirect(url_for('login'))
    
    # Get department
    department = current_user.department
    plant_sections.append(department.name)
    
    # Get questions for this department
    questions_query = db.session.query(Question).join(
        QuestionPool
    ).filter(
        QuestionPool.department_id == department.id,
        Question.is_deleted == False
    ).order_by(Question.order_index).all()
    
    questions = [{
        'id': q.id,
        'question': q.question_text,
        'type': q.question_type,
        'options': json.loads(q.options) if q.options else []
    } for q in questions_query]
    
    # Get count of active checklist assignments
    count_num = ChecklistAssignment.query.filter_by(
        is_deleted=False
    ).count()
    
    # Get existing checklist assignments for display
    count = ChecklistAssignment.query.filter_by(
        is_deleted=False
    ).all()
    
    count_list = []
    for assignment in count:
        items = ChecklistItem.query.filter_by(
            template_id=assignment.template_id,
            is_active=True
        ).order_by(ChecklistItem.order_index).all()
        
        checklist_questions = [{
            'id': item.id,
            'question': item.title,
            'description': item.description
        } for item in items]
        
        count_list.append({
            'id': assignment.id,
            'checklist_questions': checklist_questions
        })
   

    if request.method == "POST":
        # Check if the request contains JSON data
        if request.is_json:
            data = request.get_json()
            selected_section = data.get('section')
            
            # Filter questions based on the selected section
            selected_dept = Department.query.filter_by(name=selected_section).first()
            if selected_dept:
                filtered_questions = db.session.query(Question).join(
                    QuestionPool
                ).filter(
                    QuestionPool.department_id == selected_dept.id,
                    Question.is_deleted == False
                ).all()
                
                filtered_section = [{
                    'id': q.id,
                    'question': q.question_text,
                    'type': q.question_type,
                    'options': json.loads(q.options) if q.options else []
                } for q in filtered_questions]
            else:
                filtered_section = []
      
            print("filter ",filtered_section)
            # Return filtered questions as JSON
            return jsonify({
                "message": "Section received",
                "section": selected_section,
                "filtered_section": filtered_section
            })
        
        # Handle form submission
        else:
            section = request.form.get("section")
            print("section ",section)
            select = request.form.get("select")
            print("selected plant ", select)
            
            # Get locations for this section
            dept = Department.query.filter_by(name=section).first()
            if dept:
                location_zones = LocationZone.query.filter_by(
                    department_id=dept.id,
                    is_active=True
                ).all()
                
                location = [{
                    'latitude': lz.center_latitude,
                    'longitude': lz.center_longitude,
                    'range': lz.radius_meters
                } for lz in location_zones]
            else:
                location = []
            
            print("location ",location)
            Checked_questions=request.form.getlist("question_id[]")
            operators_questions=[]
            if Checked_questions:
                for id in Checked_questions:
                    q = Question.query.get(id)
                    if q:
                        operators_questions.append({
                            'id': q.id,
                            'question': q.question_text,
                            'type': q.question_type,
                            'options': json.loads(q.options) if q.options else []
                        })

                for option in operators_questions:
                    if option.get('options') and len(option['options']) > 0:
                        if isinstance(option['options'][0], str):
                            item=option['options'][0].split(",")
                            option['options'][0]=[i for i in item]
               
                latitute_longitude=[]
                for item in location:
                    lat_lon={"latitude":item['latitude'],"longitude":item['longitude'],"range":item['range']}
                    latitute_longitude.append(lat_lon)
                
                # Get operator
                operator_user = User.query.get(select)
                if operator_user:
                    operator = [{
                        'company_number': operator_user.company_number,
                        'name': operator_user.full_name or operator_user.username
                    }]
                else:
                    operator = []
                
                print(latitute_longitude)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if len(operators_questions)>0:
                   
                    print("count ", count_num)
                    
                    if count_num < 2:
                        # Create checklist template
                        template = ChecklistTemplate(
                            name=f"{section} Checklist - {timestamp}",
                            department_id=dept.id if dept else None,
                            created_by_id=user['id'],
                            is_active=True
                        )
                        db.session.add(template)
                        db.session.flush()
                        
                        # Add items to template
                        for idx, q in enumerate(operators_questions):
                            item = ChecklistItem(
                                template_id=template.id,
                                title=q['question'],
                                item_type='question',
                                order_index=idx,
                                is_required=True,
                                is_active=True
                            )
                            db.session.add(item)
                        
                        # Create assignment
                        assignment = ChecklistAssignment(
                            template_id=template.id,
                            assigned_to_user_id=operator_user.id if operator_user else None,
                            assigned_by_id=user['id'],
                            status='pending',
                            custom_fields={'location': latitute_longitude}
                        )
                        db.session.add(assignment)
                        db.session.commit()
                        
                        flash("checklist was created Successfully")
                    else:
                        flash("you cannot create more checklist, please upgrade your subscription")
                else:
                    flash("please choose atleast one or more questions")
            # Process the form data (e.g., save to database)
            return redirect(url_for("admin_create_checklist"))
   
    # Render the template for GET requests
    return render_template('admin_create_checklist.html',user=user,count=count_list, operators=operators, questions=questions,plant_sections=plant_sections)

@app.route("/delete_checklist/<id>",methods=["GET","POST"])
def delete_checklist(id):
    # Soft delete checklist assignment
    assignment = ChecklistAssignment.query.get(id)
    if assignment:
        assignment.is_deleted = True
        assignment.deleted_at = datetime.utcnow()
        db.session.commit()
        flash("checklist deleted succeesfully")
    else:
        flash("Checklist not found")
    return redirect(url_for("register"))

@app.route('/admin_view_answers', methods=['GET', 'POST'])
def admin_view_answers():

    if is_logged_out():
        return redirect(url_for('login'))

    # Get all plant sections (departments)
    plant_sections = Department.query.filter_by(
        is_deleted=False,
        is_active=True
    ).order_by(Department.name).all()

    if request.method == "POST":
        selected_section = request.form.get('section')
        if selected_section:
            # Filter answers based on the selected section
            dept = Department.query.filter_by(name=selected_section).first()
            if dept:
                submissions = ChecklistSubmission.query.filter_by(
                    department_id_at_submission=dept.id,
                    status='completed'
                ).order_by(ChecklistSubmission.submission_date.desc()).all()
            else:
                submissions = []
            print("if ",submissions)
        else:
            # If no section is selected, return all answers
            submissions = ChecklistSubmission.query.filter_by(
                status='completed'
            ).order_by(ChecklistSubmission.submission_date.desc()).all()
            print("else ",submissions)
        
        # Convert to dict format
        answers = [{
            'id': s.id,
            'company_number': s.user.company_number if s.user else None,
            'name': s.user.full_name if s.user else None,
            'plant_section': s.department_at_submission.name if s.department_at_submission else None,
            'checklist_answers': s.custom_fields.get('answers', []) if s.custom_fields else [],
            'location': s.custom_fields.get('location', []) if s.custom_fields else [],
            'submission_date': s.submission_date.strftime('%Y-%m-%d %H:%M:%S') if s.submission_date else None
        } for s in submissions]
        
        # Return the filtered answers and plant sections to the template
        return render_template("admin_view_answers.html", answers=answers, plant_sections=plant_sections)

    # For GET requests, return all answers
    submissions = ChecklistSubmission.query.filter_by(
        status='completed'
    ).order_by(ChecklistSubmission.submission_date.desc()).all()
    print("default ",submissions)
    
    answers = []
    checklist_answers=[]
    for s in submissions:
        answer_data = {
            'id': s.id,
            'company_number': s.user.company_number if s.user else None,
            'name': s.user.full_name if s.user else None,
            'plant_section': s.department_at_submission.name if s.department_at_submission else None,
            'checklist_answers': s.custom_fields.get('answers', []) if s.custom_fields else [],
            'location': s.custom_fields.get('location', []) if s.custom_fields else [],
            'submission_date': s.submission_date.strftime('%Y-%m-%d %H:%M:%S') if s.submission_date else None
        }
        answers.append(answer_data)
        print("debug item",answer_data['checklist_answers'])
        ans=json.dumps(answer_data['checklist_answers'])
        checklist_answers.append(ans)
    print("final ",checklist_answers)
    return render_template("admin_view_answers.html",checklist_answers=checklist_answers ,answers=answers, plant_sections=plant_sections)




@app.route('/admin_view_unanswered_questions',methods=['GET','POST'])
def admin_view_unanswered_questions():

    if is_logged_out():
        return redirect(url_for('login'))
    
    return render_template("admin_view_unanswered_questions.html")

@app.route('/api/filtered_answered_questions/<plant_section>', methods=['GET'])
def get_answered_questions(plant_section):

    # if is_logged_out():
    #     return redirect(url_for('login'))

    plant_section = plant_section.upper().strip()
    print("section ",plant_section)
    if not plant_section:
        return jsonify({"error": "plant_section parameter is required"}), 400

    # Get department
    dept = Department.query.filter_by(name=plant_section).first()
    if dept:
        submissions = ChecklistSubmission.query.filter_by(
            department_id_at_submission=dept.id,
            status='completed'
        ).order_by(ChecklistSubmission.submission_date.desc()).all()
    else:
        submissions = []
    
    results = []
    for s in submissions:
        result_item = {
            'id': s.id,
            'company_number': s.user.company_number if s.user else None,
            'name': s.user.full_name if s.user else None,
            'plant_section': plant_section,
            'location': s.custom_fields.get('location', []) if s.custom_fields else [],
            'checklist_answers': s.custom_fields.get('answers', []) if s.custom_fields else [],
            'submission_date': s.submission_date.strftime('%Y-%m-%d %H:%M:%S') if s.submission_date else None
        }
        print(type(result_item['location']))
        results.append(result_item)
    
    print(results)
    return jsonify(results)


@app.route('/api/all_answered_questions', methods=['GET'])
def all_answered_questions():

    # if is_logged_out():
    #     return redirect(url_for('login'))

    submissions = ChecklistSubmission.query.filter_by(
        status='completed'
    ).order_by(ChecklistSubmission.submission_date.desc()).all()
    
    results = []
    for s in submissions:
        result_item = {
            'id': s.id,
            'company_number': s.user.company_number if s.user else None,
            'name': s.user.full_name if s.user else None,
            'plant_section': s.department_at_submission.name if s.department_at_submission else None,
            'location': s.custom_fields.get('location', []) if s.custom_fields else [],
            'checklist_answers': s.custom_fields.get('answers', []) if s.custom_fields else [],
            'submission_date': s.submission_date.strftime('%Y-%m-%d %H:%M:%S') if s.submission_date else None
        }
        print(type(result_item['location']))
        results.append(result_item)
    
    print("answers --",results)
    return jsonify(results)

@app.route('/operator', methods=["GET", "POST"])
def operator():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    # Get user's checklist assignments
    current_user = User.query.filter_by(
        company_number=user['company_number'],
        is_deleted=False
    ).first()
    
    if not current_user:
        return redirect(url_for('login'))
    
    # Get active assignments for this user
    assignments = ChecklistAssignment.query.filter(
        or_(
            ChecklistAssignment.assigned_to_user_id == current_user.id,
            ChecklistAssignment.assigned_to_team_id == current_user.team_id
        ),
        ChecklistAssignment.status.in_(['pending', 'in_progress']),
        ChecklistAssignment.is_deleted == False
    ).all()
    
    questions = []
    for assignment in assignments:
        # Get checklist items
        items = ChecklistItem.query.filter_by(
            template_id=assignment.template_id,
            is_active=True
        ).order_by(ChecklistItem.order_index).all()
        
        checklist_questions = [{
            'id': item.id,
            'question': item.title,
            'description': item.description
        } for item in items]
        
        questions.append({
            'id': assignment.id,
            'checklist_questions': json.dumps(checklist_questions),
            'location': json.dumps(assignment.custom_fields.get('location', [])) if assignment.custom_fields else '[]'
        })
    
    if request.method == 'POST':
        user_data = request.json
        user_lat = user_data.get('latitude')
        user_lon = user_data.get('longitude')
        user_answers = user_data.get('answers_with_questions', None)

        if not questions:
            return jsonify({'status': 'error', 'message': 'No checklist questions found'})
        
        print("questions ", questions)
        location = json.loads(questions[0]['location'])[0] if questions[0]['location'] else {}
        is_within = is_within_range(
            str(user_lat), str(user_lon),
            location.get('latitude', '0'), location.get('longitude', '0'),
            location.get('range', '0')
        )
        response_data = {
            'status': 'success',
            'is_within_range': is_within,
        }
        print("response data ",response_data)
        checklist_id = questions[0]['id']

        if user_answers is not None:
            if is_within:
                # Store answers
                assignment = ChecklistAssignment.query.get(checklist_id)
                if assignment:
                    submission = ChecklistSubmission(
                        assignment_id=assignment.id,
                        user_id=current_user.id,
                        department_id_at_submission=current_user.department_id,
                        team_id_at_submission=current_user.team_id,
                        status='completed',
                        custom_fields={'answers': user_answers, 'location': {'latitude': user_lat, 'longitude': user_lon}}
                    )
                    db.session.add(submission)
                    
                    # Update assignment
                    assignment.status = 'completed'
                    assignment.completed_date = datetime.utcnow()
                    db.session.commit()
                    
                    output = True
                else:
                    output = False
                
                response_data['message'] = 'Checklist submitted successfully' if output else 'Error submitting checklist'
                response_data['status'] = 'success' if output else 'error'
            else:
                response_data['message'] = 'User not within the required location'
        else:
            if is_within:
                response_data['operators_questions'] = json.loads(questions[0]['checklist_questions'])
        print("FINAL RESPONSE:", response_data)

        return jsonify(response_data)

    # Initial page load
    return render_template('operator.html', operators_questions=[], user=user)


@app.route("/submit_location", methods=["GET", "POST"])
def submit_location():
    if is_logged_out():
        return redirect(url_for('login'))

    user = session['user']
    
    # Get all location zones
    locations = LocationZone.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        plant_section = request.form["plant_section"]
        latitude = request.form["latitude"]
        longitude = request.form["longitude"]
        range_meters = request.form["range"]
        
        # Get or create department
        department = Department.query.filter_by(name=plant_section.upper()).first()
        if not department:
            department = Department(
                name=plant_section.upper(),
                code=plant_section.upper().replace(' ', '_')[:50],
                level=1,
                is_active=True
            )
            db.session.add(department)
            db.session.flush()
        
        # Create location zone
        location_zone = LocationZone(
            name=f"{plant_section.upper()} Zone",
            zone_type='circle',
            center_latitude=float(latitude),
            center_longitude=float(longitude),
            radius_meters=float(range_meters),
            department_id=department.id,
            is_active=True
        )
        
        db.session.add(location_zone)
        db.session.commit()
        
        flash("Location successfully saved")
        return redirect(url_for("submit_location"))
    
    return render_template("superAdmin_location_update.html", locations=locations, user=user)


@app.route('/delete_location/<plant_section>', methods=['GET', 'POST'])
def delete_location(plant_section):
    if is_logged_out():
        return redirect(url_for('login'))

    # Find and delete location zones for this department
    department = Department.query.filter_by(name=plant_section).first()
    if department:
        LocationZone.query.filter_by(department_id=department.id).delete()
        
        # Delete unanswered checklist assignments for this department
        ChecklistAssignment.query.filter(
            ChecklistAssignment.template.has(department_id=department.id),
            ChecklistAssignment.status == 'pending'
        ).delete(synchronize_session=False)
        
        db.session.commit()
        flash("Location deleted from your repository", "success")
    else:
        flash("Location not found", "error")

    return redirect(url_for('submit_location'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_out():
        return redirect(url_for('login'))
    
    user = session['user']
    
    # Get all users with admin or higher roles
    admin_roles = Role.query.all()
    admin_role_ids = [r.id for r in admin_roles]
    
    admins = User.query.filter(
        User.role_id.in_(admin_role_ids),
        User.is_deleted == False
    ).all()
    
    # Get all users
    users = User.query.filter(User.is_deleted == False).all()
    
    # Get all active roles with user counts for hierarchy display
    roles_with_counts = db.session.query(
        Role,
        db.func.count(User.id).label('user_count')
    ).outerjoin(User, and_(User.role_id == Role.id, User.is_deleted == False)).filter(
        Role.is_active == True
    ).group_by(Role.id).all()
    
    available_roles = []
    for role, user_count in roles_with_counts:
        role_dict = {
            'id': role.id,
            'name': role.name,
            'display_name': role.display_name,
            'description': role.description,
            # 'level': role.level, (removed)
            'parent_role_id': role.parent_role_id,
            'is_active': role.is_active,
            'is_system_role': role.is_system_role,
            'user_count': user_count
        }
        available_roles.append(role_dict)
    
    # Get department assignments (users with departments)
    administrators = db.session.query(
        User, Department
    ).join(Department, User.department_id == Department.id).filter(
        User.is_deleted == False,
        Department.is_deleted == False
    ).all()
    
    # Get checklist assignments count
    count = ChecklistAssignment.query.filter(
        ChecklistAssignment.is_deleted == False
    ).all()
    
    if request.method == 'POST':
        company_number = request.form.get('company_number')
        username = request.form.get('username')
        password = request.form.get('password')
        role_name = request.form.get('role')
        
        # Check if user exists
        existing_user = User.query.filter(
            or_(User.username == username.upper(), User.company_number == company_number.upper()),
            User.is_deleted == False
        ).first()
        
        if existing_user:
            flash("This user already exists")
        else:
            # Get role
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role.query.filter_by(name='operator').first()
            
            # Create new user
            new_user = User(
                username=username.upper().strip(),
                company_number=company_number.upper(),
                password_hash=hash_password(password.strip()),
                full_name=username.upper().strip(),
                role_id=role.id,
                is_active=True,
                is_verified=True
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Create audit log
            audit = AuditLog(
                user_id=user['id'],
                action='create_user',
                entity_type='user',
                entity_id=new_user.id,
                description=f"Created new user: {new_user.username}",
                new_values={'username': new_user.username, 'role': role.name},
                success=True
            )
            db.session.add(audit)
            db.session.commit()
            
            flash("User registered successfully")
            return redirect(url_for("register"))
    
    return render_template('superAdmin.html', count=count, users=users, user=user, admins=admins, administrator=administrators, available_roles=available_roles)




@app.route('/delete_assigned_section/<int:id>', methods=['GET', 'POST'])
def delete_assigned_section(id):
    if is_logged_out():
        return redirect(url_for('login'))
    
    # Soft delete user's department assignment
    user = User.query.get(id)
    if user:
        user.department_id = None
        user.team_id = None
        db.session.commit()
        flash("Assignment removed")
    else:
        flash("User not found", "error")
    
    return redirect(url_for('register'))

@app.route('/delete_user/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    if is_logged_out():
        return redirect(url_for('login'))
    
    user = User.query.get(id)
    if user:
        # Soft delete
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        user.deleted_by = session['user']['id']
        
        db.session.commit()
        
        # Create audit log
        audit = AuditLog(
            user_id=session['user']['id'],
            action='delete_user',
            entity_type='user',
            entity_id=id,
            description=f"Deleted user: {user.username}",
            old_values={'username': user.username, 'company_number': user.company_number},
            success=True
        )
        db.session.add(audit)
        db.session.commit()
        
        flash("User deleted successfully")
    else:
        flash("User not found", "error")
    
    return redirect(url_for('register'))


def is_within_range(user_lat, user_lon, target_lat, target_lon, range_meters):
    """
    Check if the user's location is within the specified range of the target location.
    """
    user_location = (float(user_lat), float(user_lon))
    target_location = (float(target_lat), float(target_lon))
    distance = geodesic(user_location, target_location).meters
    return distance <= float(range_meters)

@app.route('/getlocation', methods=['POST', 'GET'])
def getlocation():
    return render_template("getlocation.html")

def is_logged_out():
   
    if not session.get('user'):
        return True


# ============================================================================
# SUPER ADMIN - ROLE MANAGEMENT ROUTES
# ============================================================================

@app.route('/superadmin/manage_users', methods=['GET'])
def manage_users():
    """View and manage all users in the system"""
    if is_logged_out():
        return redirect(url_for('login'))
    
    user = session['user']
    current_user = User.query.get(user['id'])
    
    
    # Get all users with their roles and departments
    users = db.session.query(User).join(
        Role, User.role_id == Role.id
    ).outerjoin(
        Department, User.department_id == Department.id
    ).filter(
        User.is_deleted == False
    ).order_by(User.created_at.desc()).all()
    
    # Get all roles for dropdowns
    roles = Role.query.filter_by(is_deleted=False).all()
    
    # Get all departments for dropdowns
    departments = Department.query.filter_by(is_deleted=False).order_by(Department.name).all()
    
    users_serialized = [u.to_dict() for u in users]
    return render_template('superAdmin_manage_users.html', 
                         users=users_serialized, 
                         roles=roles, 
                         departments=departments,
                         user=user)

@app.route('/superadmin/manage_roles', methods=['GET'])
def manage_roles():
    """View and manage all roles in the system"""
    if is_logged_out():
        return redirect(url_for('login'))
    
    user = session['user']
    current_user = User.query.get(user['id'])
    
    
    # Get all roles with user counts
    roles = db.session.query(
        Role,
        db.func.count(User.id).label('user_count')
    ).outerjoin(User, User.role_id == Role.id).group_by(Role.id).all()
    
    roles_list = []
    for role, user_count in roles:
        roles_list.append({
            'id': role.id,
            'name': role.name,
            'display_name': role.display_name,
            'description': role.description,
            # 'level': role.level, (removed)
            'parent_role_id': role.parent_role_id,
            'parent_role': role.parent_role.display_name if role.parent_role else None,
            'is_active': role.is_active,
            'is_system_role': role.is_system_role,
            'user_count': user_count,
            'permissions': role.permissions or {}
        })
    
    return render_template('superAdmin_manage_roles.html', roles=roles_list, all_roles=roles_list, user=user)


@app.route('/create_role', methods=['POST'])
def create_role():
    """Create a new role"""
    if is_logged_out():
        return redirect(url_for('login'))
    
    user = session['user']
    current_user = User.query.get(user['id'])

    
    try:
        name = request.form.get('name')
        display_name = request.form.get('display_name')
        description = request.form.get('description')
        # level removed
        parent_role_id = request.form.get('parent_role_id')
        
        # Check if role name already exists
        existing = Role.query.filter_by(name=name).first()
        if existing:
            flash(f"Role with name '{name}' already exists", "error")
            return redirect(url_for('manage_roles'))
        
        # Build permissions dict
        permissions_list = request.form.getlist('permissions[]')
        permissions = {
            'view_users': 'view_users' in permissions_list,
            'manage_users': 'manage_users' in permissions_list,
            'view_departments': 'view_departments' in permissions_list,
            'manage_departments': 'manage_departments' in permissions_list,
            'view_questions': 'view_questions' in permissions_list,
            'manage_questions': 'manage_questions' in permissions_list,
            'view_checklists': 'view_checklists' in permissions_list,
            'manage_checklists': 'manage_checklists' in permissions_list
        }
        
        # Create role
        new_role = Role(
            name=name,
            display_name=display_name,
            description=description,
            level=level,
            parent_role_id=int(parent_role_id) if parent_role_id else None,
            permissions=permissions,
            is_active=True,
            is_system_role=False
        )
        
        db.session.add(new_role)
        db.session.commit()
        
        # Create audit log
        audit = AuditLog(
            user_id=user['id'],
            action='create_role',
            target_type='Role',
            target_id=new_role.id,
            description=f"Created role: {display_name}",
            new_value={'name': name, 'display_name': display_name, 'level': level}
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f"Role '{display_name}' created successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating role: {str(e)}", "error")
    
    return redirect(url_for('manage_roles'))


@app.route('/update_role/<int:role_id>', methods=['POST'])
def update_role(role_id):
    """Update an existing role"""
    if is_logged_out():
        return redirect(url_for('login'))
    
    user = session['user']
    current_user = User.query.get(user['id'])
    
    # Only Super Admin can update roles
    if not current_user or not current_user.role:
        flash("Access denied. Super Admin only.", "error")
        return redirect(url_for('login'))
    
    try:
        role = Role.query.get(role_id)
        if not role:
            flash("Role not found", "error")
            return redirect(url_for('manage_roles'))
        
        # System roles can only be modified by super admins (level 100)
        # And they cannot change certain core attributes
        if role.is_system_role and user.get('role_level', 0) < 100:
            flash("Only Super Admins can modify system roles", "error")
            return redirect(url_for('manage_roles'))
        
        # Save old values for audit
        old_values = {
            'display_name': role.display_name,
            # 'level': role.level,  # Removed: no longer used
            'parent_role_id': role.parent_role_id,
            'is_active': role.is_active
        }
        
        # Update role
        role.display_name = request.form.get('display_name')
        role.description = request.form.get('description')
        # role.level = int(request.form.get('level', role.level))  # Removed: no longer used
        parent_role_id = request.form.get('parent_role_id')
        role.parent_role_id = int(parent_role_id) if parent_role_id else None
        role.is_active = bool(int(request.form.get('is_active', 1)))
        
        # Update permissions
        permissions_list = request.form.getlist('permissions[]')
        role.permissions = {
            'view_users': 'view_users' in permissions_list,
            'manage_users': 'manage_users' in permissions_list,
            'view_departments': 'view_departments' in permissions_list,
            'manage_departments': 'manage_departments' in permissions_list,
            'view_questions': 'view_questions' in permissions_list,
            'manage_questions': 'manage_questions' in permissions_list,
            'view_checklists': 'view_checklists' in permissions_list,
            'manage_checklists': 'manage_checklists' in permissions_list
        }
        
        db.session.commit()
        
        # Create audit log
        audit = AuditLog(
            user_id=user['id'],
            action='update_role',
            target_type='Role',
            target_id=role.id,
            description=f"Updated role: {role.display_name}",
            old_value=old_values,
            new_value={
                'display_name': role.display_name,
                # 'level': role.level,  # Removed: no longer used
                'parent_role_id': role.parent_role_id,
                'is_active': role.is_active
            }
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f"Role '{role.display_name}' updated successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating role: {str(e)}", "error")
    
    return redirect(url_for('manage_roles'))


@app.route('/delete_role/<int:role_id>', methods=['POST'])
def delete_role(role_id):
    """Delete a role (only if no users assigned)"""
    if is_logged_out():
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user = session['user']
    current_user = User.query.get(user['id'])
    
    # Only Super Admin can delete roles
    if not current_user or not current_user.role:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'success': False, 'message': 'Role not found'}), 404
        
        # Cannot delete system roles
        if role.is_system_role:
            return jsonify({'success': False, 'message': 'Cannot delete system roles'}), 400
        
        # Check if any users have this role
        user_count = User.query.filter_by(role_id=role_id, is_deleted=False).count()
        if user_count > 0:
            return jsonify({
                'success': False, 
                'message': f'Cannot delete role. {user_count} users still assigned to this role'
            }), 400
        
        # Check if any roles have this as parent
        child_roles = Role.query.filter_by(parent_role_id=role_id).count()
        if child_roles > 0:
            return jsonify({
                'success': False, 
                'message': f'Cannot delete role. {child_roles} child roles depend on this role'
            }), 400
        
        # Create audit log before deletion
        audit = AuditLog(
            user_id=user['id'],
            action='delete_role',
            target_type='Role',
            target_id=role.id,
            description=f"Deleted role: {role.display_name}",
            old_value={'name': role.name, 'display_name': role.display_name}  # Removed level
        )
        db.session.add(audit)
        
        # Delete role
        db.session.delete(role)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Role deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/role/<int:role_id>', methods=['GET'])
def get_role_details(role_id):
    """Get detailed information about a role"""
    if is_logged_out():
        return jsonify({'error': 'Not logged in'}), 401
    
    user = session['user']
    current_user = User.query.get(user['id'])
    
    # Only Super Admin can view role details
    if not current_user or not current_user.role:
        return jsonify({'error': 'Access denied'}), 403
    
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    
    # Get user count
    user_count = User.query.filter_by(role_id=role_id, is_deleted=False).count()
    
    # Get child roles count
    child_roles_count = Role.query.filter_by(parent_role_id=role_id).count()
    
    return jsonify({
        'id': role.id,
        'name': role.name,
        'display_name': role.display_name,
        'description': role.description,
        'level': role.level,
        'parent_role_id': role.parent_role_id,
        'parent_role': role.parent_role.display_name if role.parent_role else None,
        'is_active': role.is_active,
        'is_system_role': role.is_system_role,
        'permissions': role.permissions or {},
        'user_count': user_count,
        'child_roles_count': child_roles_count,
        'created_at': role.created_at.isoformat() if role.created_at else None,
        'updated_at': role.updated_at.isoformat() if role.updated_at else None
    })


if __name__ == '__main__':
    app.run(debug=True)
    # manager.run()