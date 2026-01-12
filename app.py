from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from analyzer import analyze_csv
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("logfile")

    if not file:
        return "No file uploaded", 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    analysis = analyze_csv(save_path)

    return render_template(
        "report.html",
        filename=filename,
        analysis=analysis
    )


if __name__ == "__main__":
    app.run(debug=True)
