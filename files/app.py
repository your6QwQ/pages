import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import markdown2

ROOT_PATH = "/files"

FILES_ROOT_PATH = Path("./content").absolute()

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    favicon_url=None,
    root_path=ROOT_PATH,
)

templates = Jinja2Templates(directory="templates")

logger = logging.getLogger(__name__)

@app.get("/{path:path}", name="path")
async def index(req: Request, path: str):
    path = "/" + path.rstrip("/")
    result_path = (FILES_ROOT_PATH / path.lstrip('/')).resolve()
    if not result_path.is_relative_to(FILES_ROOT_PATH.resolve()):
        raise HTTPException(status_code=403)
    if not result_path.exists():
        raise HTTPException(status_code=404)
    if result_path.is_dir():
        readme_html = None
        if (result_path / "README.md").is_file():
            readme_content = (result_path / "README.md").read_text(encoding="utf-8")
            readme_html = markdown2.markdown(readme_content)
        parent_path = None if path == '/' else ROOT_PATH + path[:path.rfind('/')]
        print(path, path.rfind('/'), parent_path, sep='\n')
        file_list = [
            {"url_path": ROOT_PATH + path + ('/' if path[-1] != '/' else '') + item.name, "name": item.name, "size": item.stat().st_size, "is_dir": item.is_dir()}
            for item in sorted(os.scandir(result_path), key=lambda x: (not x.is_dir(), x.name))
        ]
        print(file_list)
        return templates.TemplateResponse(
            "index.html",
            {"request": req, "current_path": path, "readme_html": readme_html, "file_list": file_list, "parent_path": parent_path},
        )
    elif result_path.is_file():
        return FileResponse(str(result_path), media_type="application/octet-stream")



