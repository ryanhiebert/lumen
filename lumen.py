import os
from flask import Flask, redirect, render_template, request, url_for
from contextlib import closing, ExitStack, contextmanager, closing
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR


app = Flask(__name__, template_folder="")


app.config["PROJECTORS"] = {
    conf.split(":", 1)[0]: conf.split(":", 2)[1:]
    for conf in os.environ.get("PROJECTORS", "").split(",")
    if conf.count(":") >= 2
}


@app.route("/", endpoint="display")
def display():
    """Display the projector control form."""
    active = (
        app.config["PROJECTORS"]
        if "projectors" not in request.args
        else request.args["projectors"].split(",")
    )
    return render_template(
        "lumen.html",
        projectors=app.config["PROJECTORS"],
        active=active,
        error=request.args.get("error"),
        replace_url=url_for("display", projectors=",".join(active)),
    )


@app.route("/", methods=["POST"])
def submit():
    """Handle the projector control form submit."""
    handlers = {"canon": canon, "vivitek": vivitek}
    projectors = request.form.getlist("projector")
    command = request.form["command"]
    args = {"projectors": ",".join(projectors)}
    try:
        with ExitStack() as stack:
            for label in projectors:
                type, conn = app.config["PROJECTORS"][label]
                print(f"{label} ({type}:{conn}): {command}")
                stack.enter_context(handlers.get(type, unknown)(label, conn, command))
    except Exception as e:
        args["error"] = str(e)
    return redirect(url_for("display", **args), 303)


@contextmanager
def unknown(label: str, conn: str, command: str):
    """Send a command to a fake projector without blocking."""
    yield
    print(f"{label} (fake:{conn}): {command} done")


@contextmanager
def canon(label: str, conn: str, command: str):
    """Send a command to a canon projector without blocking."""
    with closing(socket(AF_INET, SOCK_STREAM)) as s:
        s.connect((conn, 33336))
        commands = {
            "poweron": b"POWER=ON",
            "poweroff": b"POWER=OFF",
            "freeze": b"FREEZE=ON",
            "unfreeze": b"FREEZE=OFF",
            "blank": b"BLANK=ON",
            "unblank": b"BLANK=OFF",
        }
        s.send(commands[command] + b"\r")
        yield
        s.recv(128)
        s.shutdown(SHUT_RDWR)
        print(f"{label} (canon:{conn}): {command} done")


@contextmanager
def vivitek(label: str, conn: str, command: str):
    """Send a command to a vivitek projector without blocking."""
    with closing(socket(AF_INET, SOCK_STREAM)) as s:
        s.connect((conn, 7000))
        commands = {
            "poweron": b"power.on",
            "poweroff": b"power.off",
            "freeze": b"freeze = 1",
            "unfreeze": b"freeze = 0",
            "blank": b"blank = 1",
            "unblank": b"blank = 0",
        }
        s.send(b"op " + commands[command] + b"\r")
        yield
        s.recv(128)
        s.shutdown(SHUT_RDWR)
        print(f"{label} (vivitek:{conn}): {command} done")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
