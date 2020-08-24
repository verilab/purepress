import os

from purepress import app

if __name__ == "__main__":
    os.environ["INSTANCE_PATH"] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dev_inst"
    )
    app.run("127.0.0.1", 8080, debug=True)
