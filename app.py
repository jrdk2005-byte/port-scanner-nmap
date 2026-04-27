from flask import Flask, render_template, request
import subprocess
import datetime
import os

app = Flask(__name__)

def run_scan(target, scan_type):
    if not os.path.exists("scan_results"):
        os.mkdir("scan_results")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"scan_results/{scan_type}_{timestamp}.txt"

    if scan_type == "basic":
        command = ["nmap", target]
    elif scan_type == "service":
        command = ["nmap", "-sV", target]
    elif scan_type == "aggressive":
        command = ["nmap", "-A", target]
    else:
        command = ["nmap", target]

    result = subprocess.run(command, capture_output=True, text=True)

    with open(output_file, "w") as f:
        f.write(result.stdout)

    return result.stdout

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""

    if request.method == "POST":
        target = request.form.get("target")
        scan_type = request.form.get("scan")

        if target:
            output = run_scan(target, scan_type)

    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)
