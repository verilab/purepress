import os
import json
from datetime import datetime
from typing import Dict, List, Optional

import yaml
from markdown import Markdown
from mdx_gfm import GithubFlavoredMarkdownExtension
from flask import Flask, render_template, abort, current_app

instance_path = os.getenv("INSTANCE_PATH", os.getcwd())
template_folder = os.path.join(instance_path, "theme", "templates")
static_folder = os.path.join(instance_path, "theme", "static")

app = Flask(
    __name__,
    instance_path=instance_path,
    template_folder=template_folder,
    static_folder=static_folder,
)

markdown = Markdown(extensions=[GithubFlavoredMarkdownExtension()])

site: Dict[str, str] = {}
try:
    with open(os.path.join(instance_path, "site.json"), "r", encoding="utf-8") as f:
        site = json.load(f)
except FileNotFoundError:
    pass


@app.context_processor
def inject_site_object():
    return {"site": site}


def load_post(
    year: int, month: int, day: int, name: str, *, convert_content: bool = True
) -> Optional[dict]:
    post_file = f"{year:0>4d}-{month:0>2d}-{day:0>2d}-{name}.md"
    yml_fm = ""
    md_content = ""
    try:
        with open(
            os.path.join(current_app.instance_path, "posts", post_file),
            "r",
            encoding="utf-8",
        ) as f:
            firstline = f.readline().strip()
            remained = f.read().strip()
            if firstline == "---":
                yml_fm, remained = remained.split("---", maxsplit=1)
                md_content = remained.strip()
            else:
                md_content = "\n\n".join([firstline, remained])
        return {
            "title": name,
            "date": datetime(year=year, month=month, day=day),
            "url": f"/post/{year:0>4d}/{month:0>2d}/{day:0>2d}/{name}",
            **yaml.load(yml_fm),
            "content": markdown.convert(md_content) if convert_content else None,
        }
    except FileNotFoundError:
        return None


def load_posts(sort_key: str = "date", sort_reverse: bool = True) -> List[dict]:
    post_files = []
    try:
        post_files = os.listdir(os.path.join(current_app.instance_path, "posts"))
    except FileNotFoundError:
        pass
    posts = []
    for post_file in post_files:
        try:
            filename, ext = os.path.splitext(post_file)
            if ext != ".md":
                continue
            year, month, day, name = filename.split("-", maxsplit=3)
            year, month, day = int(year), int(month), int(day)
            post = load_post(year, month, day, name)
            if post:
                posts.append(post)
        except Exception as e:
            print(e)
    posts.sort(key=lambda x: x.get(sort_key), reverse=sort_reverse)
    return posts


def render_index() -> str:
    posts = load_posts()
    return render_template("index.html", posts=posts)


def render_entry(template: str, entry: dict) -> str:
    template = {"post": "post.html", "page": "page.html"}.get(template, template)
    return render_template(template, entry=entry)


@app.route("/")
def index():
    return render_index()


@app.route("/post/<int:year>/<int:month>/<int:day>/<name>")
def post(year: int, month: int, day: int, name: str):
    post = load_post(year, month, day, name)
    if not post:
        abort(404)
    return render_entry("post", post)


# if __name__ == "__main__":
#     app.run("127.0.0.1", 8080, debug=True)
#     with app.test_request_context("/"):
#         print(render_index())
