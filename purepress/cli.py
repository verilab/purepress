import click

from .__meta__ import __version__


@click.group(name="purepress", short_help="A simple static blog generator.")
@click.version_option(version=__version__)
def cli():
    pass


@cli.command("preview", short_help="Preview the site.")
@click.option("--host", "-h", default="127.0.0.1", help="Host to preview the site.")
@click.option("--port", "-p", default=8080, help="Port to preview the site.")
@click.option("--debug", is_flag=True, default=False, help="Preview in debug mode.")
def preview_command(host, port, debug):
    from purepress import app

    app.debug = debug
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(host=host, port=port, debug=debug)
