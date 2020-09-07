import os
import re
import shutil
import functools
import traceback
from urllib.parse import urlparse

import click
from flask import url_for

from .__meta__ import __version__
from . import (
    app,
    instance_path,
    static_folder,
    theme_static_folder,
    pages_folder,
    raw_folder,
    load_posts,
)


echo = click.echo
echo_green = functools.partial(click.secho, fg="green")
echo_blue = functools.partial(click.secho, fg="blue")
echo_red = functools.partial(click.secho, fg="red")
echo_yellow = functools.partial(click.secho, fg="yellow")


@click.group(name="purepress", short_help="A simple static blog generator.")
@click.version_option(version=__version__)
def cli():
    pass


def main():
    cli.main()


@cli.command("preview", short_help="Preview the site.")
@click.option("--host", "-h", default="127.0.0.1", help="Host to preview the site.")
@click.option("--port", "-p", default=8080, help="Port to preview the site.")
@click.option("--debug", is_flag=True, default=False, help="Preview in debug mode.")
def preview_command(host, port, debug):
    app.debug = debug
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(host=host, port=port, debug=debug)


@cli.command("build", short_help="Build the site.")
@click.option(
    "--url-root",
    prompt="Please enter the url root (used as prefix of generated url)",
    help="The url root of your site. For example, if you want to access the site "
    'through "http://example.com/blog/", "http://example.com/blog/" should be '
    "passed in as the url root.",
)
def build_command(url_root):
    res = urlparse(url_root)
    app.config["PREFERRED_URL_SCHEME"] = res.scheme
    app.config["SERVER_NAME"] = res.netloc
    app.config["APPLICATION_ROOT"] = res.path or "/"
    # mark as 'BUILDING' status, so that templates can react properly,
    app.config["BUILDING"] = True

    try:
        with app.test_client() as client:
            build(client)
        echo_green('OK! Now you can find the built site in the "build" folder.')
    except Exception:
        traceback.print_exc()
        echo_red("Failed to build the site.")


def build(client):
    # prepare folder paths
    build_folder = os.path.join(instance_path, "build")
    build_static_folder = os.path.join(build_folder, "static")
    build_static_theme_folder = os.path.join(build_static_folder, "theme")
    build_pages_folder = build_folder
    build_posts_folder = os.path.join(build_folder, "post")
    build_categories_folder = os.path.join(build_folder, "category")
    build_tags_folder = os.path.join(build_folder, "tag")
    build_archive_folder = os.path.join(build_folder, "archive")
    build_index_page_folder = os.path.join(build_folder, "page")

    echo("Creating build folder...", nl=False)
    if os.path.isdir(build_folder):
        shutil.rmtree(build_folder)
    elif os.path.exists(build_folder):
        os.remove(build_folder)
    os.mkdir(build_folder)
    echo_green("OK")

    echo("Copying raw files...", nl=False)
    copy_folder_content(raw_folder, build_folder)
    echo_green("OK")

    echo("Copying theme static files...", nl=False)
    os.makedirs(build_static_theme_folder, exist_ok=True)
    copy_folder_content(theme_static_folder, build_static_theme_folder)
    echo_green("OK")

    echo("Copying static files...", nl=False)
    copy_folder_content(static_folder, build_static_folder)
    echo_green("OK")

    echo("Building custom pages...", nl=False)
    for dirname, _, files in os.walk(pages_folder):
        rel_dirname = os.path.relpath(dirname, pages_folder)
        os.makedirs(os.path.join(build_pages_folder, rel_dirname), exist_ok=True)
        for file in files:
            rel_path = os.path.join(rel_dirname, file)
            dst_rel_path = re.sub(r".md$", ".html", rel_path)
            dst_path = os.path.join(build_pages_folder, dst_rel_path)
            rel_url = "/".join(os.path.split(dst_rel_path))
            with app.test_request_context():
                url = url_for(".page", rel_url=rel_url)
            res = client.get(url)
            with open(dst_path, "wb") as f:
                f.write(res.data)
    echo_green("OK")

    with app.test_request_context():
        posts = load_posts(meta_only=True)

    echo("Building posts...", nl=False)
    for post in posts:
        filename = post["filename"]
        year, month, day, name = os.path.splitext(filename)[0].split("-", maxsplit=3)
        dst_dirname = os.path.join(build_posts_folder, year, month, day, name)
        os.makedirs(dst_dirname, exist_ok=True)
        dst_path = os.path.join(dst_dirname, "index.html")
        with app.test_request_context():
            url = url_for(".post", year=year, month=month, day=day, name=name)
        res = client.get(url)
        with open(dst_path, "wb") as f:
            f.write(res.data)
    echo_green("OK")

    echo("Bulding categories...", nl=False)
    categories = set(
        functools.reduce(lambda c, p: c + p.get("categories", []), posts, [])
    )
    for category in categories:
        category_folder = os.path.join(build_categories_folder, category)
        os.makedirs(category_folder, exist_ok=True)
        with app.test_request_context():
            url = url_for(".category", name=category)
        res = client.get(url)
        with open(os.path.join(category_folder, "index.html"), "wb") as f:
            f.write(res.data)
    echo_green("OK")

    echo("Bulding tags...", nl=False)
    tags = set(functools.reduce(lambda t, p: t + p.get("tags", []), posts, []))
    for tag in tags:
        tag_folder = os.path.join(build_tags_folder, tag)
        os.makedirs(tag_folder, exist_ok=True)
        with app.test_request_context():
            url = url_for(".tag", name=tag)
        res = client.get(url)
        with open(os.path.join(tag_folder, "index.html"), "wb") as f:
            f.write(res.data)
    echo_green("OK")

    echo("Bulding archive...", nl=False)
    os.makedirs(build_archive_folder, exist_ok=True)
    with app.test_request_context():
        url = url_for(".archive")
    res = client.get(url)
    with open(os.path.join(build_archive_folder, "index.html"), "wb") as f:
        f.write(res.data)
    echo_green("OK")

    echo("Building index...", nl=False)
    with app.test_request_context():
        url = url_for(".index")
    res = client.get(url)
    with open(os.path.join(build_folder, "index.html"), "wb") as f:
        f.write(res.data)
    page_num = 2
    while res.status_code != 404:
        page_folder = os.path.join(build_index_page_folder, str(page_num))
        os.makedirs(page_folder, exist_ok=True)
        with app.test_request_context():
            url = url_for(".index_page", page_num=page_num)
        res = client.get(url)
        with open(os.path.join(page_folder, "index.html"), "wb") as f:
            f.write(res.data)
        page_num += 1
    echo_green("OK")

    echo("Building feed...", nl=False)
    with app.test_request_context():
        url = url_for(".feed")
    res = client.get(url)
    with open(os.path.join(build_folder, "feed.atom"), "wb") as f:
        f.write(res.data)
    echo_green("OK")

    echo("Building 404...", nl=False)
    with app.test_request_context():
        url = url_for(".page_not_found")
    res = client.get(url)
    with open(os.path.join(build_folder, "404.html"), "wb") as f:
        f.write(res.data)
    echo_green("OK")


def copy_folder_content(src, dst):
    """
    Copy all content in src directory to dst directory.
    The src and dst must exist.
    """
    for file in os.listdir(src):
        file_path = os.path.join(src, file)
        dst_file_path = os.path.join(dst, file)
        if os.path.isdir(file_path):
            shutil.copytree(file_path, dst_file_path)
        else:
            shutil.copy(file_path, dst_file_path)
