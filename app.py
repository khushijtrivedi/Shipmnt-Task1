from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import pandas as pd
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'shipmnt'

def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file and (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        try:
            data = pd.read_excel(file)
            data.fillna("", inplace=True)  # Handle missing values
            # Convert DataFrame to JSON
            data_json = data.to_json(orient='split')
            return render_template('view.html', data_json=data_json)
        except Exception as e:
            flash(f"An error occurred while processing the file: {e}")
            return redirect(url_for('index'))
    else:
        flash("Invalid file format! Please upload an Excel file.")
        return redirect(url_for('index'))

@app.route('/confirm', methods=['POST'])
def confirm_data():
    data_json = request.form.get('data')
    connection = None
    cursor = None
    try:
        if data_json:
            data = pd.read_json(data_json, orient='split')
            connection = get_db_connection()
            cursor = connection.cursor()
            for index, row in data.iterrows():
                try:
                    # Convert 'Date of Birth' to datetime object
                    date_of_birth = row['Date of Birth']
                    
                    # Check if date_of_birth is an integer (timestamp)
                    if isinstance(date_of_birth, int):
                        date_of_birth = datetime.fromtimestamp(date_of_birth / 1000)
                    elif isinstance(date_of_birth, str):
                        try:
                            # Try parsing as a string if it matches a date format
                            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d')
                        except ValueError:
                            # Handle other possible date formats or conversions
                            date_of_birth = datetime.strptime(date_of_birth, '%m/%d/%Y')

                    try:
                        cursor.execute("""
                            INSERT INTO Author (name, email, date_of_birth)
                            VALUES (%s, %s, %s)
                            """, (row['Author Name'], row['Email'], date_of_birth))
                        author_id = cursor.lastrowid
                    except mysql.connector.IntegrityError as e:
                        if e.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                            # Handle duplicate entry error
                            cursor.execute("SELECT id FROM Author WHERE email = %s", (row['Email'],))
                            result = cursor.fetchone()
                            author_id = result[0]
                        else:
                            raise

                    cursor.execute("""
                        INSERT INTO Book (name, isbn_code, author_id)
                        VALUES (%s, %s, %s)
                        """, (row['Book Name'], row['ISBN Code'], author_id))
                    
                    connection.commit()
                except mysql.connector.Error as e:
                    connection.rollback()
                    flash(f"An error occurred while inserting data: {e}")
                    return redirect(url_for('index'))

            flash("Data successfully stored in the database!")
        else:
            flash("No data was uploaded.")
    
    except Exception as e:
        flash(f"An error occurred while processing the data: {e}")
        return redirect(url_for('index'))
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
