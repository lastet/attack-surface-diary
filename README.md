# Attack Surface Diary 🛡️

A hands-on security lab focused on observing and analyzing real-world authentication attack patterns against exposed infrastructure.

This project combines **Azure VM deployment**, **log collection**, and **Python-based analysis** (Flask + pandas + matplotlib) to visualize and compare attack behavior under different credential-strength conditions.

---

## 🧠 Project Idea

The goal of this lab was to answer a simple but critical question:

> **How quickly is exposed infrastructure discovered, and how do attackers behave when credentials are weak vs strong?**

To explore this, I deployed **two Windows virtual machines in Azure**:

- **VM #1 (Weak credentials)**  
  - Common username  
  - Very weak password
  - All ports open with Any-Any rules, fw off
- **VM #2 (Strong credentials)**  
  - Non-trivial username  
  - Strong, complex password
  - All ports open with Any-Any rules, fw off

Both VMs were exposed long enough to collect meaningful authentication logs.
Raw authentication logs were collected from Azure-deployed Windows VMs and analyzed locally.
Log files are intentionally excluded from the repository for security and privacy reasons.

---

## 🏗️ Lab Setup

### Infrastructure
- Microsoft Azure
- Two public-facing Windows VMs
- Windows Security Event Logs
- Logs exported from Azure / Sentinel as CSV files

### Data Sources
- `WC_query_data_*.csv` — **Weak credentials VM**
- `GC_query_data_*.csv` — **Good (strong) credentials VM**

> 📌 Screenshots and metrics with a **`c` suffix** (e.g. `metrics3.1c`) are **control results** from the VM with strong credentials.

---

## ⚙️ Application Overview

This repository contains a small Flask web application that:

1. Accepts authentication log files (CSV)
2. Automatically detects relevant columns
3. Analyzes attack patterns
4. Generates tables and visualizations

### Tech Stack
- Python 3
- Flask
- pandas
- matplotlib
- HTML (Jinja templates)

---

## 📊 Implemented Metrics & Visualizations

### 1. Top IPs by Authentication Attempts
- Total attempts per IP
- Unique usernames targeted per IP
- **Spray score**  



### 2. Attempts Over Time
- Authentication attempts aggregated per minute
- Clearly shows:
- attack bursts
- discovery timing
- drop-offs after VM shutdown or blocking

### 3. EventID Breakdown
- Top Windows Security Event IDs
- Highlights dominant authentication-related events
- Useful for SOC-style triage

### 4. Top Targeted Usernames
- Most frequently targeted account names
- Includes:
- `administrator`
- `admin`
- `test`
- service-style accounts
- Rendered as:
- bar chart
- sortable table

---

## 🔬 Comparative Analysis (Weak vs Strong Credentials)

One of the key aspects of this lab is **comparison**.

### Weak Credentials VM
- Extremely high volume of authentication attempts
- Massive username enumeration
- Clear credential spraying behavior
- High spray scores from a small set of IPs

### Strong Credentials VM (Control)
- Significantly fewer attempts
- Much lower username diversity
- No signs of successful authentication
- Attackers disengage faster

📎 All comparison screenshots are included and labeled with a `c` suffix for clarity.


🚀 How to Run Locally

pip install -r requirements.txt
python app.py

Then open:
http://127.0.0.1:5000

Upload a CSV log file and view the analysis report.

🧩 Why This Project Matters

This lab demonstrates:

Real-world attack behavior (not synthetic data)
Practical log analysis skills
Ability to design controlled experiments
Understanding of credential-based attack techniques
Clear, visual security reporting
It reflects the kind of exploratory, investigative work performed in SOC, cloud security, and blue team roles.

📌 Future Improvements 

GeoIP enrichment

Detection heuristics (credential spray alerts)

Comparison dashboards (weak vs strong side-by-side)

Exportable reports (PDF / CSV summaries)

✨ Final Note
This project is intentionally simple in tooling and rich in signal.
It focuses on what attackers actually do, not just what tools claim they do.



## 📁 Repository Structure

```text
attack-surface-diary/
│
├── analyzer.py
│   Core analysis logic.
│   Parses authentication logs, detects relevant columns,
│   computes metrics (spray score, unique usernames, attempts),
│   and generates plots and tables.
│
├── app.py
│   Flask application entry point.
│   Handles file uploads, triggers analysis,
│   and renders the final report.
│
├── requirements.txt
│   Python dependencies required to run the project.
│
├── templates/
│   ├── index.html
│   │   Upload page for CSV log files.
│   │
│   └── report.html
│       Rendered analysis report including
│       charts, tables, and summary statistics.
│
├── static/
│   Auto-generated visualizations (plots) served by Flask.
│   Images are created dynamically during analysis.
│
├── uploads/
│   Temporary storage for uploaded CSV log files.
│   (Excluded from version control in real use.)
│
├── screenshots/
│   Screenshots documenting the experiment and results:
│
│   ├── metrics*.png
│   │   Analysis results from the weak-credentials VM.
│
│   ├── metrics*c.png
│   │   Control results from the strong-credentials VM
│   │   (suffix `c` = control).
│
│   ├── tool.png
│   │   Example of the analysis report UI.
│
│   └── tool_and_setup.png
│       Overview of lab setup and tool execution.
│
├── README.md
│   Project documentation and experiment description.
│
└── .gitignore
    Excludes log files, uploads, and other sensitive or
    non-essential artifacts.


