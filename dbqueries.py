import psycopg2
import bcrypt
from encryption import (hash_password)
from psycopg2 import sql
import json
import os


""" 
{
  "previewLimit": 50,
  "server": "localhost",
  "port": 5432,
  "driver": "PostgreSQL",
  "name": "rand_refinary",
  "database": "rand_refinary",
  "username": "postgres",
  "password": "Admin"
} 

"""

def get_db_connection():
    try:
        # Use environment variables for connection parameters
        conn = psycopg2.connect(
            dbname="rand_refinary", 
            user="postgres",  
            password="Admin",  
            host="localhost", 
            port=5432 
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None


# def get_db_connection():
#     try:
#         conn = psycopg2.connect(
#             dbname=os.getenv("DB_NAME", "randrefinerydb_hdcz"),  
#             user=os.getenv("DB_USER", "randrefinerydb_hdcz_user"),    
#             password=os.getenv("DB_PASSWORD", "NJY9sBdbbw3Sipd0gFGhHFjlLoiWnaaD"),  
#             host=os.getenv("DB_HOST", "dpg-cudl8flumphs73cpbcj0-a"),  
#             port=os.getenv("DB_PORT", "5432")  
#         )
#         print("Database Connection Successful!")
#         return conn
#     except Exception as e:
#         print(f"Database Connection Error: {e}")
#         return None



# Database connection function
def insert_registerd_user(company_name, password, role,username):
    """Inserts a new user into the PostgreSQL database."""
    hashed_password = hash_password(password)  # Securely hash the password
    
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert Query
        query = """
        INSERT INTO rand_refinary_registration (company_number, password, role,name) 
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """
        cur.execute(query, (company_name, hashed_password, role,username))
        
        user_id = cur.fetchone()[0]  # Get the ID of the inserted user
        
        # Commit and close connection
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"User inserted successfully with ID: {user_id}")
        return user_id

    except psycopg2.Error as e:
        print("Error inserting user:", e)
        return None


def verify_user_credentials(company_number, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch stored hashed password, company_number, and role
    cursor.execute("SELECT id,password, company_number, role,name FROM rand_refinary_registration WHERE company_number = %s", (company_number,))
    row = cursor.fetchone()
    
    conn.close()
    if row:
        id,stored_hash, company_number, role,name = row  # Unpack the row
    
        # Verify the entered password against the stored hash
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return {"id":id,"company_number": company_number, "role": role,"name":name}  # Return relevant data

    return None  # Return None if verification fails


def get_all_administrators():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all users with role = 'administrator'
    cursor.execute("SELECT id,name,company_number, role FROM rand_refinary_registration WHERE role = 'administrator'")
    rows = cursor.fetchall()

    conn.close()

    # Convert query result into a list of dictionaries
    administrators = [{"id": row[0],"name":row[1], "company_number": row[2],"role":row[3]} for row in rows]

    return administrators


def insert_into_admin(plant_section, admin, admin_id):
    """Inserts a new administrator into the PostgreSQL database and returns the new admin ID."""
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert Query
        query = """
        INSERT INTO administrator (plant_section, admin, admin_id) 
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        cur.execute(query, (plant_section, admin, admin_id))

        # Fetch the newly inserted admin ID
        new_admin_id = cur.fetchone()[0]  # Fetch the first (and only) column from the returned row

        # Commit and close connection
        conn.commit()
        cur.close()
        conn.close()
        
        return new_admin_id  # Return the new admin's ID

    except psycopg2.Error as e:
        print("Error inserting admin:", e)
        conn.rollback()  # Rollback in case of an error
        return None  # Return None to indicate failure


def delete_from_admin(admin_id, plant_section):
    """Deletes an administrator from the PostgreSQL database."""
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete Query
        query = "DELETE FROM administrator WHERE admin_id=%s AND plant_section=%s"
        cur.execute(query, (admin_id, plant_section))  # Fixed parameter order

        # Check if deletion was successful
        if cur.rowcount > 0:  # rowcount returns number of affected rows
            conn.commit()
            result = True  # Successfully deleted
        else:
            result = False  # No rows were deleted (admin_id not found)

        # Close connection
        cur.close()
        conn.close()
        return result

    except psycopg2.Error as e:
        print("Error deleting admin:", e)
        return False  # Return False in case of an error


def get_all_administrators_on_all_sections():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all users with role = 'administrator'
    cursor.execute("SELECT id,plant_section,admin, admin_id FROM administrator")
    rows = cursor.fetchall()

    conn.close()

    # Convert query result into a list of dictionaries
    administrators = [{"id": row[0],"plant_section":row[1], "admin": row[2],"admin_id":row[3]} for row in rows]

    return administrators


def get_all_administrators_on_particular_sections(plant_section):
    """Fetch all administrators in a specific plant section."""
    try:
        # Ensure proper resource management
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT id, plant_section, admin, admin_id 
                FROM administrator 
                WHERE plant_section = %s
                """
                cursor.execute(query, (plant_section,))  # Fixed parameter passing

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert query result into a list of dictionaries
                administrators = [
                    {"id": row[0], "plant_section": row[1], "admin": row[2], "admin_id": row[3]} 
                    for row in rows
                ]

                return administrators  # Return the list

    except Exception as e:
        print("Error fetching administrators:", e)
        return []  # Return empty list if an error occurs



def get_all_plantsection_and_question(plant_section,question):
    """Fetch all administrators in a specific plant section."""
    try:
        # Ensure proper resource management
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT id, plant_section, question 
                FROM checklist_questions 
                WHERE plant_section = %s AND question = %s
                """
                cursor.execute(query, (plant_section,question))  # Fixed parameter passing

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert query result into a list of dictionaries
                questions = [
                    {"id": row[0], "plant_section": row[1], "question": row[2]} 
                    for row in rows
                ]

                return questions  # Return the list

    except Exception as e:
        print("Error fetching administrators:", e)
        return []  # Return empty list if an error occurs



def get_count_of_question():
    """Fetch the total number of questions and details for each record."""
    try:
        # Establish database connection
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Query to fetch total count and question details
                query = """
                SELECT 
                    COUNT(*) OVER() AS total_count,  -- Window function for total count
                    id, 
                    plant_section, 
                    checklist_questions,
                    location
                FROM questions;
                """
                cursor.execute(query)

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert query result into a list of dictionaries
                questions = [
                    {
                        "total_count": row[0],
                        "id": row[1],
                        "plant_section": row[2],
                        "checklist_questions": row[3]
                    } 
                    for row in rows
                ]

                return questions  # Return the list of dictionaries

    except Exception as e:
        print(f"Error fetching questions: {e}")
        return []  # Return empty list if an error occurs



def delete_checklist_questions(id):
    """Deletes an checklist_questions from the PostgreSQL database."""
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete Query
        query = "DELETE FROM questions WHERE id=%s "
        cur.execute(query, (id,))  # Fixed parameter order

        # Check if deletion was successful
        if cur.rowcount > 0:  # rowcount returns number of affected rows
            conn.commit()
            result = True  # Successfully deleted
        else:
            result = False  # No rows were deleted (admin_id not found)

        # Close connection
        cur.close()
        conn.close()
        return result

    except psycopg2.Error as e:
        print("Error deleting admin:", e)
        return False  # Return False in case of an error


def delete_assined_sections(id):
    """Deletes an administrator from the PostgreSQL database."""
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete Query
        query = "DELETE FROM administrator WHERE admin_id=%s"
        cur.execute(query,(id,))  # Fixed parameter order

        # Check if deletion was successful
        if cur.rowcount > 0:  # rowcount returns number of affected rows
            conn.commit()
            result = True  # Successfully deleted
        else:
            result = False  # No rows were deleted (admin_id not found)

        # Close connection
        cur.close()
        conn.close()
        return result

    except psycopg2.Error as e:
        print("Error deleting admin:", e)
        return False  # Return False in case of an error


def delete_assined_sections_by_section(plant_section):
    """Deletes an administrator from the PostgreSQL database."""
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete Query
        query = "DELETE FROM administrator WHERE plant_section=%s"
        cur.execute(query,(plant_section,))  # Fixed parameter order

        # Check if deletion was successful
        if cur.rowcount > 0:  # rowcount returns number of affected rows
            conn.commit()
            result = True  # Successfully deleted
        else:
            result = False  # No rows were deleted (admin_id not found)

        # Close connection
        cur.close()
        conn.close()
        return result

    except psycopg2.Error as e:
        print("Error deleting admin:", e)
        return False  # Return False in case of an error




def get_administrator_with_id_and_section(admin_id,section):
    """Fetch administrators with id."""
    try:
        # Ensure proper resource management
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT id, plant_section, admin, admin_id 
                FROM administrator 
                WHERE admin_id = %s AND plant_section=%s
                """
                cursor.execute(query, (admin_id,section))  # Fixed parameter passing

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert query result into a list of dictionaries
                administrators = [
                    {"id": row[0], "plant_section": row[1], "admin": row[2], "admin_id": row[3]} 
                    for row in rows
                ]

                return administrators  # Return the list
    except Exception as e:
        print("Error fetching administrators:", e)
        return []  # Return empty list if an error occurs


def get_administrator_with_id(admin_id):
    """Fetch administrators with id."""
    try:
        # Ensure proper resource management
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT id, plant_section, admin, admin_id 
                FROM administrator 
                WHERE admin_id = %s
                """
                cursor.execute(query, (admin_id,))  # Fixed parameter passing

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert query result into a list of dictionaries
                administrators = [
                    {"id": row[0], "plant_section": row[1], "admin": row[2], "admin_id": row[3]} 
                    for row in rows
                ]

                return administrators  # Return the list
    except Exception as e:
        print("Error fetching administrators:", e)
        return []  # Return empty list if an error occurs


def get_operator_with_id(id):
    """Fetch operator with id."""
    try:
        # Ensure proper resource management
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT id, company_number, role, name 
                FROM rand_refinary_registration 
                WHERE id = %s
                """
                cursor.execute(query, (id,))  # Fixed parameter passing

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert query result into a list of dictionaries
                operator = [
                    {"id": row[0], "company_number": row[1], "role": row[2], "name": row[3]} 
                    for row in rows
                ]

                return operator  # Return the list
    except Exception as e:
        print("Error fetching administrators:", e)
        return []  # Return empty list if an error occurs




def get_all_operators():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all users with role = 'administrator'
    cursor.execute("SELECT id,name,company_number, role FROM rand_refinary_registration WHERE role = 'operator'")
    rows = cursor.fetchall()

    conn.close()

    # Convert query result into a list of dictionaries
    operators = [{"id": row[0],"name":row[1], "company_number": row[2],"role":row[3]} for row in rows]

    return operators


def insert_into_checklist_questions(plant_section, question,question_type,options,reasoning,author_id):
    """Inserts a new checklist_questions into the PostgreSQL database """
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert Query
        query = """
        INSERT INTO checklist_questions (plant_section, question,question_type,options,reasoning,author_id) 
        VALUES (%s, %s, %s, %s, %s,%s)
        RETURNING id;
        """
        cur.execute(query, (plant_section, question,question_type,options,reasoning,author_id))

        # Fetch the newly inserted admin ID
        new_admin_id = cur.fetchone()[0]  # Fetch the first (and only) column from the returned row

        # Commit and close connection
        conn.commit()
        cur.close()
        conn.close()
        
        return new_admin_id  # Return the new admin's ID

    except psycopg2.Error as e:
        print("Error inserting admin:", e)
        conn.rollback()  # Rollback in case of an error
        return None  # Return None to indicate failure

def get_all_questions(section):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all questions
    cursor.execute("""SELECT id,plant_section,question, question_type,options,reasoning,author_id
                    FROM checklist_questions WHERE plant_section=%s""",(section,))
    rows = cursor.fetchall()

    conn.close()

    # Convert query result into a list of dictionaries
    questions = [{"id": row[0],"plant_section":row[1], "question": row[2],"question_type":row[3],"reasoning":row[4],"author_id":row[5]} for row in rows]

    return questions



def delete_selected_questions(id):
    """Deletes an checklist_questions from the PostgreSQL database."""
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete Query
        query = "DELETE FROM checklist_questions WHERE id=%s "
        cur.execute(query, (id,))  # Fixed parameter order

        # Check if deletion was successful
        if cur.rowcount > 0:  # rowcount returns number of affected rows
            conn.commit()
            result = True  # Successfully deleted
        else:
            result = False  # No rows were deleted (admin_id not found)

        # Close connection
        cur.close()
        conn.close()
        return result

    except psycopg2.Error as e:
        print("Error deleting admin:", e)
        return False  # Return False in case of an error


def get_one_question(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all questions
    cursor.execute("""SELECT id,plant_section,question, question_type,options,reasoning
                    FROM checklist_questions WHERE id=%s """,(id,))
    row = cursor.fetchone()

    conn.close()
    print("row ",row)
    # Convert query result into a list of dictionaries
    questions = [{"id": row[0],"plant_section":row[1], "question": row[2],"question_type":row[3],"options":row[4],"reasoning":row[5]}]
   
    return questions

def update_selected_questions(id, question=None, question_type=None, options=None, reasoning=None):
    """Updates checklist question fields in the PostgreSQL database if they are not NULL."""
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # List to hold the query parameters
        query_params = []
        set_clause = []

        # Add the fields to the update query only if they are not None
        if question is not None:
            set_clause.append("question = %s")
            query_params.append(question)
        
        if question_type is not None:
            set_clause.append("question_type = %s")
            query_params.append(question_type)

        if options is not None:
            set_clause.append("options = %s")
            query_params.append(options)

        if reasoning is not None:
            set_clause.append("reasoning = %s")
            query_params.append(reasoning)

        # If no fields are provided to update, return False
        if not set_clause:
            print("No fields provided to update.")
            return False

        # Add the condition for the question ID
        set_clause_str = ", ".join(set_clause)
        query_params.append(id)  # Add the question ID at the end of parameters

        # Construct the final SQL query
        query = f"UPDATE checklist_questions SET {set_clause_str} WHERE id = %s"

        # Execute the update query
        cur.execute(query, tuple(query_params))

        # Check if the update was successful
        if cur.rowcount > 0:
            conn.commit()
            result = True  # Successfully updated
        else:
            result = False  # No rows were updated (id not found)

        # Close connection
        cur.close()
        conn.close()
        return result

    except psycopg2.Error as e:
        print("Error updating question:", e)
        return False  # Return False in case of an error


def get_all_questions_selected_questions(id):
    """Fetch all administrators in a specific plant section."""
    try:
        # Ensure proper resource management
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT id,plant_section,question, question_type,options,reasoning
                    FROM checklist_questions 
                WHERE id = %s
                """
                cursor.execute(query, (id,))  # Fixed parameter passing

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert query result into a list of dictionaries
                questions = [
                    {"id": row[0], "plant_section": row[1], "question": row[2], "question_type": row[3],"options":row[4],"reasoning":row[5]} 
                    for row in rows
                ]

                return questions  # Return the list

    except Exception as e:
        print("Error fetching administrators:", e)
        return []  # Return empty list if an error occurs

def get_all_questions_on_particular_sections(plant_section):
    """Fetch all administrators in a specific plant section."""
    try:
        # Ensure proper resource management
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT id,plant_section,question, question_type,options,reasoning
                    FROM checklist_questions 
                WHERE plant_section = %s
                """
                cursor.execute(query, (plant_section,))  # Fixed parameter passing

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert query result into a list of dictionaries
                questions = [
                    {"id": row[0], "plant_section": row[1], "question": row[2], "question_type": row[3],"options":row[4],"reasoning":row[5]} 
                    for row in rows
                ]

                return questions  # Return the list

    except Exception as e:
        print("Error fetching administrators:", e)
        return []  # Return empty list if an error occurs


def insert_into_section_location(plant_section, latitude, longitude, range, user_id):
    """Inserts a new section location into the PostgreSQL database """
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the plant_section already exists
        check_query = """
        SELECT 1 FROM plant_section_locations WHERE plant_section = %s LIMIT 1;
        """
        cur.execute(check_query, (plant_section,))
        exists = cur.fetchone()

        if exists:
            # If plant_section already exists, return a message indicating this
            return {"message": "Plant section already exists."}
        else:
            # Insert Query
            query = """
            INSERT INTO plant_section_locations(
                plant_section, latitude, longitude, range, user_id)
                VALUES ( %s, %s, %s, %s, %s)
            RETURNING id, plant_section, latitude, longitude, range, user_id;
            """
            cur.execute(query, (plant_section, latitude, longitude, range, user_id))

            # Fetch the newly inserted admin ID
            data = cur.fetchone()[0]  # Fetch the first (and only) column from the returned row

            # Commit and close connection
            conn.commit()
            cur.close()
            conn.close()
            
            return data  # Return the new admin's ID

    except psycopg2.Error as e:
        print("Error inserting admin:", e)
        conn.rollback()  # Rollback in case of an error
        return None  # Return None to indicate failure


def get_all_locations():
    """Fetch all plant_section_locations."""
    try:
        # Ensure proper resource management
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT id,plant_section, latitude, longitude, range, user_id
                    FROM plant_section_locations 
                
                """
                cursor.execute(query, )  # Fixed parameter passing

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert query result into a list of dictionaries
                data = [
                    {"id": row[0], "plant_section": row[1], "latitude": row[2], "longitude": row[3],"range":row[4],"user_id":row[5]} 
                    for row in rows
                ]

                return data  # Return the list

    except Exception as e:
        print("Error fetching administrators:", e)
        return []  # Return empty list if an error occurs


def get_all_plant_sections():
    """Fetch all plant_section."""
    try:
        # Ensure proper resource management
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT id,plant_section, latitude, longitude, range, user_id
                    FROM plant_section_locations 
                
                """
                cursor.execute(query, )  # Fixed parameter passing

                # Fetch all rows
                rows = cursor.fetchall()

                # Convert query result into a list of dictionaries
                data = [
                    {"id": row[0], "plant_section": row[1], "latitude": row[2], "longitude": row[3],"range":row[4],"user_id":row[5]} 
                    for row in rows
                ]

                return data  # Return the list

    except Exception as e:
        print("Error fetching administrators:", e)
        return []  # Return empty list if an error occurs




def get_all_locations_by_plant_section(plant_section):
    """Fetch all plant_section_locations for a given plant_section.
    
    Args:
        plant_section (str): The plant section to query locations for
        
    Returns:
        list: A list of dictionaries containing location data, or empty list if none found
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT id, plant_section, latitude, longitude, range, user_id
                FROM plant_section_locations
                WHERE plant_section = %s
                ORDER BY id DESC
                """
                cursor.execute(query, (plant_section,))
                
                # Use named cursor description for more robust column access
                columns = [desc[0] for desc in cursor.description]
                locations = []
                print("database plant location ",locations)
                for row in cursor:
                    location = dict(zip(columns, row))
                    locations.append(location)
                
                return locations

    except Exception as e:
        print(f"Error fetching locations for {plant_section}: {e}")
        return []
    


def insert_question(checklist_questions, location, plant_section, company_number, operator, time_stamp,checklist_answers=None, operators_location=None ):
    """Inserts a new question entry into the PostgreSQL database"""
    conn = None
    inserted_data = None
    print(type(checklist_questions), type(location), type(plant_section), type(company_number), type(operator), type(time_stamp))
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        if conn is None:
            return None  # Return None if connection fails
        
        cur = conn.cursor()
        # Convert lists and dicts to JSON strings
        if isinstance(checklist_questions, (list, dict)):
            checklist_questions = json.dumps(checklist_questions)
        if isinstance(checklist_answers, (list, dict)):
            checklist_answers = json.dumps(checklist_answers)
        if isinstance(location, (list, dict)):
            location = json.dumps(location)
        if isinstance(operators_location, (list, dict)):
            operators_location = json.dumps(operators_location)
        # Insert Query
        insert_query = """
        INSERT INTO public.questions(
            checklist_questions, checklist_answers, location, plant_section, company_number, operator, operators_location, time_stamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, checklist_questions, checklist_answers, location, plant_section, company_number, operator, operators_location, time_stamp;
        """
        cur.execute(insert_query, (checklist_questions, checklist_answers, location, plant_section, company_number, operator, operators_location, time_stamp))

        # Fetch the newly inserted data
        inserted_data = cur.fetchone()

        # Commit the transaction
        conn.commit()

        return inserted_data  # Return all inserted data

    except psycopg2.Error as e:
        print("Error inserting question:", e)
        if conn:
            conn.rollback()  # Rollback if an error occurs
        return None  # Indicate failure

    finally:
        if conn:
            cur.close()
            conn.close()  # Ensure the connection is closed



def get_all_questions_by_company_number(company_number):
    """Retrieves all records from the questions table."""
    conn = None
    results = []

    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        if conn is None:
            return None  # Return None if connection fails

        cur = conn.cursor()

        # Select query to fetch all records
        select_query = """
        SELECT id, checklist_questions, checklist_answers, location, plant_section, 
               company_number, operator, operators_location, time_stamp
        FROM public.questions WHERE company_number=%s AND (checklist_answers IS NULL OR checklist_answers = 'null' OR checklist_answers = '') ORDER BY id DESC LIMIT 1;
        """
        
        cur.execute(select_query,(company_number,))
        rows = cur.fetchall()

        # Convert the results to a list of dictionaries
        columns = [desc[0] for desc in cur.description]  # Get column names
        results = [dict(zip(columns, row)) for row in rows]

        return results  # Return all records as a list of dictionaries

    except psycopg2.Error as e:
        print("Error fetching questions:", e)
        return None  # Indicate failure

    finally:
        if conn:
            cur.close()
            conn.close()  # Ensure the connection is closed


def get_all_questions_limited():
    """Retrieves all records from the questions table."""
    conn = None
    results = []

    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        if conn is None:
            return None  # Return None if connection fails

        cur = conn.cursor()

        # Select query to fetch all records
        select_query = """
        SELECT id, checklist_questions, checklist_answers, location, plant_section, 
               company_number, operator, operators_location, time_stamp
        FROM public.questions LIMIT 20;
        """
        
        cur.execute(select_query,)
        rows = cur.fetchall()

        # Convert the results to a list of dictionaries
        columns = [desc[0] for desc in cur.description]  # Get column names
        results = [dict(zip(columns, row)) for row in rows]

        return results  # Return all records as a list of dictionaries

    except psycopg2.Error as e:
        print("Error fetching questions:", e)
        return None  # Indicate failure

    finally:
        if conn:
            cur.close()
            conn.close()  # Ensure the connection is closed


def delete_from_super_admin(plant_section):
    """Deletes an administrator from the PostgreSQL database."""
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete Query
        query = "DELETE FROM plant_section_locations WHERE plant_section=%s"
        cur.execute(query, (plant_section,))  # Fixed parameter order

        # Check if deletion was successful
        if cur.rowcount > 0:  # rowcount returns number of affected rows
            conn.commit()
            result = True  # Successfully deleted
        else:
            result = False  # No rows were deleted (admin_id not found)

        # Close connection
        cur.close()
        conn.close()
        return result

    except psycopg2.Error as e:
        print("Error deleting admin:", e)
        return False  # Return False in case of an error

def udate_question(checklist_answers, operators_location=None ):
    """Inserts a new question entry into the PostgreSQL database"""
    conn = None
    inserted_data = None
    print(type(checklist_answers), type(operators_location))
    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        if conn is None:
            return None  # Return None if connection fails
        
        cur = conn.cursor()
        # Convert lists and dicts to JSON strings
        if isinstance(checklist_answers, (list, dict)):
            checklist_answers = json.dumps(checklist_answers)
        if isinstance(operators_location, (list, dict)):
            operators_location = json.dumps(operators_location)
        # Insert Query
        insert_query = """
        UPDATE public.questions SET(
            checklist_answers, operators_location)
        VALUES (%s, %s)
        RETURNING id, checklist_questions, checklist_answers, location, plant_section, company_number, operator, operators_location, time_stamp;
        """
        cur.execute(insert_query, (checklist_answers,operators_location))

        # Fetch the newly inserted data
        inserted_data = cur.fetchone()

        # Commit the transaction
        conn.commit()

        return inserted_data  # Return all inserted data

    except psycopg2.Error as e:
        print("Error inserting question:", e)
        if conn:
            conn.rollback()  # Rollback if an error occurs
        return None  # Indicate failure

    finally:
        if conn:
            cur.close()
            conn.close()  # Ensure the connection is closed



def get_all_questions_by_plant_section_that_are_not_answered(plant_section):
    """
    Retrieves all records from the questions table for a specific plant section
    where the checklist_answers are either NULL, 'null', or an empty string.
    
    Args:
        plant_section (str): The plant section to filter the questions by.
    
    Returns:
        list: A list of dictionaries representing the records, or None if an error occurs.
    """
    conn = None
    results = []

    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        if conn is None:
            print("Failed to connect to the database.")
            return None  # Return None if connection fails

        cur = conn.cursor()

        # Select query to fetch all records for the specified plant section
        select_query = sql.SQL("""
            SELECT id, checklist_questions, checklist_answers, location, plant_section, 
                   company_number, operator, operators_location, time_stamp
            FROM public.questions
            WHERE plant_section = %s
              AND (checklist_answers IS NULL 
                   OR checklist_answers = 'null' 
                   OR checklist_answers = '');
        """)
        
        # Execute the query with the plant_section parameter
        cur.execute(select_query, (plant_section,))
        rows = cur.fetchall()

        # Convert the results to a list of dictionaries
        columns = [desc[0] for desc in cur.description]  # Get column names
        results = [dict(zip(columns, row)) for row in rows]

        return results  # Return all records as a list of dictionaries

    except psycopg2.Error as e:
        print("Error fetching questions:", e)
        return None  # Indicate failure

    finally:
        if conn:
            cur.close()
            conn.close()  # Ensure the connection is closed



def get_all_questions_by_plant_section(plant_section):
    """
    Retrieves all records from the questions table for a specific plant section.
    
    Args:
        plant_section (str): The plant section to filter the questions by.
    
    Returns:
        list: A list of dictionaries representing the records, or None if an error occurs.
    """
    conn = None
    results = []

    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        if conn is None:
            print("Failed to connect to the database.")
            return None  # Return None if connection fails

        cur = conn.cursor()

        # Select query to fetch all records for the specified plant section
        select_query = sql.SQL("""
            SELECT id, checklist_questions, checklist_answers, location, plant_section, 
                   company_number, operator, operators_location, time_stamp
            FROM public.questions
            WHERE plant_section = %s;
        """)
        
        # Execute the query with the plant_section parameter
        cur.execute(select_query, (plant_section,))
        rows = cur.fetchall()

        # Convert the results to a list of dictionaries
        columns = [desc[0] for desc in cur.description]  # Get column names
        results = [dict(zip(columns, row)) for row in rows]

        return results  # Return all records as a list of dictionaries

    except psycopg2.Error as e:
        print("Error fetching questions:", e)
        return None  # Indicate failure

    finally:
        if conn:
            cur.close()
            conn.close()  # Ensure the connection is closed




def get_all_answered_questions_by_plant_section(plant_section):
    """
    Retrieves all records from the questions table for a specific plant section
    where checklist_answers is not null or empty.
    """
    print("Fetching records for plant section:", plant_section)
    conn = None
    results = []

    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        if conn is None:
            print("Error: Database connection failed.")
            return None  # Return None if connection fails

        cur = conn.cursor()
       
        # Select query to fetch all records for the specified plant section
        select_query = """
            SELECT id, checklist_answers, location, plant_section, 
                   company_number, operator, operators_location, time_stamp
            FROM public.questions
            WHERE plant_section = %s
            AND 
            (checklist_answers IS NOT NULL
            OR checklist_answers::text != 'null'
            OR checklist_answers::text != '[]'
            OR checklist_answers::text != '{}'
            OR checklist_answers::text != ''
            OR checklist_answers::text != '[null]'
            OR jsonb_array_length(checklist_answers::jsonb) > 0)
        """
        
        cur.execute(select_query, (plant_section,))
        rows = cur.fetchall()

        # Ensure we have column names before processing
        if cur.description:
            columns = [desc[0] for desc in cur.description]  # Get column names
            results = [dict(zip(columns, row)) for row in rows]
        else:
            print("Warning: No column descriptions found.")

        print("Fetched results:", results)
        return results  # Return all records as a list of dictionaries

    except psycopg2.Error as e:
        print("Database error while fetching questions:", e)
        return None  # Indicate failure

    finally:
        # Ensure cursor and connection are closed
        if conn:
            if 'cur' in locals():
                cur.close()
            conn.close()




def get_all_answered_questions():
    """
    Retrieves all records from the questions table where checklist_answers is not null, not 'null', and not empty.
    
    Returns:
        list: A list of dictionaries representing the records, or None if an error occurs.
    """
    conn = None
    results = []

    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        if conn is None:
            print("Failed to connect to the database.")
            return None  # Return None if connection fails

        cur = conn.cursor()

        # Select query to fetch records with valid checklist_answers
        select_query = sql.SQL("""
            SELECT id, checklist_questions, checklist_answers, location, plant_section, 
                   company_number, operator, operators_location, time_stamp
            FROM public.questions
            WHERE checklist_answers IS NOT NULL
              OR checklist_answers != '[null]'
              OR checklist_answers != ''
        """)
        
        cur.execute(select_query)
        rows = cur.fetchall()

        # Convert the results to a list of dictionaries
        columns = [desc[0] for desc in cur.description]  # Get column names
        results = [dict(zip(columns, row)) for row in rows]

        return results  # Return all records as a list of dictionaries

    except psycopg2.Error as e:
        print("Error fetching questions:", e)
        return None  # Indicate failure

    finally:
        if conn:
            cur.close()
            conn.close()  # Ensure the connection is closed


def delete_all_unanswered_questions(plant_section):
    """
    Deletes all records from the questions table for a specific plant section
    where checklist_answers is NULL, 'null', or an empty string.
    
    Args:
        plant_section (str): The plant section to filter the questions by.
    
    Returns:
        int: The number of rows deleted, or None if an error occurs.
    """
    conn = None

    try:
        # Connect to PostgreSQL
        conn = get_db_connection()
        if conn is None:
            print("Failed to connect to the database.")
            return None  # Return None if connection fails

        cur = conn.cursor()

        # Delete query to remove records with unanswered questions
        delete_query = sql.SQL("""
            DELETE FROM public.questions
            WHERE plant_section = %s
              AND (checklist_answers IS NULL 
                  OR checklist_answers = 'null' 
                  OR checklist_answers = '');
        """)
        
        # Execute the delete query
        cur.execute(delete_query, (plant_section,))
        
        # Get the number of rows deleted
        rows_deleted = cur.rowcount
        
        # Commit the transaction
        conn.commit()
        
        return rows_deleted  # Return the number of rows deleted

    except psycopg2.Error as e:
        print("Error deleting unanswered questions:", e)
        if conn:
            conn.rollback()  # Rollback the transaction in case of an error
        return None  # Indicate failure

    finally:
        if conn:
            cur.close()
            conn.close()  # Ensure the connection is closed



def store_answers(id, checklist_answers):
    """
    Store the user's answers in the database.
    
    Args:
        id (int): The ID of the question record to update.
        checklist_answers (str): The user's answers in JSON format.
    
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Convert the list of dictionaries to a JSON string
        checklist_answers = json.dumps(checklist_answers)

        print("checklist_answers db",checklist_answers)
        # Update the checklist_answers column in the database
        cur.execute("""
            UPDATE questions
            SET checklist_answers = %s
            WHERE id = %s
        """, (checklist_answers, id))

        conn.commit()
        return True  # Return True if the update was successful
    except Exception as e:
        print(f"Error storing answers: {e}")
        return False  # Return False if an error occurs
    finally:
        if conn:
            cur.close()
            conn.close()



# def get_all():
#     """Retrieves all records from the questions table."""
#     conn = None
#     results = []

#     try:
#         # Connect to PostgreSQL
#         conn = get_db_connection()
#         if conn is None:
#             return None  # Return None if connection fails

#         cur = conn.cursor()

#         # Select query to fetch all records
#         select_query = """
#         SELECT id, checklist_questions, checklist_answers, location, plant_section, 
#                company_number, operator, operators_location, time_stamp
#         FROM public.questions ;
#         """
        
#         cur.execute(select_query,)
#         rows = cur.fetchall()

#         # Convert the results to a list of dictionaries
#         columns = [desc[0] for desc in cur.description]  # Get column names
#         results = [dict(zip(columns, row)) for row in rows]
#         print("this are questions ",results)
#         return results  # Return all records as a list of dictionaries

#     except psycopg2.Error as e:
#         print("Error fetching questions:", e)
#         return None  # Indicate failure

#     finally:
#         if conn:
#             cur.close()
#             conn.close()  # Ensure the connection is closed
# get_all()






# def delete_all_data_from_all_tables():
#     """
#     Deletes all data from all tables in the database.
#     """
#       # Connect to the database
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
      

#         # Disable foreign key checks (if needed)
#         cursor.execute("SET CONSTRAINTS ALL DEFERRED;")

#         # Get a list of all tables in the database
#         cursor.execute("""
#             SELECT table_name
#             FROM information_schema.tables
#             WHERE table_schema = 'public';
#         """)
#         tables = cursor.fetchall()

#         # Iterate through each table and delete all data
#         for table in tables:
#             table_name = table[0]
#             print(f"Deleting all data from table: {table_name}")

#             # Use TRUNCATE for faster deletion (resets auto-increment counters)
#             cursor.execute(sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;").format(
#                 sql.Identifier(table_name)
#             ))

#         # Commit the transaction
#         conn.commit()
#         print("All data has been deleted from all tables.")

#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         # Close the cursor and connection
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# # Example usage
# delete_all_data_from_all_tables()