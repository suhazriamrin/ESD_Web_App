from flask import Flask, render_template, request, jsonify
from functools import wraps
from data_filter import fetch_date_range, fetch_department
from db_queries import fetch_latest_results, fetch_no_records, delete_user, get_admin_credentials, validate_api_key, fetch_all_namelist, ensure_api_key_column, generate_api_key_for_user, fetch_esd_namelist_this_week, get_connection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize API key column on startup
ensure_api_key_column()

# Decorator to validate API key
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'success': False, 'message': 'API Key is required in X-API-Key header'}), 401
        
        user = validate_api_key(api_key)
        if not user:
            return jsonify({'success': False, 'message': 'Invalid API Key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/printer/')
def printer():
    return render_template("printer.html")

@app.route('/placement/<category>/', methods=['GET', 'POST'])
def placement(category):
    try:
        if request.method =='POST':
            option=request.form["range"]
        else:
            option="This Week"
        
        start_date, end_date = fetch_date_range(option)
        dept = fetch_department(category)

        data = fetch_latest_results(start_date, end_date, dept)
        no_records = fetch_no_records(start_date, end_date, dept)

        return render_template("placement.html",
                            data=data,
                            no_records=no_records,
                            selected=option,
                            category=category)
    except Exception as e:
        print("ERROR:", e)  # log for debugging
        return render_template("server_busy.html"), 500

@app.route('/placement/', methods=['GET', 'POST'])
def placement_default():
    return placement('all')

@app.route('/api/login', methods=['POST'])
def login():
    """Verify admin login from database."""
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    # Fetch admin credentials from database
    admin_user = get_admin_credentials(username, password)
    if admin_user:
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/generate-key', methods=['POST'])
def generate_key():
    """Generate or retrieve API key for authenticated admin user."""
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        # Verify admin credentials
        admin_user = get_admin_credentials(username, password)
        if not admin_user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # Generate new API key for this user
        api_key = generate_api_key_for_user(username)
        if api_key:
            return jsonify({
                'success': True,
                'message': 'API key generated successfully',
                'api_key': api_key,
                'usage': 'Add this to your request headers as: X-API-Key: ' + api_key
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Error generating API key'}), 500
    except Exception as e:
        print("ERROR:", e)
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete-user', methods=['POST'])
def delete_user_route():
    """Delete a user by setting active to 0."""
    try:
        data = request.get_json()
        name = data.get('name', '')
        
        if not name:
            return jsonify({'success': False, 'message': 'User name is required'}), 400
        
        result = delete_user(name)
        if result:
            return jsonify({'success': True, 'message': f'User {name} deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Error deleting user'}), 500
    except Exception as e:
        print("ERROR:", e)
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/update-remarks', methods=['POST'])
def update_remarks():
    """Update remarks for a user."""
    try:
        data = request.get_json()
        name = data.get('name', '')
        remarks = data.get('remarks', '')
        
        if not name:
            return jsonify({'success': False, 'message': 'User name is required'}), 400
        
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            query = "UPDATE zhaji.cards SET remarks = %s WHERE name = %s"
            cursor.execute(query, (remarks, name))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': f'Remarks updated for {name}'})
        else:
            return jsonify({'success': False, 'message': 'Database connection error'}), 500
    except Exception as e:
        print("ERROR:", e)
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/namelist', methods=['GET'])
@require_api_key
def get_namelist():
    """Get ESD testing namelist (results + no records) for this week as JSON."""
    try:
        data = fetch_esd_namelist_this_week()
        if data is None:
            return jsonify({'success': False, 'message': 'Error fetching records'}), 500
        
        return jsonify({
            'success': True,
            'period': data['period'],
            'date_range': {
                'start_date': data['start_date'],
                'end_date': data['end_date']
            },
            'results': {
                'count': len(data['results']),
                'data': data['results']
            },
            'no_records': {
                'count': len(data['no_records']),
                'data': data['no_records']
            },
            'total_count': len(data['results']) + len(data['no_records'])
        }), 200
    except Exception as e:
        print("ERROR:", e)
        return jsonify({'success': False, 'message': str(e)}), 500

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html"), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)