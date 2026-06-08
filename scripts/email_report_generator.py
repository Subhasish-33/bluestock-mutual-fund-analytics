"""
Bonus Challenge 5: Automated HTML Email Report Generator
Bluestock MF Capstone

Generates a professional weekly HTML performance summary report and
optionally sends it via SMTP (Gmail).

The HTML is built using Jinja2 (with a plain-string fallback).

Usage:
    # Generate HTML only (saved to reports/weekly_report.html)
    python scripts/email_report_generator.py

    # Also send via SMTP (requires env vars SENDER_EMAIL + SMTP_PASSWORD)
    python scripts/email_report_generator.py --send-email recipient@example.com
"""

import os
import sys
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    from jinja2 import Template
    HAS_JINJA = True
except ImportError:
    HAS_JINJA = False

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE     = Path(__file__).resolve().parent.parent
DB_PATH  = BASE / "data" / "db" / "bluestock_mf.db"
OUT_PATH = BASE / "reports" / "weekly_report.html"

# ── Jinja2 HTML Template ──────────────────────────────────────────────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Weekly MF Performance Report</title>
  <style>
    body   { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }
    .card  { background: white; border-radius: 10px; padding: 30px; max-width: 900px;
             margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    h1     { color: #1E3A8A; border-bottom: 3px solid #1E3A8A; padding-bottom: 10px; }
    h2     { color: #374151; margin-top: 30px; }
    .badge { display:inline-block; background:#1E3A8A; color:white;
             border-radius:4px; padding:2px 8px; font-size:0.8em; }
    table  { width:100%; border-collapse:collapse; margin-top:15px; }
    th     { background:#1E3A8A; color:white; padding:10px 12px; text-align:left; }
    td     { padding:9px 12px; border-bottom:1px solid #e5e7eb; }
    tr:nth-child(even) td { background:#f8f9fa; }
    tr:hover td { background:#e0f2fe; }
    .positive { color:#16a34a; font-weight:600; }
    .negative { color:#dc2626; font-weight:600; }
    .footer { color:#6b7280; font-size:0.85em; margin-top:25px; text-align:center; }
  </style>
</head>
<body>
  <div class="card">
    <h1>📈 Bluestock MF — Weekly Performance Report</h1>
    <p>Generated on <strong>{{ report_date }}</strong> &nbsp;
       <span class="badge">Automated</span></p>

    <h2>🏆 Top 5 Funds (by Sharpe Ratio)</h2>
    <table>
      <tr>
        <th>#</th><th>Scheme Name</th><th>Category</th>
        <th>1Y Return (%)</th><th>3Y Return (%)</th>
        <th>Sharpe Ratio</th><th>Expense Ratio (%)</th>
      </tr>
      {% for row in top_funds %}
      <tr>
        <td>{{ loop.index }}</td>
        <td>{{ row.scheme_name }}</td>
        <td>{{ row.category }}</td>
        <td class="{{ 'positive' if row.return_1yr_pct > 0 else 'negative' }}">{{ "%.2f"|format(row.return_1yr_pct) }}%</td>
        <td class="{{ 'positive' if row.return_3yr_pct > 0 else 'negative' }}{{ "%.2f"|format(row.return_3yr_pct) }}%</td>
        <td>{{ "%.3f"|format(row.sharpe_ratio) }}</td>
        <td>{{ "%.2f"|format(row.expense_ratio_pct) }}%</td>
      </tr>
      {% endfor %}
    </table>

    <h2>📊 Portfolio Summary</h2>
    <table>
      <tr><th>Metric</th><th>Value</th></tr>
      <tr><td>Total Funds Tracked</td><td>{{ summary.total_funds }}</td></tr>
      <tr><td>Average 1Y Return</td>
          <td class="{{ 'positive' if summary.avg_1yr > 0 else 'negative' }}">{{ "%.2f"|format(summary.avg_1yr) }}%</td></tr>
      <tr><td>Average 3Y Return</td>
          <td class="{{ 'positive' if summary.avg_3yr > 0 else 'negative' }}">{{ "%.2f"|format(summary.avg_3yr) }}%</td></tr>
      <tr><td>Total AUM (₹ Cr)</td><td>₹{{ "{:,.0f}".format(summary.total_aum) }} Cr</td></tr>
      <tr><td>Average Expense Ratio</td><td>{{ "%.2f"|format(summary.avg_expense) }}%</td></tr>
    </table>

    <p class="footer">
      This is an automated report from the Bluestock MF Capstone Project.<br>
      Data sourced from AMFI via mfapi.in. Not investment advice.
    </p>
  </div>
</body>
</html>
"""


def load_data():
    """Fetch report data from the SQLite database."""
    conn = sqlite3.connect(DB_PATH)

    # Top 5 by Sharpe
    top_funds = pd.read_sql_query("""
        SELECT scheme_name, category,
               return_1yr_pct, return_3yr_pct,
               sharpe_ratio, expense_ratio_pct
        FROM scheme_performance
        ORDER BY sharpe_ratio DESC
        LIMIT 5
    """, conn)

    # Portfolio-level summary
    summary_row = pd.read_sql_query("""
        SELECT COUNT(*)            AS total_funds,
               AVG(return_1yr_pct) AS avg_1yr,
               AVG(return_3yr_pct) AS avg_3yr,
               SUM(aum_crore)      AS total_aum,
               AVG(expense_ratio_pct) AS avg_expense
        FROM scheme_performance
    """, conn).iloc[0]

    conn.close()
    return top_funds, summary_row


def build_html(top_funds: pd.DataFrame, summary) -> str:
    """Render the Jinja2 template (or fallback to plain-string generation)."""
    report_date = datetime.now().strftime("%d %B %Y, %I:%M %p")

    if HAS_JINJA:
        template = Template(HTML_TEMPLATE)
        return template.render(
            report_date=report_date,
            # Pass as list of namedtuples so Jinja can do row.scheme_name
            top_funds=list(top_funds.itertuples(index=False)),
            summary=summary,
        )
    else:
        # Plain-string fallback (no Jinja2 needed)
        rows = ""
        for i, (_, row) in enumerate(top_funds.iterrows(), 1):
            cls1 = "positive" if row.return_1yr_pct > 0 else "negative"
            cls3 = "positive" if row.return_3yr_pct > 0 else "negative"
            rows += (
                f"<tr><td>{i}</td><td>{row.scheme_name}</td>"
                f"<td>{row.category}</td>"
                f"<td class='{cls1}'>{row.return_1yr_pct:.2f}%</td>"
                f"<td class='{cls3}'>{row.return_3yr_pct:.2f}%</td>"
                f"<td>{row.sharpe_ratio:.3f}</td>"
                f"<td>{row.expense_ratio_pct:.2f}%</td></tr>"
            )
        return f"<h1>Weekly MF Report — {report_date}</h1><table border='1'>{rows}</table>"


def send_email(html_content: str, recipient: str):
    """Send HTML email via Gmail SMTP (requires env vars)."""
    sender   = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SMTP_PASSWORD")

    if not sender or not password:
        print("⚠️  SENDER_EMAIL / SMTP_PASSWORD env vars not set. Skipping send.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Weekly MF Performance Report — {datetime.now().strftime('%d %b %Y')}"
    msg["From"]    = sender
    msg["To"]      = recipient
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
    print(f"✅ Email sent to {recipient}")


def generate_report(send_to: str = None):
    print("Connecting to database and loading data...")
    top_funds, summary = load_data()

    html_content = build_html(top_funds, summary)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html_content, encoding="utf-8")
    print(f"✅ HTML report saved → {OUT_PATH}")

    if send_to:
        send_email(html_content, send_to)


if __name__ == "__main__":
    recipient = None
    if "--send-email" in sys.argv:
        idx = sys.argv.index("--send-email")
        if idx + 1 < len(sys.argv):
            recipient = sys.argv[idx + 1]
        else:
            print("Usage: python email_report_generator.py --send-email recipient@example.com")
            sys.exit(1)

    generate_report(send_to=recipient)
