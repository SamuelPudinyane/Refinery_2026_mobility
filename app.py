from flask import render_template,Flask,request,session,flash,redirect, url_for,jsonify
from dbqueries import (insert_registerd_user,get_db_connection,verify_user_credentials,get_all_administrators,insert_into_admin,
                       delete_from_admin,get_all_administrators_on_all_sections,get_all_administrators_on_particular_sections,
                       get_all_operators,insert_into_checklist_questions,get_all_questions,delete_selected_questions,get_one_question,
                       update_selected_questions,get_all_questions_on_particular_sections,get_all_questions_selected_questions,get_administrator_with_id_and_section,
                       get_administrator_with_id,insert_into_section_location,get_all_locations,get_all_plant_sections,get_all_plantsection_and_question,get_all_locations_by_plant_section,
                        get_operator_with_id,insert_question
                       )
from datetime import datetime
import json


app = Flask(__name__)

app.secret_key="session"

@app.route("/")
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        company_number=request.form.get('username')
        password=request.form.get('password')
        user=verify_user_credentials(company_number,password)
       
        session["user"]=user
        if not user:
            flash("An error has occurred. Make sure your login credentials are correct", "error")
            return redirect(url_for('login'))
        
        if user['role']=='master_administrator':
            administrator=get_all_administrators()
            return render_template('masterAdmin_addAdmin.html',administrator=administrator)
        
        elif user['role']=='administrator':
            return redirect(url_for('admin_create_checklist')) 
        
        elif user['role']=='operator':
            return redirect(url_for('operator'))
        
        elif user['role']=='superadmin':
            return render_template("superAdmin.html")

    return render_template('index.html')


@app.route('/master_add',methods=['GET','POST'])
def master_add():
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
    return render_template('masterAdmin_addAdmin.html',administrator=administrator,plant_section=plant_section)

@app.route('/master_remove',methods=['GET','POST'])
def master_remove():
    administrator=get_all_administrators()
    plant_section=get_all_plant_sections()
    if request.method=='POST':
        selected_admins = request.form.getlist("selected_admins[]")
       
        section = request.form.get("section")
        if section:
            for admins in selected_admins:
                admin_id=admins.split(",")[0]
                found_admin=get_administrator_with_id_and_section(admin_id,section)
                if found_admin:
                    
                    delete_from_admin(admin_id, section)
                    flash("You have successfully removed this Administrator", "success")
                else:
                    flash(f"This admin does not exists in this plant section")
        else:
            flash("please select section before you remove administrator","error")
    return render_template('masterAdmin_removeAdmin.html',administrator=administrator,plant_section=plant_section)

@app.route('/master_view',methods=['GET','POST'])
def master_view():
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
        return redirect(url_for("master_view"))
    return render_template('masterAdmin_viewAdmin.html',administrator=administrator,plant_section=plant_section)


@app.route('/admin_create_question',methods=['GET','POST'])
def admin_create_question():

    user=session['user']
    print(user)
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
    return render_template('admin_create_questions.html',plant_sections=plant_sections)


@app.route('/admin_delete_question',methods=["GET","POST"])
def admin_delete_question():
    
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
      
            
            # Return filtered questions as JSON
            return jsonify({
                "message": "Section received",
                "section": selected_section,
                "filtered_section": filtered_section
            })
        else:
            question_ids = request.form.getlist("question_ids[]")
        
            if question_ids:
                    for id in question_ids:
                        
                        # Call a function to delete the selected questions
                        delete_selected_questions(id)
                        flash("Question successfully deleted", "success")
                        return redirect(url_for('admin_delete_question'))
    return render_template('admin_delete_questions.html',questions=questions,plant_sections=plant_sections)


@app.route('/admin_edit_question',methods=['POST','GET'])
def admin_edit_question():
    
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
      
            
            # Return filtered questions as JSON
            return jsonify({
                "message": "Section received",
                "section": selected_section,
                "filtered_section": filtered_section
            })
        else:

            question_id = request.form.get("question_id")
            question=get_one_question(question_id)
            return render_template('admin_modify_question.html',question=question,plant_sections=plant_sections)
    
    return render_template('admin_edit_question.html',questions=questions,plant_sections=plant_sections)

@app.route('/admin_modify_question',methods=["GET","POST"])
def admin_modify_question():

    if request.method=="POST":
        
        question = request.form.get("question")
        question_type = request.form.get("question_type")
        options = request.form.getlist("options[]")
        reasoning = request.form.get("reasoning")
        update_selected_questions(id, question, question_type, options, reasoning)
        flash("Question successfully updated", "success")
    return render_template('admin_modify_question.html')


@app.route('/admin_create_checklist', methods=['GET', 'POST'])
def admin_create_checklist():
    operators = get_all_operators()
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
            select = request.form.get("select")
            location=get_all_locations_by_plant_section(section)
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
                    print(item)
                    lat_lon={"latitude":item['latitude'],"longitude":item['longitude'],"range":item['range']}
                    
                    latitute_longitude.append(lat_lon)
                operator=get_operator_with_id(select)
                print(latitute_longitude)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                insert_question(operators_questions, latitute_longitude,section, operator[0]['company_number'], operator[0]['name'], timestamp,checklist_answers=None, operators_location=None )
            # Process the form data (e.g., save to database)
            return render_template("tion.html",operators_questions=operators_questions)

    # Render the template for GET requests
    return render_template('admin_create_checklist.html', operators=operators, questions=questions,plant_sections=plant_sections)



@app.route('/operator')
def operator():
    user=session['user']
    
    questions=get_all_questions(user['company_number'])
    
    
    questions=json.loads(questions[0]['checklist_questions'])
    print(questions)
    # questions[0]['reasoning']="no"
    # questions=questions
 
    return render_template('operator.html',operators_questions=questions)


@app.route("/submit_location", methods=["GET","POST"])
def submit_location():
    user=session['user']
    locations=get_all_locations()
    if request.method=='POST':
        
        plant_section= request.form["plant_section"]
        latitude= request.form["latitude"]
        longitude= request.form["longitude"]
        range= request.form["range"]
        user_id=user['id']
        locations=insert_into_section_location(plant_section, latitude, longitude, range, user_id)
        if "message" in locations:
            flash("plant section already exist")
        else:
            flash("successfully safed")
            return redirect(url_for("submit_location"))
    return render_template("superAdmin_location_update.html",locations=locations)

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method=='POST':
        company_number=request.form.get('company_number')
        username=request.form.get('username')
        password=request.form.get('password')
        role=request.form.get('role')
        insert_registerd_user(company_number.upper(), password.strip(), role,username.upper().strip())

    return render_template('superAdmin.html')



if __name__ == '__main__':
    app.run(debug=True)