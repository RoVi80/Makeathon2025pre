import requests
import os
from datetime import datetime, timedelta

# Paste your API key here (or use os.getenv)
api_key = "sxx"

# Set date range: last 30 days
end_date = datetime.utcnow().date()
start_date = end_date - timedelta(days=180)

# Check usage
usage_url = f"https://api.openai.com/v1/dashboard/billing/usage?start_date={start_date}&end_date={end_date}"
sub_url = "https://api.openai.com/v1/dashboard/billing/subscription"

headers = {"Authorization": f"Bearer {api_key}"}

# Get usage
usage_response = requests.get(usage_url, headers=headers)
sub_response = requests.get(sub_url, headers=headers)

if usage_response.status_code == 200 and sub_response.status_code == 200:
    used = usage_response.json()["total_usage"] / 100  # cents → USD
    limit = sub_response.json()["hard_limit_usd"]
    print(f"💸 You’ve used ${used:.2f} of your ${limit:.2f} credit.")
else:
    print("⚠️ Something went wrong.")
    print("Usage response:", usage_response.status_code, usage_response.text)
    print("Sub response:", sub_response.status_code, sub_response.text)