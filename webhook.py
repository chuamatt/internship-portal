# Import necessary default libraries
import os
import json
import re
import time
import logging
from datetime import datetime

# Import external dependencies
import requests
# For MRT distance calculation
import pandas as pd
from geopy.distance import geodesic

# It is a good practice to use CaseInsensitiveDict to store HTTP headers (which are case-insensitive)
# This avoids future typos or mistakes (like duplicate keys) when using dictionaries
# In a CaseInsensitiveDict, keys are all converted to lowercase
from requests.structures import CaseInsensitiveDict

# Configure logging
# The logging level can be set to DEBUG, INFO, WARNING, ERROR, or CRITICAL
# Configuring the logging level would allow us to filter out messages that are not relevant to us
# In this case, we set the logging level to INFO to filter out DEBUG messages
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s.%(msecs)03d L%(lineno)d PID%(process)d TID%(thread)d\n%(message)s",
    datefmt="%a %d %b %Y %H:%M:%S"
)


# Set base URL for Internship API
# BASE_URL = os.environ.get("BASE_URL")
BASE_URL = "https://internship.sp.edu.sg/roboroy/api/v1"

# Set HTTP headers using CaseInsensitiveDict
headers = CaseInsensitiveDict()
headers["cookie"] = os.environ.get("COOKIE")

if "connect.sid=" not in headers["cookie"]:
    headers["cookie"] = "connect.sid=" + headers["cookie"]

# Validate auth cookie using regex
# if re.fullmatch(r"connect\.sid=s%3A.{32}\..{45}", headers["cookie"]) is None:
#     logging.error("Invalid auth cookie")
#     exit(1)
# Commented out because doesn't seem to be reliable

WEBHOOK_ID = os.environ.get("WEBHOOK_ID")
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN")
WEBHOOK_URL = f"https://discord.com/api/webhooks/{WEBHOOK_ID}/{WEBHOOK_TOKEN}"

endpoint = "/jobs/list"

# Error handling for graceful exit
jobs_list = []
try:
    # Make HTTP request
    resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    logging.info("IntsPortal HTTP Request Status: %s, URL: %s", resp.status_code, resp.url)
    # Parse JSON response and store list of jobs
    jobs_list = json.loads(resp.text)
    jobs_list = jobs_list.get("jobs")
    if jobs_list is None:
        logging.error("No jobs found. Please check your IntsPortal Auth Cookie and try again.")
        exit(1)
except requests.ConnectionError:
    # Handle ConnectionError
    logging.error("There was a problem with the network connection. Please try again later.")
    exit(1)
except requests.Timeout:
    # Handle Timeout
    logging.error("The request took too long to complete. Please try again later.")
    exit(1)

# Read MRT station names from CSV file
with open('mrt.json', 'r') as mrt_file:
    list_of_mrt = json.load(mrt_file)

# Use the OneMap API to obtain the (lat, long) coordinates of each MRT station.
# It is also possible to use the Google Maps API to achieve this, but that requires a API key.
# Simply put, the OneMap API is easier to use (and possibly has the latest data, cuz you know, Government).
mrt_lat = []
mrt_long = []

for i in range(0, len(list_of_mrt)):
    query_address = list_of_mrt[i]
    query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(
        query_address) + '&returnGeom=Y&getAddrDetails=Y'
    resp = requests.get(query_string)
    logging.info("OneMap HTTP Request Status (%s/%s): %s, URL: %s", i+1, len(list_of_mrt), resp.status_code, resp.url)

    data_mrt = json.loads(resp.content)

    if data_mrt['found'] != 0:
        mrt_lat.append(data_mrt["results"][0]["LATITUDE"])
        mrt_long.append(data_mrt["results"][0]["LONGITUDE"])

    # This is unlikely to trigger, but just in case
    else:
        mrt_lat.append('NotFound')
        mrt_lat.append('NotFound')
        logging.warning("No Results")

# Store this information in a Pandas dataframe
# Essentially, this is a two-dimensional table
mrt_location = pd.DataFrame({
    'MRT': list_of_mrt,
    'Latitude': mrt_lat,
    'Longitude': mrt_long
})

# TODO: Store this dataframe in a file instead of requesting 9999 urls every time

# Distance to nearest MRT
list_of_dist_mrt = []
min_dist_mrt = ""

# List of MRT Coordinates in Singapore
mrt_lat = mrt_location['Latitude']
mrt_long = mrt_location['Longitude']

list_of_mrt_coordinates = []
# example: [(lat,long),(lat,long), (lat,long)]

for lat, long in zip(mrt_lat, mrt_long):
    list_of_mrt_coordinates.append((lat, long))

# Check posted interns
with open('interns.json', 'r') as interns_file:
    interns = json.load(interns_file)

for job_index, job in enumerate(jobs_list, start=1):
    # Pass if no applications
    if job.get("totalApplications") == 0:
        continue

    # Get job information
    curr_time_ms = round(time.time() * 1000)
    resp = requests.get(f"{BASE_URL}/jobs/{job.get('_id')}?_={curr_time_ms}&jobId={job.get('_id')}", headers=headers)
    logging.info("IntsPortal HTTP Request Status (%s/%s): %s, URL: %s", job_index, len(jobs_list), resp.status_code, resp.url)
    test1 = json.loads(resp.text)
    test2 = json.loads(resp.text).get("jobs")
    job_details = json.loads(resp.text).get("jobs")[0]

    # Pass if no successful applications
    if job_details.get("dashboard").get("hiredApplns") == 0:
        continue

    # This is to avoid Discord raising an error because the URL field expects a URL (ie. with http:// or https://)
    if 'http' in job_details.get('company').get('website'):
        company_website = job_details.get('company').get('website')
    else:
        company_website = 'https://' + job_details.get('company').get('website')

    # Start constructing webhook message
    job_interns = []

    webhook_data = {
        "content": None,
        "embeds": [
            {
                "title": f"{job_details.get('jobname').get('nameName').title()}",
                "url": f"https://internship.sp.edu.sg/app/campus/candidate/job/{job.get('_id')}",
                "description": f":date: **Posted:** {datetime.strptime(job_details.get('approvedList')[0].get('updatedDate'), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%a %d %b %Y')}\n:moneybag: **Salary:** ${job_details.get('maxSalary')}\n:busts_in_silhouette: **Vacancies:** {job_details.get('vacancy')}\n:envelope_with_arrow: **Applications:** {job_details.get('dashboard').get('totalApplications')}",
                "color": 65280,
                "fields": [],
                "author": {
                    "name": f"{job_details.get('company').get('displayCompanyName')}",
                    "url": f"{company_website}"
                }
            }
        ],
        "username": "Congratulations, you got an internship!",
        "avatar_url": "https://cdn.iconscout.com/icon/free/png-256/celebration-party-popper-tada-decoration-christmas-38099.png",
        "attachments": []
    }

    # Get list of successful applicants
    for app_index, intern_details in enumerate(job_details.get('dashboard').get('hiredApplnsArray'), start=1):
        # It is possible that the details of the intern has been published previously,
        # so compare the intern's ID with the list of interns we have already scraped.
        if int(intern_details.get('applicantStudentProfile').get('studentUniversityId')) in interns:
            continue
        else:
            job_interns.append(int(intern_details.get('applicantStudentProfile').get('studentUniversityId')))
        webhook_data["embeds"][0]["fields"].append({
            "name": f"Intern #{app_index}",
            "value": f"{':mens:' if intern_details.get('applicantProfile').get('genderId') == 1 else ':womens:'} **Name:** {intern_details.get('applicantProfile').get('firstName')}\n:email: **Email:** {intern_details.get('applicantProfile').get('email')}\n:id: **ID:** {intern_details.get('applicantStudentProfile').get('studentUniversityId')}\n:date: **Offered:** {datetime.strptime(intern_details.get('applicationData').get('shortlistedDate'), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%a %d %b %Y')}\n:passport_control: **Residency:** {intern_details.get('applicantProfile').get('residentStatus')}\n{'<:linkedin:1051501235171229776> **LinkedIn:** ' if intern_details.get('applicantProfile').get('linkedin') != None else ''}{intern_details.get('applicantProfile').get('linkedin') if intern_details.get('applicantProfile').get('linkedin') != None else ''}",
            "inline": True
        })

    if len(job_interns) == 0:
        continue

    webhook_data["embeds"][0]["fields"].append({
        "name": "Company",
        "value": f":bust_in_silhouette: **Name:** {job_details.get('user').get('firstname')} {job_details.get('user').get('lastname') if job_details.get('user').get('lastname') != ' ' else ''}\n:briefcase: **Role:** {job_details.get('user').get('designation')}\n:email: **Email:**  {job_details.get('user').get('email')}\n:telephone: **Contact:**  {job_details.get('user').get('contactnumber')}"
    })

    # It's address time!
    query_string = 'https://developers.onemap.sg/commonapi/search?searchVal=' + str(
        job_details.get('office').get('address').get('zipcode')) + '&returnGeom=Y&getAddrDetails=Y'
    resp = requests.get(query_string)
    logging.info("OneMap HTTP Request Status: %s, URL: %s", resp.status_code, resp.url)
    address_info = json.loads(resp.text).get('results')[0]
    origin = (address_info.get('LATITUDE'), address_info.get('LONGITUDE'))

    # Get distance to nearest MRT
    list_of_dist_mrt = []
    for destination in range(0, len(list_of_mrt_coordinates)):
        list_of_dist_mrt.append(geodesic(origin, list_of_mrt_coordinates[destination]).meters)
    shortest = (min(list_of_dist_mrt))
    min_dist_mrt = shortest
    min_mrt = list_of_mrt[list_of_dist_mrt.index(float(min_dist_mrt))]

    # Present all that address info nicely
    webhook_data["embeds"][0]["fields"].append({
        "name": "Location",
        "value": f":map: **Address:**\n> {address_info.get('BUILDING')}\n> {address_info.get('BLK_NO')} {address_info.get('ROAD_NAME')}\n> SINGAPORE {address_info.get('POSTAL')}\n:station: **Nearest MRT:**\n> {min_mrt} \n> {round(min_dist_mrt)}m"
    })

    # Send webhook message
    resp = requests.post(WEBHOOK_URL, json=webhook_data)
    logging.debug(json.dumps(webhook_data))
    logging.info("Discord Webhook HTTP Request Status: %s, URL: %s", resp.status_code, resp.url)

    # Update interns list
    interns = interns + job_interns

# Update interns file
with open('interns.json', 'w') as interns_file:
    interns_file.write(json.dumps(interns))





