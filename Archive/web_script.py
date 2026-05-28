from flask import Flask, render_template, request
from data_filter import fetch_date_range, fetch_department
from db_queries import fetch_latest_results, fetch_no_records

app = Flask(__name__)

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

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html"), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)