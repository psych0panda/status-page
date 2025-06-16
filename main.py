import os
import json
import asyncio
import aiohttp
import asyncpg
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Boss AI Status")
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load components from JSON file
def load_components():
    try:
        with open("components.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "service1": {"name": "", "url": ""},
            "service2": {"name": "", "url": ""}
        }

def save_components(components):
    with open("components.json", "w") as f:
        json.dump(components, f, indent=4)

# Status history
status_history = []

async def check_component(url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return response.status == 200
    except:
        return False

async def check_db(url: str) -> bool:
    try:
        conn = await asyncpg.connect(url)
        await conn.execute('SELECT 1')
        await conn.close()
        return True
    except:
        return False

@app.get("/", response_class=HTMLResponse)
async def status_page(request: Request):
    components = load_components()
    statuses = {}
    for component_id, component in components.items():
        if not component["url"]:  # Skip components without URLs
            statuses[component_id] = {
                "name": component["name"],
                "status": "unknown",
                "last_checked": datetime.now().isoformat()
            }
            continue
            
        if component_id == "db":
            is_healthy = await check_db(component["url"])
        else:
            is_healthy = await check_component(component["url"])
        
        statuses[component_id] = {
            "name": component["name"],
            "status": "operational" if is_healthy else "degraded",
            "last_checked": datetime.now().isoformat()
        }
        
        # Update history
        status_history.append({
            "component": component_id,
            "status": statuses[component_id]["status"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 entries
        if len(status_history) > 100:
            status_history.pop(0)
    
    return templates.TemplateResponse(
        "status.html",
        {
            "request": request,
            "components": components,
            "statuses": statuses,
            "history": status_history[-10:]  # Show last 10 status changes
        }
    )

@app.get("/configure", response_class=HTMLResponse)
async def configure_page(request: Request):
    components = load_components()
    return templates.TemplateResponse(
        "configure.html",
        {
            "request": request,
            "components": components
        }
    )

@app.post("/configure")
async def update_components(request: Request):
    form_data = await request.form()
    components = {}
    
    # Process form data
    service_count = int(form_data.get("service_count", 2))
    for i in range(1, service_count + 1):
        service_id = f"service{i}"
        components[service_id] = {
            "name": form_data.get(f"{service_id}_name", ""),
            "url": form_data.get(f"{service_id}_full_url", "")  # Use the full URL including scheme
        }
    
    save_components(components)
    return RedirectResponse(url="/", status_code=303)

@app.get("/api/status")
async def api_status():
    statuses = {}
    for component_id, component in components.items():
        if component_id == "db":
            is_healthy = await check_db(component["url"])
        else:
            is_healthy = await check_component(component["url"])
        
        statuses[component_id] = {
            "name": component["name"],
            "status": "operational" if is_healthy else "degraded",
            "last_checked": datetime.now().isoformat()
        }
    
    return statuses

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8181) 