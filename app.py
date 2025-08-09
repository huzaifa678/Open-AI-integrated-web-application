from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from openai import OpenAI
import os
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join("static", "index.html")
    with open(index_path, "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/generate", response_class=HTMLResponse)
async def generate_text(prompt: str = Form(...)):
    
    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
        )
        
        if not response.choices or not response.choices[0].message:
            return HTMLResponse(content="<h1>No response from the model</h1>", status_code=500)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1> An error occured. Please try again </h1>", status_code=500)
    
    summary = summary = response.choices[0].message.content.strip()


    html_result = f"""
    <html>
        <head>
            <title>Generated Text</title>
        </head>
        <body>
            <h1>Your Prompt:</h1>
            <p>{prompt}</p>
            <h2>Generated Text:</h2>
            <p>{summary}</p>
            <a href="/">Generate another</a>
        </body>
    </html>
    """
    return html_result

    