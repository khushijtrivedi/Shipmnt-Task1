from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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

mysql = mysql.connector.connect(
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
    if data_json:
        try:
            data = pd.read_json(data_json, orient='split')
            cursor = mysql.cursor()
            for index, row in data.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO Author (name, email, date_of_birth)
                        VALUES (%s, %s, %s)
                        """, (row['Author Name'], row['Email'], datetime.strptime(row['Date of Birth'], '%Y-%m-%d')))
                    author_id = cursor.lastrowid
                    cursor.execute("""
                        INSERT INTO Book (name, isbn_code, author_id)
                        VALUES (%s, %s, %s)
                        """, (row['Book Name'], row['ISBN Code'], author_id))
                    mysql.commit()
                except mysql.connector.Error as e:
                    mysql.rollback()
                    flash(f"An error occurred while inserting data: {e}")
                    return redirect(url_for('index'))

            flash("Data successfully stored in the database!")
        except Exception as e:
            flash(f"An error occurred while reading the file: {e}")
            return redirect(url_for('index'))
    else:
        flash("No data was uploaded.")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
