from flask import Flask, render_template, request
import subprocess
import datetime
import os
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


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


def explain_with_ai(scan_output):
    prompt = f"""
Explain this Nmap scan result in simple beginner-friendly language.

Include:
1. Summary of the scan
2. Open ports found
3. Meaning of each service
4. Possible risks
5. Safety recommendations

Nmap scan result:
{scan_output}
"""

    response = model.generate_content(prompt)
    return response.text


@app.route("/", methods=["GET", "POST"])
def index():
    raw_output = ""
    ai_output = ""

    if request.method == "POST":
        target = request.form.get("target")
        scan_type = request.form.get("scan")

        if target:
            raw_output = run_scan(target, scan_type)
            ai_output = explain_with_ai(raw_output)

    return render_template(
        "index.html",
        raw_output=raw_output,
        ai_output=ai_output
    )


if __name__ == "__main__":
    app.run(debug=True)
