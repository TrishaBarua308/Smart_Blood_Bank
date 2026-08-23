from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# SQL
def init_db():
    conn = sqlite3.connect('blood_bank.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            area TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

init_db()



@app.route('/')
def home():
    return render_template('index.html')

# 1. Register Donor
@app.route('/register', methods=['POST'])
def register_donor():
    data = request.get_json()
    name = data['name']
    blood_group = data['blood_group']
    area = data['area']
    phone = data['phone']
    
    try:
        conn = sqlite3.connect('blood_bank.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO donors (name, blood_group, area, phone) VALUES (?, ?, ?, ?)", 
                       (name, blood_group, area, phone))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Donor registered successfully into SQL database!"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "This phone number is already registered!"})

# 2. Search Donors (By Group & Area)
@app.route('/search', methods=['GET'])
def search_blood():
    blood_group = request.args.get('blood_group')
    area = request.args.get('area')  
    
    conn = sqlite3.connect('blood_bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, blood_group, area, phone FROM donors WHERE blood_group = ? AND area LIKE ?", 
                   (blood_group, f"%{area}%"))
    
    rows = cursor.fetchall()
    conn.close()
    
    donor_list = []
    for row in rows:
        donor_list.append({"name": row[0], "blood_group": row[1], "area": row[2], "phone": row[3]})
        
    return jsonify(donor_list)

# 3. Get Single Profile (By Phone)
@app.route('/get-profile', methods=['GET'])
def get_profile():
    phone = request.args.get('phone')
    
    conn = sqlite3.connect('blood_bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, blood_group, area, phone FROM donors WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({"status": "success", "profile": {"name": row[0], "blood_group": row[1], "area": row[2], "phone": row[3]}})
    else:
        return jsonify({"status": "error", "message": "No profile found with this phone number!"})

# 4. Update Profile
@app.route('/update', methods=['PUT'])
def update_donor():
    data = request.get_json()
    phone = data['phone']
    new_name = data['name']
    new_area = data['area']
    
    conn = sqlite3.connect('blood_bank.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE donors SET name = ?, area = ? WHERE phone = ?", (new_name, new_area, phone))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    
    if changes > 0:
        return jsonify({"status": "success", "message": "Donor profile updated successfully!"})
    else:
        return jsonify({"status": "error", "message": "Phone number not found!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')