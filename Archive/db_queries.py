import mysql.connector
from mysql.connector import Error

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
    """Fetch latest PASS/FAIL status within the given date range."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        if dept == 'all':
            query = """
                SELECT 
                    name
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
                    name
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
    