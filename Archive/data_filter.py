from datetime import datetime, timedelta


def fetch_date_range(option):
    today = datetime.today()
    if option == "This Week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=7)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    
    elif option == "Last Week":
        start_date = today - timedelta(days=today.weekday()) - timedelta(days=7)
        end_date = start_date + timedelta(days=7)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    else:
        start_date = today.replace(day=1)
        end_date = today
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    
def fetch_department(option):
    if option == "mainline":
        dept = "ATM SMT Placement Machine Assembly"
        return dept
    elif option == "module":
        dept = "ATM SMT Placement Module Assembly"
        return dept
    elif option == "system_acceptance":
        dept = "ATM SMT System Acceptance"
        return dept
    else:
        dept = "all"
        return dept