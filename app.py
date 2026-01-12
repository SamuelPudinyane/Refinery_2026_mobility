from flask import render_template,Flask,request,session,flash,redirect, url_for,jsonify
from dbqueries import (insert_registerd_user,get_db_connection,verify_user_credentials,get_all_administrators,insert_into_admin,
                       delete_from_admin,get_all_administrators_on_all_sections,get_all_administrators_on_particular_sections,
                       get_all_operators,insert_into_checklist_questions,get_all_questions,delete_selected_questions,get_one_question,
                       update_selected_questions,get_all_questions_on_particular_sections,get_all_questions_selected_questions,get_administrator_with_id_and_section,
                       get_administrator_with_id,insert_into_section_location,get_all_locations,get_all_plant_sections,get_all_plantsection_and_question,get_all_locations_by_plant_section,
                        get_operator_with_id,insert_question,get_all_questions_by_company_number,delete_from_super_admin,get_all_answered_questions_by_plant_section,
                        get_all_answered_questions,delete_all_unanswered_questions,store_answers,get_count_of_question,delete_checklist_questions,
                        delete_assined_sections,delete_assined_sections_by_section,user_exist_credentials,get_all_users,delete_the_user
                       )
from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from config import get_config

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load configuration from config.py based on environment
config_obj = get_config()
app.config.from_object(config_obj)

# Set secret key from environment or config
app.secret_key = os.getenv("SECRET_KEY", config_obj.SECRET_KEY)

# Optional: SQLAlchemy setup (uncomment if using SQLAlchemy ORM)
# app.config["SQLALCHEMY_DATABASE_URI"] = config_obj.get_database_url()
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# Print database connection info for debugging (remove in production)
if app.config['DEBUG']:
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Database: {config_obj.DB_NAME}")
    print(f"Host: {config_obj.DB_HOST}:{config_obj.DB_PORT}")


@app.route("/")
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        company_number=request.form.get('username')
        password=request.form.get('password')
        user=verify_user_credentials(company_number,password)
       
        session["user"]=user
        print("user ",session['user'])
        if not user:
            flash("An error has occurred. Make sure your login credentials are correct", "error")
            return redirect(url_for('login'))
        
        if user['role']=='master_administrator':
            return redirect(url_for('master_add'))
        
        elif user['role']=='administrator':
            return redirect(url_for('admin_create_checklist')) 
        
        elif user['role']=='operator':
            return redirect(url_for('operator'))
        
        elif user['role']=='superadmin':
            return redirect(url_for("register"))

    return render_template('index.html')

@app.route('/logout',methods=['GET','POST'])
def logout():
    session.clear()
    return render_template("index.html")


@app.route('/master_add',methods=['GET','POST'])
def master_add():
    if is_logged_out():
        return redirect(url_for('login'))
    user=session['user']
    administrator=get_all_administrators()
    plant_section=get_all_plant_sections()
    if request.method=='POST':
        selected_admins = request.form.getlist("selected_admins[]")
        section = request.form.get("section")
        if section:
            for admins in selected_admins:
                admin_id=admins.split(",")[0]
                admin=admins.split(",")[1]
                # check if selected admin exists in this plant section
                found_admin=get_administrator_with_id_and_section(admin_id,section)
                if not found_admin:
                    insert_into_admin(section, admin, admin_id)
                    flash("Addministrator added successfully", "success")
                else:
                    flash(f"{found_admin[0]['admin'].split('-')[1]} already exists in this plant section")
        else:
            flash("please select section before you add Administrator")
    return render_template('masterAdmin_addAdmin.html',administrator=administrator,plant_section=plant_section,user=user)

@app.route('/master_remove',methods=['GET','POST'])
def master_remove():

    if is_logged_out():
        return redirect(url_for('login'))
    user=session['user']
    administrator=get_all_administrators()
    plant_section=get_all_plant_sections()
    
    if request.method=='POST':
        selected_admins = request.form.getlist("selected_admins[]")
       
        section = request.form.get("section")
        if section:
            for admins in selected_admins:
                print(admins.split(",")[0])
                admin_id=admins.split(",")[0]
                found_admin=get_administrator_with_id_and_section(admin_id,section)
                if found_admin:
                    print("deleted",found_admin)
                    delete_from_admin(admin_id, section)
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
    administrator=get_all_administrators_on_all_sections()
    plant_section=get_all_plant_sections()
    for items in administrator:
        items['company_number']=items['admin'].split("-")[0]
        items['username']=items['admin'].split("-")[1]
   

    if request.method=='POST':
        section = request.form.get("section")
        administrators=get_all_administrators_on_particular_sections(section)
        for items in administrators:
            items['company_number']=items['admin'].split("-")[0]
            items['username']=items['admin'].split("-")[1]
        return render_template('masterAdmin_viewAdmin.html',administrator=administrators,plant_section=plant_section,user=user)
    return render_template('masterAdmin_viewAdmin.html',administrator=administrator,plant_section=plant_section,user=user)


@app.route('/admin_create_question',methods=['GET','POST'])
def admin_create_question():

    if is_logged_out():
        return redirect(url_for('login'))
    
    user=session['user']
    plant_sections=[]
    found_admin=get_administrator_with_id(user['id'])
    if not found_admin:
        flash("you are currently not assigned to any plant section")
        return redirect(url_for('login'))
    else:
       
        for item in found_admin:
            plant_sections.append(item['plant_section'])
    
    if request.method=="POST":
        
        section = request.form.get("section")
        question = request.form.get("question")
        question_type = request.form.get("question_type")
        options = request.form.getlist("options[]")
        reasoning = request.form.get("reasoning")
        if not section:
            flash("please select plant section you want to add question to")
            redirect(url_for("admin_create_question"))
        else:
            exists=get_all_plantsection_and_question(section,question)
            if not exists:
                insert_into_checklist_questions(section,question,question_type,options,reasoning,user['id'])
                flash("Your question is successfully created", "success")
            else:
                flash("this question already exists")
    return render_template('admin_create_questions.html',plant_sections=plant_sections,user=user)


@app.route('/admin_delete_question',methods=["GET","POST"])
def admin_delete_question():
    
    if is_logged_out():
        return redirect(url_for('login'))

    user=session['user']
    plant_sections=[]
    found_admin=get_administrator_with_id(user['id'])
   
    if not found_admin:
        flash("you are currently not assigned to any plant section")
        return redirect(url_for('login'))
    else:
       
        for item in found_admin:
            plant_sections.append(item['plant_section'])
           
            questions=get_all_questions(item['plant_section'])
            
    if request.method=="POST":
        if request.is_json:
            data = request.get_json()
            selected_section = data.get('section')
      
            
            # Filter questions based on the selected section
            filtered_section = get_all_questions_on_particular_sections(selected_section)
      
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
                        
                        # Call a function to delete the selected questions
                        delete_selected_questions(id)
                        flash("Question successfully deleted", "success")
                    return redirect(url_for('admin_delete_question'))
    return render_template('admin_delete_questions.html',questions=questions,plant_sections=plant_sections,user=user)


@app.route('/admin_edit_question',methods=['POST','GET'])
def admin_edit_question():

    if is_logged_out():
        return redirect(url_for('login'))
    
    user=session['user']
    plant_sections=[]
    found_admin=get_administrator_with_id(user['id'])
    if not found_admin:
        flash("you are currently not assigned to any plant section")
        return redirect(url_for('login'))
    else:
        
        for item in found_admin:
            plant_sections.append(item['plant_section'])
            questions=get_all_questions(item['plant_section'])
   

    if request.method=="POST":
        if request.is_json:
            data = request.get_json()
            selected_section = data.get('section')
      
            
            # Filter questions based on the selected section
            filtered_section = get_all_questions_on_particular_sections(selected_section)
      
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
            question=get_one_question(question_id)
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
       
        question = request.form.get("question")
        question_type = request.form.get("question_type")
        options = request.form.getlist("options[]")
        reasoning = request.form.get("reasoning")
        update_selected_questions(id, question, question_type, options, reasoning)
        flash("Question successfully updated", "success")
        return redirect(url_for("admin_edit_question"))
    return render_template('admin_modify_question.html',user=user)


@app.route('/admin_create_checklist', methods=['GET', 'POST'])
def admin_create_checklist():

    if is_logged_out():
        return redirect(url_for('login'))
    

    operators = get_all_operators()
    user=session['user']
    print(user)
    plant_sections=[]
    found_admin=get_administrator_with_id(user["id"])
    count=get_count_of_question()
    print(found_admin)
    if not found_admin:
        flash("you are currently not assigned to any plant section")
        return redirect(url_for('login'))
    else:
        for item in found_admin:
            plant_sections.append(item['plant_section'])
            questions=get_all_questions(item['plant_section'])
   

    if request.method == "POST":
        # Check if the request contains JSON data
        if request.is_json:
            data = request.get_json()
            selected_section = data.get('section')
      
            
            # Filter questions based on the selected section
            filtered_section = get_all_questions_on_particular_sections(selected_section)
      
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
            location=get_all_locations_by_plant_section(section)
            print("location ",location)
            Checked_questions=request.form.getlist("question_id[]")
            operators_questions=[]
            if Checked_questions:
                for id in Checked_questions:
                    operators_questions.append(get_all_questions_selected_questions(id)[0])

                for option in operators_questions:
                    
                    item=option['options'][0].split(",")
                    option['options'][0]=[i for i in item]
               
                latitute_longitude=[]
                for item in location:
                    
                    lat_lon={"latitude":item['latitude'],"longitude":item['longitude'],"range":item['range']}
                    
                    latitute_longitude.append(lat_lon)
                operator=get_operator_with_id(select)
                print(latitute_longitude)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if len(operators_questions)>0:
                   
                    print("count ", count)
                    
                    if len(count)<2:
                        insert_question(operators_questions, latitute_longitude,section, operator[0]['company_number'], operator[0]['name'], timestamp,checklist_answers=None, operators_location=None )
                        flash("checklist was created Successfully")
                    else:
                        flash("you cannot create more checklist, please upgrade your subscription")
                else:
                    flash("please choose atleast one or more questions")
            # Process the form data (e.g., save to database)
            return redirect(url_for("admin_create_checklist")) #render_template("tion.html",operators_questions=operators_questions)
    
    if count:
        for item in count:
            print("item ",type(json.loads(item['checklist_questions'])))
            item['checklist_questions']=json.loads(item['checklist_questions'])
   
    # Render the template for GET requests
    return render_template('admin_create_checklist.html',user=user,count=count, operators=operators, questions=questions,plant_sections=plant_sections)

@app.route("/delete_checklist/<id>",methods=["GET","POST"])
def delete_checklist(id):
    delete_checklist_questions(id)
    flash("checklist deleted succeesfully")
    return redirect(url_for("register"))

@app.route('/admin_view_answers', methods=['GET', 'POST'])
def admin_view_answers():

    if is_logged_out():
        return redirect(url_for('login'))

    plant_sections = get_all_plant_sections()  # Get all plant sections for the dropdown

    if request.method == "POST":
        selected_section = request.form.get('section')  # Get the selected section from the form
        if selected_section:
            # Filter answers based on the selected section
            answers = get_all_answered_questions_by_plant_section(selected_section)
            print("if ",answers)
        else:
            # If no section is selected, return all answers
            answers = get_all_answered_questions()
            print("else ",answers)
        # Return the filtered answers and plant sections to the template
        return render_template("admin_view_answers.html", answers=answers, plant_sections=plant_sections)

    # For GET requests, return all answers
    answers = get_all_answered_questions()
    print("default ",answers)
    checklist_answers=[]
    for item in answers:
        print("debug item",item['checklist_answers'])
        ans=json.dumps(item['checklist_answers'])
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

    plant_section = plant_section.upper().strip()  # Get plant_section from query parameters
    print("section ",plant_section)
    if not plant_section:
        return jsonify({"error": "plant_section parameter is required"}), 400

    results=get_all_answered_questions_by_plant_section(plant_section)
    for items in results:
        location=json.loads(items['location'])
        checklist_answers=json.loads(items['checklist_answers'])
        print(type(items['location']))
        items['location']=location
        items['checklist_answers']=checklist_answers
    print(results)
    return jsonify(results)  # Return all records as JSON


@app.route('/api/all_answered_questions', methods=['GET'])
def all_answered_questions():

    # if is_logged_out():
    #     return redirect(url_for('login'))

    results=get_all_answered_questions()
    for items in results:
        location=json.loads(items['location'])
        checklist_answers=json.loads(items['checklist_answers'])
        print(type(items['location']))
        items['location']=location
        items['checklist_answers']=checklist_answers
    print("answers --",results)
    return jsonify(results)  # Return all records as JSON

@app.route('/operator', methods=["GET", "POST"])
def operator():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    questions = get_all_questions_by_company_number(user['company_number'])
    if request.method == 'POST':
        user_data = request.json
        user_lat = user_data.get('latitude')
        user_lon = user_data.get('longitude')
        user_answers = user_data.get('answers_with_questions', None)

        
        if not questions:
            return jsonify({'status': 'error', 'message': 'No checklist questions found'})
        print("questions ", questions)
        location = json.loads(questions[0]['location'])[0]
        is_within = is_within_range(
            str(user_lat), str(user_lon),
            location['latitude'], location['longitude'],
            location['range']
        )
        response_data = {
            'status': 'success',
            'is_within_range': is_within,
        }
        print("response data ",response_data)
        checklist_id = questions[0]['id']

        if user_answers is not None:
            if is_within:
                output = store_answers(checklist_id, user_answers)
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


@app.route("/submit_location", methods=["GET","POST"])
def submit_location():

    if is_logged_out():
        return redirect(url_for('login'))

    user=session['user']
    locations=get_all_locations()
    print(locations)
    if request.method=='POST':
        
        plant_section= request.form["plant_section"]
        latitude= request.form["latitude"]
        longitude= request.form["longitude"]
        range= request.form["range"]
        user_id=user['id']
        insert_into_section_location(plant_section.upper(), latitude, longitude, range, user_id)
        
        flash("location successfully saved")
        return redirect(url_for("submit_location"))
    return render_template("superAdmin_location_update.html",locations=locations,user=user)


@app.route('/delete_location/<plant_section>', methods=['GET', 'POST'])
def delete_location(plant_section):
    if is_logged_out():
        return redirect(url_for('login'))

    user = session['user']
    locations = get_all_locations()
    print(locations)
    print("Plant section:", plant_section)

    # Delete the location and unanswered questions
    results = delete_from_super_admin(plant_section)
    unanswered_questions = delete_all_unanswered_questions(plant_section)
    

    if results:
        print("Location deleted:", results, "Deleted unanswered questions:", unanswered_questions)
        delete_assined_sections_by_section(plant_section)
        flash("Location deleted from your repository", "success")
    else:
        flash("Failed to delete location", "error")

    # Redirect to the superAdmin_location_update page
    return redirect(url_for('submit_location'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    user=session['user']
    admins=get_all_administrators()
    administrator=get_all_administrators_on_all_sections()
    users=get_all_users()
    count=get_count_of_question()
    for items in administrator:
        items['company_number']=items['admin'].split("-")[0]
        items['username']=items['admin'].split("-")[1]
    print("admins ",admins)
    if request.method=='POST':
        company_number=request.form.get('company_number')
        username=request.form.get('username')
        password=request.form.get('password')
        role=request.form.get('role')
        if user_exist_credentials(company_number.upper()):
            flash("This user already exists")
        else:
            insert_registerd_user(company_number.upper(), password.strip(), role,username.upper().strip())
            flash("User registered successfully")
            redirect(url_for("register"))
    if count:
        for item in count:
            print("item ",type(json.loads(item['checklist_questions'])))
            item['checklist_questions']=json.loads(item['checklist_questions'])
    return render_template('superAdmin.html',count=count,users=users,user=user,admins=admins,administrator=administrator)




@app.route('/delete_assigned_section/<id>',methods=['GET','POST'])
def delete_assigned_section(id):
    delete_assined_sections(id)
    flash("assignment removed")
    return redirect(url_for('register'))

@app.route('/delete_user/<id>',methods=['GET','POST'])
def delete_user(id):
    delete_the_user(id)
    flash("User deleted succesfully")
    return redirect(url_for('register'))


from geopy.distance import geodesic

def is_within_range(user_lat, user_lon, target_lat, target_lon, range_meters):
    """
    Check if the user's location is within the specified range of the target location.

    :param user_lat: User's latitude
    :param user_lon: User's longitude
    :param target_lat: Target latitude
    :param target_lon: Target longitude
    :param range_meters: Range in meters
    :return: True if the user is within range, False otherwise
    """
    # Create tuples for the user and target locations
    user_location = (user_lat, user_lon)
    target_location = (target_lat, target_lon)

    # Calculate the distance between the two points in meters
    distance = geodesic(user_location, target_location).meters

    # Check if the distance is within the specified range
    return distance <= range_meters

@app.route('/getlocation',methods=['POST','GET'])
def getlocation():
    return render_template("getlocation.html")

def is_logged_out():
   
    if not session.get('user'):
        return True

if __name__ == '__main__':
    app.run(debug=True)
    # manager.run()