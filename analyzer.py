import os
import time
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # non-GUI backend for servers
import matplotlib.pyplot as plt


def _pick_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first existing column name from candidates."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def analyze_csv(file_path: str, plots_dir: str = "static/plots") -> dict:
    # low_memory=False reduces mixed-dtype warnings on big CSV exports
    df = pd.read_csv(file_path, low_memory=False)

    # Try to find the most likely columns in Sentinel/Windows exports
    ip_col = _pick_col(df, ["IpAddress", "ClientIPAddress", "ClientAddress", "RemoteIpAddress"])
    user_col = _pick_col(df, ["Account", "TargetUserName", "TargetUser", "SubjectUserName", "AccountName"])
    time_col = _pick_col(df, ["TimeGenerated [UTC]", "TimeGenerated", "Timestamp", "EventTime"])

    # Make sure plots dir exists + create unique stamp for file names
    os.makedirs(plots_dir, exist_ok=True)
    stamp = int(time.time())

    result = {
        "total_events": int(len(df)),
        "unique_ips": "N/A",
        "unique_users": "N/A",

        # Targeted usernames
        "top_users": [],
        "user_plot_file": None,

        "ip_col": ip_col,
        "user_col": user_col,
        "time_col": time_col,

        "columns": list(df.columns),

        # IP metrics
        "top_ips": [],
        "plot_file": None,

        # time-series plot
        "time_plot_file": None,

        # EventID breakdown
        "eventid_plot_file": None,
        "eventid_counts": None,
    }

    # -----------------------------
    # Basic unique counts
    # -----------------------------
    if ip_col:
        result["unique_ips"] = int(pd.Series(df[ip_col]).nunique(dropna=True))

    if user_col:
        result["unique_users"] = int(pd.Series(df[user_col]).nunique(dropna=True))

    # -----------------------------
    # Metric #1: Top IPs + attempts + unique usernames per IP + Spray Score
    # -----------------------------
    if ip_col:
        df_ips = df[[ip_col]].copy()
        df_ips[ip_col] = df_ips[ip_col].astype(str).str.strip()
        df_ips = df_ips[(df_ips[ip_col] != "") & (df_ips[ip_col].str.lower() != "nan")]

        attempts_per_ip = df_ips[ip_col].value_counts().head(20)

        unique_users_per_ip = None
        if user_col:
            df_u = df[[ip_col, user_col]].copy()
            df_u[ip_col] = df_u[ip_col].astype(str).str.strip()
            df_u[user_col] = df_u[user_col].astype(str).str.strip()
            df_u = df_u[(df_u[ip_col] != "") & (df_u[ip_col].str.lower() != "nan")]
            df_u = df_u[(df_u[user_col] != "") & (df_u[user_col].str.lower() != "nan")]
            unique_users_per_ip = df_u.groupby(ip_col)[user_col].nunique()

        top_rows = []
        for ip, attempts in attempts_per_ip.items():
            unique_users = int(unique_users_per_ip.get(ip, 0)) if unique_users_per_ip is not None else 0
            spray_score = round(unique_users / attempts, 3) if attempts > 0 else 0

            top_rows.append({
                "ip": ip,
                "attempts": int(attempts),
                "unique_usernames": unique_users,
                "spray_score": spray_score,
            })

        result["top_ips"] = top_rows

        # Plot: attempts per IP
        plot_filename = f"top_ips_{stamp}.png"
        plot_path = os.path.join(plots_dir, plot_filename)

        plt.figure()
        attempts_per_ip.plot(kind="bar")
        plt.title("Top IPs by number of attempts")
        plt.xlabel("IP Address")
        plt.ylabel("Attempts")
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()

        result["plot_file"] = f"plots/{plot_filename}"

    # -----------------------------
    # Metric #2: Attempts over time (per minute)
    # -----------------------------
    if time_col:
        df_time = df[[time_col]].copy()
        df_time[time_col] = pd.to_datetime(df_time[time_col], errors="coerce")
        df_time = df_time.dropna()

        if not df_time.empty:
            attempts_over_time = df_time.set_index(time_col).resample("1min").size()

            time_plot_filename = f"attempts_over_time_{stamp}.png"
            time_plot_path = os.path.join(plots_dir, time_plot_filename)

            plt.figure(figsize=(10, 4))
            attempts_over_time.plot()
            plt.title("Authentication attempts over time")
            plt.xlabel("Time")
            plt.ylabel("Attempts per minute")
            plt.tight_layout()
            plt.savefig(time_plot_path)
            plt.close()

            result["time_plot_file"] = f"plots/{time_plot_filename}"

    # -----------------------------
    # Metric #3: EventID breakdown (Top 10)
    # -----------------------------
    if "EventID" in df.columns:
        event_counts = df["EventID"].value_counts().head(10)

        event_plot_filename = f"eventid_breakdown_{stamp}.png"
        event_plot_path = os.path.join(plots_dir, event_plot_filename)

        plt.figure()
        event_counts.plot(kind="bar")
        plt.title("Top Event IDs")
        plt.xlabel("EventID")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(event_plot_path)
        plt.close()

        result["eventid_plot_file"] = f"plots/{event_plot_filename}"
        result["eventid_counts"] = event_counts.to_dict()

    # -----------------------------
    # Metric #4: Top targeted usernames (Top 20)
    # -----------------------------
    if user_col:
        df_users = df[[user_col]].copy()
        df_users[user_col] = df_users[user_col].astype(str).str.strip()
        df_users = df_users[(df_users[user_col] != "") & (df_users[user_col].str.lower() != "nan")]

        top_users_series = df_users[user_col].value_counts().head(20)

        # Save for table
        result["top_users"] = [
            {"username": u, "attempts": int(c)}
            for u, c in top_users_series.items()
        ]

        # Plot
        user_plot_filename = f"top_usernames_{stamp}.png"
        user_plot_path = os.path.join(plots_dir, user_plot_filename)

        plt.figure()
        top_users_series.plot(kind="bar")
        plt.title("Top targeted usernames")
        plt.xlabel("Username")
        plt.ylabel("Attempts")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(user_plot_path)
        plt.close()

        result["user_plot_file"] = f"plots/{user_plot_filename}"

    return result
