import os
import re
import functools
import xml.etree.ElementTree as etree
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional

import yaml
import pytz
import markdown.extensions
import markdown.treeprocessors
from markdown import Markdown
from mdx_gfm import GithubFlavoredMarkdownExtension
from flask import (
    Flask,
    render_template,
    abort,
    redirect,
    url_for,
    Blueprint,
    send_from_directory,
    request,
    make_response,
)
from werkzeug.security import safe_join
from feedgen.feed import FeedGenerator

# calculate some folder path
instance_path = os.getenv("INSTANCE_PATH", os.getcwd())
static_folder = os.path.join(instance_path, "static")
template_folder = os.path.join(instance_path, "theme", "templates")
theme_static_folder = os.path.join(instance_path, "theme", "static")
posts_folder = os.path.join(instance_path, "posts")
pages_folder = os.path.join(instance_path, "pages")
raw_folder = os.path.join(instance_path, "raw")

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

# load configurations
app.config.from_object("purepress.default_config")
app.config.from_pyfile("config.py", silent=True)

# prepare markdown parser
class HookImageSrcProcessor(markdown.treeprocessors.Treeprocessor):
    def run(self, root: etree.Element):
        # TODO: hook all relative links
        for el in root.iter("img"):
            src = el.get("src", "")
            static_url = url_for("static", filename="", _external=True)
            el.set("src", re.sub(r"^/static/", static_url, src))


class HookImageSrcExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md) -> None:
        md.treeprocessors.register(HookImageSrcProcessor(), "hook-image-src", 5)


md = Markdown(extensions=[GithubFlavoredMarkdownExtension(), HookImageSrcExtension()])


# inject site info into template context
@app.context_processor
def inject_site_object() -> Dict[str, Any]:
    return {"site": app.config["SITE_INFO"]}


def load_entry(fullpath: str, *, meta_only: bool = False) -> Optional[Dict[str, Any]]:
    # read frontmatter and content
    frontmatter, content = "", ""
    try:
        with open(fullpath, mode="r", encoding="utf-8") as f:
            firstline = f.readline().strip()
            remained = f.read().strip()
            if firstline == "---":
                frontmatter, remained = remained.split("---", maxsplit=1)
                content = remained.strip()
            else:
                content = "\n\n".join([firstline, remained])
    except FileNotFoundError:
        return None
    # construct the entry object
    entry: Dict[str, Any] = yaml.load(frontmatter, Loader=yaml.FullLoader) or {}
    # ensure datetime fields are real datetime
    for k in ("created", "updated"):
        if isinstance(entry.get(k), date) and not isinstance(entry.get(k), datetime):
            entry[k] = datetime.combine(entry[k], datetime.min.time())
    # ensure tags and categories are lists
    for k in ("categories", "tags"):
        if isinstance(entry.get(k), str):
            entry[k] = [entry[k]]
    # if should, convert markdown content to html
    if not meta_only:
        entry["content"] = md.convert(content)
    return entry


def load_post(filename: str, meta_only: bool = False) -> Optional[Dict[str, Any]]:
    # parse the filename (yyyy-MM-dd-post-title.md)
    try:
        year, month, day, name = os.path.splitext(filename)[0].split("-", maxsplit=3)
        year, month, day = int(year), int(month), int(day)
    except ValueError:
        return None
    # load post entry
    fullpath = safe_join(posts_folder, filename)
    if fullpath is None:
        return None
    post = load_entry(fullpath, meta_only=meta_only)
    if post is None:  # note that post may be {}
        return None
    # add some fields
    post["filename"] = filename
    post["url"] = url_for(
        ".post",
        year=f"{year:0>4d}",
        month=f"{month:0>2d}",
        day=f"{day:0>2d}",
        name=name,
    )
    # ensure *title* field
    if "title" not in post:
        post["title"] = " ".join(name.split("-"))
    # ensure *created* field
    if "created" not in post:
        post["created"] = datetime(year=year, month=month, day=day)
    return post


def load_posts(*, meta_only: bool = False) -> List[Dict[str, Any]]:
    try:
        post_files = os.listdir(posts_folder)
    except FileNotFoundError:
        return []
    posts = []
    for post_file in post_files:
        if not post_file.endswith(".md"):
            continue
        post = load_post(post_file, meta_only=meta_only)
        if post:
            posts.append(post)
    posts.sort(key=lambda x: x.get("created"), reverse=True)
    return posts


def load_page(rel_url: str) -> Optional[Dict[str, Any]]:
    # convert relative url to full file path
    pathnames = rel_url.split("/")
    fullpath = safe_join(pages_folder, *pathnames)
    if fullpath is None:
        return None
    if fullpath.endswith(os.path.sep):  # /foo/bar/
        fullpath = os.path.join(fullpath, "index.md")
    elif fullpath.endswith(".html"):  # /foo/bar.html
        fullpath = os.path.splitext(fullpath)[0] + ".md"
    else:  # /foo/bar
        fullpath += ".md"
    # load page entry
    page = load_entry(fullpath)
    if page is None:
        return None
    page["url"] = url_for(".page", rel_url=rel_url)
    # ensure *title* field
    if "title" not in page:
        name = os.path.splitext(os.path.basename(fullpath))[0]
        page["title"] = " ".join(name.split("-"))
    return page


def templated(template: str) -> Callable:
    if not template.endswith(".html"):
        template += ".html"

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if isinstance(res, dict):
                return render_template([f"custom/{template}", template], **res)
            return res

        return wrapper

    return decorator


@app.route("/")
def index():
    # the logic is the same as /page/1/, just reuse it
    return index_page(1, from_index=True)


@app.route("/page/<int:page_num>/")
@templated("index")
def index_page(page_num, *, from_index: bool = False):
    # do some calculation and handle unexpected cases
    posts_per_page = app.config["POSTS_PER_PAGE_ON_INDEX"]
    posts = load_posts(meta_only=True)  # just load meta data quickly
    post_count = len(posts)
    page_count = (post_count + posts_per_page - 1) // posts_per_page
    if page_num == 1 and not from_index:
        # redirect /page/1/ to /
        return redirect(url_for("index"), 302)
    if page_num < 1 or page_num > page_count:
        abort(404)

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
        posts_to_render.append(load_post(posts[i]["filename"]))
    return {
        "entries": posts_to_render,
        "pager": {"prev_url": prev_url, "next_url": next_url},
    }


@app.route("/post/<year>/<month>/<day>/<name>/")
@templated("post")
def post(year: str, month: str, day: str, name: str):
    # use secure_filename to avoid filename attacks
    post = load_post(f"{year}-{month}-{day}-{name}.md")
    if not post:
        abort(404)
    return {"entry": post}


@app.route("/archive/")
@templated("archive")
def archive():
    posts = load_posts(meta_only=True)
    return {"entries": posts, "archive": {"type": "Archive", "name": "All"}}


@app.route("/category/<name>/")
@templated("archive")
def category(name: str):
    posts = list(
        filter(lambda p: name in p.get("categories", []), load_posts(meta_only=True))
    )
    return {"entries": posts, "archive": {"type": "Category", "name": name}}


@app.route("/tag/<name>/")
@templated("archive")
def tag(name: str):
    posts = list(
        filter(lambda p: name in p.get("tags", []), load_posts(meta_only=True))
    )
    return {"entries": posts, "archive": {"type": "Tag", "name": name}}


@app.route("/<path:rel_url>")
@templated("page")
def page(rel_url: str):
    page = load_page(rel_url)
    if not page:
        return send_from_directory(raw_folder, rel_url)
    return {"entry": page}


@app.errorhandler(404)
@app.route("/404.html")
def page_not_found(e=None):
    return render_template("404.html"), 404


def s2tz(tz_str):
    m = re.match(r"UTC([+|-]\d{1,2}):(\d{2})", tz_str)
    if m:
        # in format 'UTC±[hh]:[mm]'
        delta_h = int(m.group(1))
        delta_m = int(m.group(2)) if delta_h >= 0 else -int(m.group(2))
        return timezone(timedelta(hours=delta_h, minutes=delta_m))
    try:
        # in format 'Asia/Shanghai'
        return pytz.timezone(tz_str)
    except pytz.UnknownTimeZoneError:
        return None


@app.route("/feed.atom")
def feed():
    root_url = request.url_root.rstrip("/")
    home_full_url = root_url + url_for(".index")
    feed_full_url = root_url + url_for(".feed")
    site = app.config["SITE_INFO"]
    site_tz = s2tz(site["timezone"]) or timezone(timedelta())

    fg = FeedGenerator()
    fg.id(home_full_url)
    fg.title(site.get("title", ""))
    fg.subtitle(site.get("subtitle", ""))
    if "author" in site:
        fg.author(name=site["author"])
    fg.link(href=home_full_url, rel="alternate")
    fg.link(href=feed_full_url, rel="self")

    posts = load_posts(meta_only=True)[:10]
    for i in range(len(posts)):
        p = load_post(posts[i]["filename"])
        if not p:
            continue
        fe = fg.add_entry()
        fe.id(root_url + p["url"])
        fe.link(href=root_url + p["url"])
        fe.title(p["title"])
        fe.content(p["content"])
        fe.published(p["created"].replace(tzinfo=site_tz))
        fe.updated(p.get("updated", p["created"]).replace(tzinfo=site_tz))
        if "author" in p:
            fe.author(name=p["author"])

    resp = make_response(fg.atom_str(pretty=True))
    resp.content_type = "application/atom+xml; charset=utf-8"
    return resp
