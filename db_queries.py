import mysql.connector
from mysql.connector import Error
import uuid

def get_connection():
    """Establish and return a MySQL database connection."""
    try:
        conn = mysql.connector.connect(
            host="10.12.206.189",
            database="zhaji",
            user="automation",
            password="123456"
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# Define your connection string here
# connection_string = (
#     "DRIVER={ODBC Driver 17 for SQL Server};"
#     "SERVER=atmnts76.atmex.asmpt.com;"
#     "DATABASE=smt_placement;"
#     "UID=automation;"
#     "PWD=123456"
# )

# def get_connection():
#     """Establish and return a database connection."""
#     return pyodbc.connect(connection_string)


def ensure_api_key_column():
    """Ensure api_key column exists in users table."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Try to add the column if it doesn't exist
            query = """
                ALTER TABLE zhaji.users 
                ADD COLUMN api_key VARCHAR(255) UNIQUE NULL
            """
            try:
                cursor.execute(query)
                conn.commit()
                print("api_key column added to users table successfully")
            except Error as e:
                if "Duplicate column name" in str(e):
                    print("api_key column already exists")
                else:
                    raise
            cursor.close()
            conn.close()
        except Error as e:
            print(f"Error ensuring api_key column: {e}")


def generate_api_key_for_user(username):
    """Generate and store a unique API key for a user."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            api_key = str(uuid.uuid4())
            query = "UPDATE zhaji.users SET api_key = %s WHERE username = %s"
            cursor.execute(query, (api_key, username))
            conn.commit()
            cursor.close()
            conn.close()
            return api_key
        except Error as e:
            print(f"Error generating API key: {e}")
            return None
    return None


def fetch_latest_results(start_date, end_date, dept):
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        print(dept)
        if dept == 'all':
            query = """
                WITH Ranked AS (
                SELECT n.name AS Name,
                    CASE WHEN g.test_result = 0 THEN 'FAIL'
                            WHEN g.test_result = 1 THEN 'PASS' END AS Status,
                    g.test_time AS Timestamp,
                    n.department,
                    ROW_NUMBER() OVER (PARTITION BY n.name ORDER BY g.test_time DESC) AS rn,
                    n.note "station",
                    n.remarks
                FROM zhaji.cards AS n
                JOIN zhaji.gate_log AS g
                    ON g.card_number = n.card_number
                WHERE n.active = 1 AND
                g.is_tested = 1
                -- AND
                -- g.test_time BETWEEN %s AND %s
            )
            SELECT name, status, station, timestamp, remarks
            FROM Ranked
            WHERE rn = 1;
            """
            cursor.execute(query, (start_date, end_date))
        else:
            query = """
                WITH Ranked AS (
                SELECT n.name AS Name,
                    CASE WHEN g.test_result = 0 THEN 'FAIL'
                            WHEN g.test_result = 1 THEN 'PASS' END AS Status,
                    g.test_time AS Timestamp,
                    n.department,
                    ROW_NUMBER() OVER (PARTITION BY n.name ORDER BY g.test_time DESC) AS rn,
                    n.note AS station,
                    n.remarks

                FROM zhaji.cards AS n
                JOIN zhaji.gate_log AS g
                    ON g.card_number = n.card_number
                WHERE n.active = 1 AND
                g.is_tested = 1
                AND g.test_time BETWEEN %s AND %s
            )
            SELECT name, status, station, timestamp, remarks
            FROM Ranked
            WHERE rn = 1 AND department = %s;
            """
            cursor.execute(query, (start_date, end_date, dept))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results


def fetch_no_records(start_date, end_date, dept):
    print(start_date)
    print(end_date)
    """Fetch records with no test results within the given date range."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        if dept == 'all':
            query = """
                SELECT 
                    name,
                    note AS station,
                    remarks
                FROM
                    zhaji.cards
                WHERE
                    active = 1
                        AND name NOT IN (SELECT DISTINCT
                            name
                        FROM
                            cards c
                                JOIN
                            gate_log g ON c.card_number = g.card_number
                        WHERE
                            c.active = 1
                                AND test_time BETWEEN %s AND %s
                                AND is_tested = 1);
            """
            cursor.execute(query, (start_date, end_date))
        else:
            query = """
                SELECT 
                    name,
                    note AS station,
                    remarks
                FROM
                    zhaji.cards
                WHERE
                    active = 1
                        AND name NOT IN (SELECT DISTINCT
                            name
                        FROM
                            cards c
                                JOIN
                            gate_log g ON c.card_number = g.card_number
                        WHERE
                            c.active = 1
                                AND test_time BETWEEN %s AND %s
                                AND is_tested = 1)
                        AND department = %s;
            """
            cursor.execute(query, (start_date, end_date, dept))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results


def delete_user(name):
    """Set user's active status to 0 by name."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "UPDATE zhaji.cards SET active = 0 WHERE name = %s"
            cursor.execute(query, (name,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error as e:
            print(f"Error deleting user: {e}")
            return False
    return False


def add_user(name, badge_no, card_no, department):
    """Add a new user to the cards table, or update if already exists."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Pad source_card with zeros to match format (e.g., "275502" -> "000275502")
            source_card = card_no.zfill(10)  # Pad to 10 digits
            
            # Convert source_card (decimal) to hex for card_number
            card_number_decimal = int(source_card)
            card_number_hex = format(card_number_decimal, '08X')  # 8 hex digits
            
            # Get current timestamp
            from datetime import datetime
            created_time = datetime.now()
            
            # Find the next card_counter (fill gaps first, then use highest + 1)
            cursor.execute("SELECT MAX(card_counter) FROM zhaji.cards WHERE card_counter > 0")
            max_counter_result = cursor.fetchone()
            max_counter = max_counter_result[0] if max_counter_result[0] else 0
            
            # Find the lowest gap in card_counter sequence
            gap_query = """
                SELECT MIN(t1.card_counter + 1) AS next_counter
                FROM zhaji.cards t1
                LEFT JOIN zhaji.cards t2 ON t1.card_counter + 1 = t2.card_counter
                WHERE t1.card_counter > 0 AND t2.card_counter IS NULL
                HAVING MIN(t1.card_counter + 1) <= %s
            """
            cursor.execute(gap_query, (max_counter,))
            gap_result = cursor.fetchone()
            
            if gap_result and gap_result[0]:
                # Use the lowest gap
                next_counter = gap_result[0]
            else:
                # Use highest + 1
                next_counter = max_counter + 1
            
            # Use INSERT ... ON DUPLICATE KEY UPDATE to handle existing cards
            query = """
                INSERT INTO zhaji.cards 
                (card_number, card_category, name, job_number, department, gender, note, 
                 created_time, card_counter, classes, source_card, active, active_log, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = %s,
                    job_number = %s,
                    department = %s,
                    card_counter = CASE WHEN card_counter = 0 THEN %s ELSE card_counter END,
                    active = 1
            """
            cursor.execute(query, (
                card_number_hex,      # card_number (hex)
                '1',                  # card_category (default)
                name,                 # name
                badge_no,             # job_number
                department,           # department
                '',                   # gender (default empty)
                '',                   # note (default empty)
                created_time,         # created_time (now)
                next_counter,         # card_counter (next available)
                '',                   # classes (default empty)
                source_card,          # source_card (padded)
                1,                    # active (default 1)
                '',                   # active_log (default empty)
                '3',                  # status (default 3)
                # UPDATE values
                name,                 # name (for update)
                badge_no,             # job_number (for update)
                department,           # department (for update)
                next_counter,         # card_counter (for update if 0)
                ''                    # remarks
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Error as e:
            print(f"Error adding user: {e}")
            return False
    return False


def get_admin_credentials(username, password):
    """Fetch admin credentials from zhaji.users table by username."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM zhaji.users WHERE username = %s and password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result
        except Error as e:
            print(f"Error fetching admin credentials: {e}")
            return None
    return None


def validate_api_key(api_key):
    """Validate API key from zhaji.users table."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, username FROM zhaji.users WHERE api_key = %s AND api_key IS NOT NULL LIMIT 1"
            cursor.execute(query, (api_key,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result
        except Error as e:
            print(f"Error validating API key: {e}")
            return None
    return None


def fetch_all_namelist():
    """Fetch all active cards/namelist from database."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    id,
                    card_number,
                    name,
                    job_number,
                    department,
                    gender,
                    card_counter,
                    source_card,
                    status,
                    created_time
                FROM zhaji.cards
                WHERE active = 1
                ORDER BY card_counter ASC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except Error as e:
            print(f"Error fetching namelist: {e}")
            return None
    return None


def fetch_esd_namelist_this_week():
    """Fetch ESD testing namelist (results + no records) for this week."""
    from data_filter import fetch_date_range
    
    start_date, end_date = fetch_date_range("This Week")
    conn = get_connection()
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Fetch records with test results (PASS/FAIL) for this week
            results_query = """
                WITH Ranked AS (
                SELECT n.name AS name,
                    CASE WHEN g.test_result = 0 THEN 'FAIL'
                            WHEN g.test_result = 1 THEN 'PASS' END AS status,
                    g.test_time AS timestamp,
                    n.department,
                    ROW_NUMBER() OVER (PARTITION BY n.name ORDER BY g.test_time DESC) AS rn
                FROM zhaji.cards AS n
                JOIN zhaji.gate_log AS g
                    ON g.card_number = n.card_number
                WHERE n.active = 1 AND
                g.is_tested = 1
                AND
                g.test_time BETWEEN %s AND %s
            )
            SELECT name, status, timestamp
            FROM Ranked
            WHERE rn = 1
            ORDER BY name ASC;
            """
            cursor.execute(results_query, (start_date, end_date))
            results = cursor.fetchall()
            
            # Fetch records with no test records for this week
            no_records_query = """
                SELECT 
                    name
                FROM
                    zhaji.cards
                WHERE
                    active = 1
                        AND name NOT IN (SELECT DISTINCT
                            name
                        FROM
                            zhaji.cards c
                                JOIN
                            zhaji.gate_log g ON c.card_number = g.card_number
                        WHERE
                            c.active = 1
                                AND test_time BETWEEN %s AND %s
                                AND is_tested = 1)
                ORDER BY name ASC;
            """
            cursor.execute(no_records_query, (start_date, end_date))
            no_records = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                'results': results,
                'no_records': no_records,
                'period': 'This Week',
                'start_date': start_date,
                'end_date': end_date
            }
        except Error as e:
            print(f"Error fetching ESD namelist: {e}")
            return None
    return None
    