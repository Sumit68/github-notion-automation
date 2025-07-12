
# import os
# import hmac
# import hashlib
# from fastapi import FastAPI, Header, Request, HTTPException
# from fastapi.responses import JSONResponse
# from dotenv import load_dotenv
# import requests

# load_dotenv()

# NOTION_TOKEN = os.getenv("NOTION_TOKEN")
# NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")
# NOTION_PROJECTS_DB_ID = os.getenv("NOTION_PROJECTS_DATABASE_ID")
# GITHUB_SECRET = os.getenv("GITHUB_SECRET")

# headers = {
#     "Authorization": f"Bearer {NOTION_TOKEN}",
#     "Notion-Version": "2022-06-28",
#     "Content-Type": "application/json"
# }

# app = FastAPI()


# def verify_signature(payload_body, signature_header):
#     mac = hmac.new(GITHUB_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
#     expected_signature = "sha256=" + mac.hexdigest()
#     return hmac.compare_digest(expected_signature, signature_header)


# def get_or_create_project_page(project_name):
#     search_url = f"https://api.notion.com/v1/databases/{NOTION_PROJECTS_DB_ID}/query"
#     payload = {
#         "filter": {
#             "property": "Project Name",
#             "title": {
#                 "equals": project_name
#             }
#         }
#     }
#     response = requests.post(search_url, headers=headers, json=payload)
#     results = response.json().get("results", [])
#     if results:
#         return results[0]["id"]

#     # Create a new project if not found
#     create_url = "https://api.notion.com/v1/pages"
#     data = {
#         "parent": {"database_id": NOTION_PROJECTS_DB_ID},
#         "properties": {
#             "Project Name": {"title": [{"text": {"content": project_name}}]},
#             "Status": {"select": {"name": "In-Progress"}}
#         }
#     }
#     create_response = requests.post(create_url, headers=headers, json=data)
#     if create_response.status_code == 200:
#         return create_response.json().get("id")
#     else:
#         print("Failed to create project page:", create_response.text)
#         return None


# @app.post("/webhook")
# async def webhook(request: Request, x_hub_signature_256: str = Header(None)):
#     payload_body = await request.body()

#     if not verify_signature(payload_body, x_hub_signature_256):
#         raise HTTPException(status_code=401, detail="Unauthorized")

#     payload = await request.json()
#     repo = payload.get("repository", {})
#     repo_name = repo.get("name")
#     branch = payload.get("ref", "").split("/")[-1]

#     project_page_id = get_or_create_project_page(repo_name)

#     commits = payload.get("commits", [])
#     for commit in commits:
#         title = commit.get("message")
#         url = commit.get("url")
#         author = commit.get("author", {}).get("name")
#         date = commit.get("timestamp")

#         page_data = {
#             "parent": {"database_id": NOTION_DB_ID},
#             "properties": {
#                 "Title": {"title": [{"text": {"content": title}}]},
#                 "Type": {"select": {"name": "Commit"}},
#                 "Author": {"select": {"name": author}},
#                 "Repo Name": {"select": {"name": repo_name}},
#                 "URL": {"rich_text": [{"text": {"content": url}}]},
#                 "Date": {"date": {"start": date}},
#                 "Branch": {"select": {"name": branch}}
#             }
#         }

#         if project_page_id:
#             page_data["properties"]["Linked Project"] = {
#                 "relation": [{"id": project_page_id}]
#             }

#         response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=page_data)
#         if response.status_code != 200:
#             print("Failed to create Notion commit page:", response.text)

#     pr = payload.get("pull_request")
#     action = payload.get("action")
#     if pr and action in ["opened", "edited", "reopened"]:
#         pr_title = pr.get("title")
#         pr_url = pr.get("html_url")
#         pr_author = pr.get("user", {}).get("login")
#         pr_created_at = pr.get("created_at")

#         pr_data = {
#             "parent": {"database_id": NOTION_DB_ID},
#             "properties": {
#                 "Title": {"title": [{"text": {"content": pr_title}}]},
#                 "Type": {"select": {"name": "Pull Request"}},
#                 "Author": {"select": {"name": pr_author}},
#                 "Repo Name": {"select": {"name": repo_name}},
#                 "URL": {"rich_text": [{"text": {"content": pr_url}}]},
#                 "Date": {"date": {"start": pr_created_at}},
#                 "Branch": {"select": {"name": branch}}
#             }
#         }

#         if project_page_id:
#             pr_data["properties"]["Linked Project"] = {
#                 "relation": [{"id": project_page_id}]
#             }

#         response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=pr_data)
#         if response.status_code != 200:
#             print("Failed to create Notion PR page:", response.text)

#     return JSONResponse(content={"status": "ok"})

import os
import hmac
import hashlib
from fastapi import FastAPI, Header, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import requests

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_PROJECTS_DB_ID = os.getenv("NOTION_PROJECTS_DATABASE_ID")
GITHUB_SECRET = os.getenv("GITHUB_SECRET")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

app = FastAPI()


def verify_signature(payload_body, signature_header):
    mac = hmac.new(GITHUB_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


def get_or_create_project_page(project_name):
    search_url = f"https://api.notion.com/v1/databases/{NOTION_PROJECTS_DB_ID}/query"
    payload = {
        "filter": {
            "property": "Project Name",
            "title": {
                "equals": project_name
            }
        }
    }
    response = requests.post(search_url, headers=headers, json=payload)
    results = response.json().get("results", [])
    if results:
        return results[0]["id"]

    # Create a new project if not found
    create_url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": NOTION_PROJECTS_DB_ID},
        "properties": {
            "Project Name": {"title": [{"text": {"content": project_name}}]},
            "Status": {"select": {"name": "In-Progress"}},
            "Latest Activity": {"date": {"start": None}}  # Will be updated below
        }
    }
    create_response = requests.post(create_url, headers=headers, json=data)
    if create_response.status_code == 200:
        return create_response.json().get("id")
    else:
        print("Failed to create project page:", create_response.text)
        return None


def update_latest_activity(project_page_id, date):
    url = f"https://api.notion.com/v1/pages/{project_page_id}"
    data = {
        "properties": {
            "Latest Activity": {"date": {"start": date}}
        }
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code != 200:
        print("Failed to update Latest Activity:", response.text)


@app.post("/webhook")
async def webhook(request: Request, x_hub_signature_256: str = Header(None)):
    payload_body = await request.body()

    if not verify_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Unauthorized")

    payload = await request.json()
    repo = payload.get("repository", {})
    repo_name = repo.get("name")
    branch = payload.get("ref", "").split("/")[-1]

    project_page_id = get_or_create_project_page(repo_name)

    commits = payload.get("commits", [])
    for commit in commits:
        title = commit.get("message")
        url = commit.get("url")
        author = commit.get("author", {}).get("name")
        date = commit.get("timestamp")

        page_data = {
            "parent": {"database_id": NOTION_DB_ID},
            "properties": {
                "Title": {"title": [{"text": {"content": title}}]},
                "Type": {"select": {"name": "Commit"}},
                "Author": {"select": {"name": author}},
                "Repo Name": {"select": {"name": repo_name}},
                "URL": {"rich_text": [{"text": {"content": url}}]},
                "Date": {"date": {"start": date}},
                "Branch": {"select": {"name": branch}}
            }
        }

        if project_page_id:
            page_data["properties"]["Linked Project"] = {
                "relation": [{"id": project_page_id}]
            }
            update_latest_activity(project_page_id, date)

        response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=page_data)
        if response.status_code != 200:
            print("Failed to create Notion commit page:", response.text)

    pr = payload.get("pull_request")
    action = payload.get("action")
    if pr and action in ["opened", "edited", "reopened"]:
        pr_title = pr.get("title")
        pr_url = pr.get("html_url")
        pr_author = pr.get("user", {}).get("login")
        pr_created_at = pr.get("created_at")
        pr_branch =  (
            payload.get("ref", "").split("/")[-1]
            or payload.get("pull_request", {}).get("head", {}).get("ref", "")
)
        pr_data = {
            "parent": {"database_id": NOTION_DB_ID},
            "properties": {
                "Title": {"title": [{"text": {"content": pr_title}}]},
                "Type": {"select": {"name": "Pull Request"}},
                "Author": {"select": {"name": pr_author}},
                "Repo Name": {"select": {"name": repo_name}},
                 "URL": {"rich_text": [{"text": {"content": pr_url}}]},
                "Date": {"date": {"start": pr_created_at}},
                "Branch": {"select": {"name": pr_branch}}
            }
        }

        if project_page_id:
            pr_data["properties"]["Linked Project"] = {
                "relation": [{"id": project_page_id}]
            }
            update_latest_activity(project_page_id, pr_created_at)

        response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=pr_data)
        if response.status_code != 200:
            print("Failed to create Notion PR page:", response.text)

    return JSONResponse(content={"status": "ok"})
