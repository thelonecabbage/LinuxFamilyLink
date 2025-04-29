#!/usr/bin/python3
import subprocess
import datetime
import re

def get_logged_in_time_today(username):
    # Get current date
    today = datetime.date.today()
    today_start = datetime.datetime.combine(today, datetime.time.min)
    now = datetime.datetime.now()

    # Use 'who' to get currently logged-in sessions
    who_output = subprocess.check_output(['who'], text=True)
    
    total_time = datetime.timedelta()

    for line in who_output.strip().split('\n'):
        if not line:
            continue
        parts = line.split()
        if parts[0] != username:
            continue
        
        # Example who line: username pts/0 2025-04-29 08:23 (:0)
        # Parse login time
        try:
            login_date_str = parts[2]
            login_time_str = parts[3]
            login_dt = datetime.datetime.strptime(f"{login_date_str} {login_time_str}", "%Y-%m-%d %H:%M")
        except (IndexError, ValueError):
            continue

        if login_dt.date() == today:
            session_duration = now - login_dt
            total_time += session_duration

    # Use 'last' to get previous sessions from today
    last_output = subprocess.check_output(['last', '-F', username], text=True)
    
    for line in last_output.strip().split('\n'):
        if 'still logged in' in line:
            continue
        if 'wtmp begins' in line:
            break

        # Match the login and logout times
        match = re.search(r'(\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+\s+\d{4})\s+-\s+(\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+\s+\d{4})', line)
        if match:
            login_str, logout_str = match.groups()
            login_dt = datetime.datetime.strptime(login_str, "%a %b %d %H:%M:%S %Y")
            logout_dt = datetime.datetime.strptime(logout_str, "%a %b %d %H:%M:%S %Y")

            if login_dt.date() == today:
                session_duration = logout_dt - login_dt
                total_time += session_duration

    return total_time

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 login_time_today.py <username>")
        exit(1)

    username = sys.argv[1]
    total = get_logged_in_time_today(username)
    max_minutes = None
    kill = False
    bedtime = None
    wakeup = None
    now = datetime.datetime.now()

    for arg in sys.argv[1:]:
        if arg.startswith("max="):
            try:
                max_minutes = int(arg.split('=')[1])
            except ValueError:
                print("Invalid max time format. Use max=<minutes>")
                exit(1)
        if arg == "--kill":
            kill = True
        if arg.startswith("bedtime="):
            try:
                bed, wake = arg.split('=')[1].split('-')
                hour, minute = map(int, bed.split(':'))
                bedtime = datetime.datetime.combine(now.date(), datetime.time(hour, minute))
                hour, minute = map(int, wake.split(':'))
                wakeup =  datetime.datetime.combine(now.date(), datetime.time(hour, minute))
            except ValueError:
                print("Invalid max time format. Use max=<minutes>")
                exit(1)

    total = get_logged_in_time_today(username)
    if max_minutes is not None and total > datetime.timedelta(minutes=max_minutes):
        print(f"Warning: Total time logged in today for {username} exceeds {max_minutes} minutes.")
        if kill:
            print(f"Killing all sessions for {username} due to exceeding max time.")
            subprocess.run(['pkill', '-u', username])
    else:
        print(f"Total time logged in today for {username}: {total}")

    if bedtime and wakeup:
        if now > bedtime or now < wakeup:
            print(f"Warning: {username} is logged in during bedtime hours.")
            if kill:
                print(f"Killing all sessions for {username} due to bedtime.")
                subprocess.run(['pkill', '-u', username])
