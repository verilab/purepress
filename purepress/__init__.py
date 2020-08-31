import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import yaml
from markdown import Markdown
from mdx_gfm import GithubFlavoredMarkdownExtension
from flask import (
    Flask,
    render_template,
    abort,
    current_app,
    redirect,
    url_for,
    Blueprint,
)
from werkzeug.utils import secure_filename

# calculate some folder path
instance_path = os.getenv("INSTANCE_PATH", os.getcwd())
static_folder = os.path.join(instance_path, "static")
template_folder = os.path.join(instance_path, "theme", "templates")
theme_static_folder = os.path.join(instance_path, "theme", "static")

app = Flask(
    __name__,
    instance_path=instance_path,
    template_folder=template_folder,
    static_folder=static_folder,
    instance_relative_config=True,
)

# handle static files for theme
theme_bp = Blueprint(
    "theme",
    __name__,
    static_url_path="/static/theme",
    static_folder=theme_static_folder,
)
app.register_blueprint(theme_bp)

app.config.from_object("purepress.default_config")
app.config.from_pyfile("config.py", silent=True)

markdown = Markdown(extensions=[GithubFlavoredMarkdownExtension()])


@app.context_processor
def inject_site_object() -> Dict[str, Any]:
    return {"site": app.config["SITE_INFO"]}


def load_post(file: str, *, meta_only: bool = False) -> Optional[Dict[str, Any]]:
    try:
        year, month, day, name = os.path.splitext(file)[0].split("-", maxsplit=3)
        year, month, day = int(year), int(month), int(day)
    except ValueError:
        return None
    yml_fm = ""
    md_content = ""
    try:
        with open(
            os.path.join(current_app.instance_path, "posts", file),
            mode="r",
            encoding="utf-8",
        ) as f:
            firstline = f.readline().strip()
            remained = f.read().strip()
            if firstline == "---":
                yml_fm, remained = remained.split("---", maxsplit=1)
                md_content = remained.strip()
            else:
                md_content = "\n\n".join([firstline, remained])
        post: Dict[str, Any] = {
            "file": file,
            "title": name,
            "url": f"/post/{year:0>4d}/{month:0>2d}/{day:0>2d}/{name}/",  # TODO, url_for
        }
        post.update(yaml.load(yml_fm, Loader=yaml.FullLoader))
        if "created" not in post:
            post["created"] = datetime(year=year, month=month, day=day)
        for k in ("created", "updated"):
            if isinstance(post.get(k), date):
                post[k] = datetime.combine(post[k], datetime.min.time())
        for k in ("categories", "tags"):
            if isinstance(post.get(k), str):
                post[k] = [post[k]]
        if not meta_only:
            post["content"] = markdown.convert(md_content)
        return post
    except FileNotFoundError:
        return None


def load_posts(
    *, sort_key: str = "created", sort_reverse: bool = True, meta_only: bool = False
) -> List[Dict[str, Any]]:
    post_files = []
    try:
        post_files = os.listdir(os.path.join(current_app.instance_path, "posts"))
    except FileNotFoundError:
        pass
    posts = []
    for post_file in post_files:
        if not post_file.endswith(".md"):
            continue
        post = load_post(post_file, meta_only=meta_only)
        if post:
            posts.append(post)
    posts.sort(key=lambda x: x.get(sort_key), reverse=sort_reverse)
    return posts


def render_entries(
    entries: List[Dict[str, Any]],
    template: str = "index.html",
    prev_url: Optional[str] = None,
    next_url: Optional[str] = None,
) -> str:
    if not template.endswith(".html"):
        template += ".html"
    return render_template(
        template, entries=entries, prev_url=prev_url, next_url=next_url
    )


def render_entry(entry: Dict[str, Any], template: str) -> str:
    if not template.endswith(".html"):
        template += ".html"
    return render_template(template, entry=entry)


@app.route("/")
def index():
    return index_page(1, from_index=True)


@app.route("/page/<int:page_num>/")
def index_page(page_num, *, from_index: bool = False):
    # do some calculation and handle unexpected cases
    posts_per_page = app.config["POSTS_PER_PAGE_ON_INDEX"]
    posts = load_posts(meta_only=True)  # just load meta data quickly
    post_count = len(posts)
    page_count = (post_count + posts_per_page - 1) // posts_per_page
    if page_num < 1 or (page_num == 1 and not from_index):
        return redirect(url_for("index"), 302)
    if page_num > page_count:
        return render_entries([])

    # prepare pager links
    prev_url, next_url = None, None
    if page_num == 2:
        prev_url = url_for("index")
    elif page_num > 2:
        prev_url = url_for("index_page", page_num=page_num - 1)
    if page_num < page_count:
        next_url = url_for("index_page", page_num=page_num + 1)

    # load posts in the specified range
    begin = (page_num - 1) * posts_per_page
    end = min(post_count, begin + posts_per_page)
    posts_to_render = []
    for i in range(begin, end):
        posts_to_render.append(load_post(posts[i]["file"]))
    return render_entries(posts_to_render, prev_url=prev_url, next_url=next_url)


@app.route("/post/<year>/<month>/<day>/<name>/")
def post(year: str, month: str, day: str, name: str):
    # use secure_filename in case somebody tries to attack
    post = load_post(secure_filename(f"{year}-{month}-{day}-{name}.md"))
    if not post:
        abort(404)
    return render_entry(post, "post")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# if __name__ == "__main__":
#     app.run("127.0.0.1", 8080, debug=True)
#     with app.test_request_context("/"):
#         print(render_index())
