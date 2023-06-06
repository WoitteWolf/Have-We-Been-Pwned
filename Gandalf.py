import requests
import urllib
import time
from datetime import datetime
HIBP_API_KEY = "your key here"
OKTA_DOMAIN = "your domain here"
OKTA_API_TOKEN = "Another key, but different"
EMAILS = ["emails@email.com", "email2@stuff.com"]
HIBP_headers = {
    "hibp-api-key": HIBP_API_KEY,
    "user-agent": "Gandalf",
}
OKTA_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"SSWS {OKTA_API_TOKEN}",
}
params = {
    "truncateResponse": "false"
}
for email in EMAILS:
    print("\n" + "=" * 40)
    print(f"Checking email: {email}")
    print("=" * 40 + "\n")
    ACCOUNT_EMAIL = urllib.parse.quote(email)
    # Initialize latest_breach_date
    latest_breach_date = None
    # HIBP request for breaches
    response = requests.get(
        f"https://haveibeenpwned.com/api/v3/breachedaccount/{ACCOUNT_EMAIL}",
        headers=HIBP_headers,
        params=params
    )
    if response.status_code == 200:
        breaches = response.json()
        for breach in breaches:
            breach_name = breach.get('Name', 'No name provided')
            breach_date = breach.get('BreachDate', 'No date provided')
            breach_desc = breach.get('Description', 'No description provided')
            print(f"Breach: {breach_name}\nBreach Date: {breach_date}\nDescription: {breach_desc}\n")
            if latest_breach_date is None or breach_date > latest_breach_date:
                latest_breach_date = breach_date
        print("Latest breach date: ", latest_breach_date)
    elif response.status_code == 404:
        print("No breaches detected")
    else:
        print("An error occurred: ", response.status_code)
    
    # Okta request for last password change
    response = requests.get(
        f"https://{OKTA_DOMAIN}/api/v1/users/{email}",
        headers=OKTA_headers,
    )
    if response.status_code == 200:
        user_data = response.json()
        password_changed = user_data.get('passwordChanged', 'No data')
        print(f"Last password change: {password_changed}")
        
        # Convert dates to datetime objects for comparison
        if password_changed != 'No data':
            password_changed_date = datetime.strptime(password_changed, "%Y-%m-%dT%H:%M:%S.%fZ").date()
        if latest_breach_date is not None:
            latest_breach_date = datetime.strptime(latest_breach_date, "%Y-%m-%d").date()
        
        # Check if password was changed after the latest breach
        if latest_breach_date and password_changed_date and password_changed_date < latest_breach_date:
            print(f"\n{email}: Change password\n")
        else:
            print(f"\n{email}: No action required\n")
    else:
        print("An error occurred while fetching Okta data: ", response.status_code)
    
    time.sleep(6)  # To comply with HIBP rate limiting
