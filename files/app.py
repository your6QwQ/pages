import itertools as it
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import markdown2

load_dotenv()

FILES_MAX_DIR_SIZE = int(os.getenv("FILES_MAX_DIR_SIZE", "32"))
FILES_ROOT_URL = os.getenv("FILES_ROOT_URL", "/files")
FILES_ROOT_PATH = Path(os.getenv("FILES_ROOT_PATH", "./content")).absolute()

if not FILES_ROOT_PATH.is_dir():
    print("Please check FILES_ROOT_PATH first!")
    exit(-1)

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    favicon_url=None,
    root_path=FILES_ROOT_URL,
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
        parent_path = None if path == '/' else FILES_ROOT_URL + path[:path.rfind('/')]
        file_list = [
            {"url_path": FILES_ROOT_URL + path + ('/' if path[-1] != '/' else '') + item.name, "name": item.name, "size": item.stat().st_size, "is_dir": item.is_dir()}
            for item in sorted(it.islice(os.scandir(result_path), FILES_MAX_DIR_SIZE), key=lambda x: (not x.is_dir(), x.name))
        ]
        return templates.TemplateResponse(
            "index.html",
            {"request": req, "current_path": path, "readme_html": readme_html, "file_list": file_list, "parent_path": parent_path},
        )
    elif result_path.is_file():
        return FileResponse(str(result_path), media_type="application/octet-stream")
        # todo: implement StreamingResponse (for flex Range Request)



