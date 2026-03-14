"""
Morning Health Check Automation
Queries Elasticsearch for Platform Health (Monitoring + Event Bus Onboarding)
and sends a formatted HTML email report via SMTP.

Usage:
    python morning_check.py            # run and send email
    python morning_check.py --dry-run  # print report only, no email sent

Required environment variables:
    ES_USER       - Elasticsearch username
    ES_PASSWORD   - Elasticsearch password
"""

import os
import sys
import smtplib
import traceback
import elasticsearch as es_lib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, List, Tuple

from elasticsearch import Elasticsearch

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

ES_HOST     = "https://metrology-elastic-1.eu-fr-paris.cloud.socgen/"
ES_USER     = os.environ.get("ES_USER", "")
ES_PASSWORD = os.environ.get("ES_PASSWORD", "")

HEALTH_INDEX = "observability_log_health_results_prod_1*"

# Region mapping: exact 'region' field value in ES  ->  display label
# Confirmed from Kibana Discover logs (healthcheck_service_name field):
MONITORING_REGIONS: Dict[str, str] = {
    "prod-paris":      "Paris",       # Monitoring v2 - prod-paris
    "prod-north":      "North",       # Monitoring v2 - prod-north
    "prod-hongkong":   "HK",          # Monitoring v2 - prod-hongkong
    "production-amer": "Amer",        # Monitoring v2 - production-amer
    "prod-singapore":  "Singapore",   # Monitoring v2 - prod-singapore
}

# Event Bus regions - update once confirmed from Kibana
EVENTBUS_REGIONS: Dict[str, str] = {
    "prod-fr-paris":  "Paris",
    "prod-fr-north":  "North",
    "prod-hk":        "HK",
    "prod-us":        "Amer",
    "prod-asia-sg":   "Singapore",
}

# Elasticsearch api_code field values
MONITORING_API_CODE = "cloudplatform-monitoring"
EVENTBUS_API_CODE   = "gts-event-bus-onboarding"

# SMTP - no TLS, port 25
SMTP_CONFIG = {
    "smtp_server": "smtp-goss.int.world.socgen",
    "smtp_port":   25,
    "use_tls":     False,
}

EMAIL_CONFIG = {
    "sender":    "no-replay-metrology@socgen.com",
    "recipients": [
        "list.par-resg-gts-metrologyaasfeatureteam@socgen.com",
    ],
    "subject":   f"Metro Morning Checks Report - {datetime.now().strftime('%Y-%m-%d')}",
}


# ─────────────────────────────────────────────
# ELASTICSEARCH CLIENT
# ─────────────────────────────────────────────

def get_es_client() -> Elasticsearch:
    """
    Create Elasticsearch client.
    Compatible with elasticsearch-py v7 (http_auth) and v8+ (basic_auth).
    """
    major = int(es_lib.__version__.split(".")[0])
    kwargs: Dict[str, Any] = dict(
        hosts=[ES_HOST],
        verify_certs=False,
        ssl_show_warn=False,
    )
    if major >= 8:
        kwargs["basic_auth"] = (ES_USER, ES_PASSWORD)
        kwargs["request_timeout"] = 30
    else:
        kwargs["http_auth"] = (ES_USER, ES_PASSWORD)
        kwargs["timeout"] = 30

    return Elasticsearch(**kwargs)


# ─────────────────────────────────────────────
# ELASTICSEARCH QUERY
# ─────────────────────────────────────────────

def query_health_by_region(
    es: Elasticsearch,
    index: str,
    api_code: str,
    region: str,
) -> Dict[str, int]:
    """
    Aggregate health records for api_code + region over last 24 hours.
    Returns dict with UP / DEGRADED / KO / TOTAL counts.
    """
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"term": {"api_code.keyword": api_code}},
                    {"term": {"region.keyword": region}},
                ],
                "filter": [
                    {"range": {"agent_timestamp": {"gte": "now-24h", "lte": "now"}}}
                ],
            }
        },
        "aggs": {
            "by_status": {
                "terms": {"field": "status.keyword", "size": 20}
            }
        },
    }

    try:
        resp    = es.search(index=index, body=query)
        buckets = resp["aggregations"]["by_status"]["buckets"]
        counts  = {b["key"]: b["doc_count"] for b in buckets}
        total   = sum(counts.values())
        return {
            "UP":       counts.get("UP", 0),
            "DEGRADED": counts.get("DEGRADED", 0),
            "KO":       counts.get("KO", 0),
            "TOTAL":    total,
        }
    except Exception as exc:
        print(f"  [WARN] ES query failed - api_code={api_code}, region={region}: {exc}")
        return {"UP": 0, "DEGRADED": 0, "KO": 0, "TOTAL": 0}


# ─────────────────────────────────────────────
# AVAILABILITY HELPERS
# ─────────────────────────────────────────────

def availability_line(label: str, counts: Dict[str, int]) -> Tuple[str, bool]:
    """
    Build a human-readable availability line.
    Returns (text, has_issue).

    Examples:
      "Paris: 100% availability"
      "HK: 99.97% availability | 0.03% Down"
      "Amer: N/A (no data)"
    """
    total = counts["TOTAL"]
    if total == 0:
        return f"{label}: N/A (no data)", True

    up       = counts["UP"]
    degraded = counts["DEGRADED"]
    ko       = counts["KO"]

    avail_pct = ((up + degraded) / total) * 100
    down_pct  = (ko / total) * 100

    if down_pct > 0:
        return (
            f"{label}: {avail_pct:.2f}% availability | {down_pct:.2f}% Down",
            True,
        )
    return f"{label}: 100% availability", False


# ─────────────────────────────────────────────
# REPORT BUILDER
# ─────────────────────────────────────────────

def build_report(es: Elasticsearch) -> Tuple[str, str]:
    """
    Query ES and build (plain_text, html) report tuple.
    """
    now_utc    = datetime.now(timezone.utc)
    now_str    = now_utc.strftime("%d/%m/%Y")
    gen_ts     = now_utc.strftime("%Y-%m-%d %H:%M UTC")
    report_hdr = f"Morning Check - {now_str} (last 24 hrs)"

    plain_lines: List[str] = [report_hdr, ""]

    # 1. Platform Health Monitoring
    print("  Querying Platform Health Monitoring ...")
    plain_lines.append("Platform Health Monitoring")
    plain_lines.append("")
    monitoring_results: List[Tuple[str, bool]] = []

    for region_key, label in MONITORING_REGIONS.items():
        counts = query_health_by_region(es, HEALTH_INDEX, MONITORING_API_CODE, region_key)
        line, issue = availability_line(label, counts)
        plain_lines.append(f"  . {line}")
        monitoring_results.append((line, issue))
        sym = "WARN" if issue else " OK "
        print(f"    [{sym}] {label:12} -> {line}")

    plain_lines.append("")

    # 2. Platform Health Eventbus
    print("  Querying Platform Health Eventbus ...")
    plain_lines.append("Platform Health Eventbus")
    plain_lines.append("")
    eventbus_results: List[Tuple[str, bool]] = []

    for region_key, label in EVENTBUS_REGIONS.items():
        counts = query_health_by_region(es, HEALTH_INDEX, EVENTBUS_API_CODE, region_key)
        line, issue = availability_line(label, counts)
        plain_lines.append(f"  . {line}")
        eventbus_results.append((line, issue))
        sym = "WARN" if issue else " OK "
        print(f"    [{sym}] {label:12} -> {line}")

    plain_lines.append("")
    plain_text = "\n".join(plain_lines)

    # Build HTML
    def make_rows(results: List[Tuple[str, bool]]) -> str:
        rows = ""
        for line, issue in results:
            bg    = "#fff5f5" if issue else "#f0fff4"
            color = "#c0392b" if issue else "#27ae60"
            icon  = "&#9888;" if issue else "&#10003;"
            bold  = "bold" if issue else "normal"
            rows += (
                f'<tr style="background:{bg}">'
                f'<td style="padding:7px 10px;width:30px;text-align:center;'
                f'color:{color};font-size:16px">{icon}</td>'
                f'<td style="padding:7px 12px;color:{color};font-weight:{bold}">{line}</td>'
                f'</tr>\n'
            )
        return rows

    html = f"""<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;font-size:14px;color:#222;
             max-width:700px;margin:auto;padding:20px">

  <h2 style="border-bottom:2px solid #2c3e50;padding-bottom:8px;color:#2c3e50">
    Morning Health Check Report
  </h2>
  <p style="color:#555;margin-top:-5px">{now_str} &bull; Last 24 hours</p>

  <h3 style="color:#2c3e50;margin-top:24px">Platform Health Monitoring</h3>
  <table cellspacing="0" cellpadding="0"
         style="border-collapse:collapse;width:100%;
                border:1px solid #ddd;font-size:14px">
    {make_rows(monitoring_results)}
  </table>

  <h3 style="color:#2c3e50;margin-top:24px">Platform Health Eventbus</h3>
  <table cellspacing="0" cellpadding="0"
         style="border-collapse:collapse;width:100%;
                border:1px solid #ddd;font-size:14px">
    {make_rows(eventbus_results)}
  </table>

  <p style="color:#aaa;font-size:11px;margin-top:30px;
            border-top:1px solid #eee;padding-top:10px">
    Auto-generated by Metro Morning Check &bull; {gen_ts}
  </p>
</body>
</html>"""

    return plain_text, html


# ─────────────────────────────────────────────
# EMAIL SENDER
# ─────────────────────────────────────────────

def send_email(plain_text: str, html_text: str) -> None:
    """Send report via SMTP (no TLS, port 25)."""
    msg            = MIMEMultipart("alternative")
    msg["Subject"] = EMAIL_CONFIG["subject"]
    msg["From"]    = EMAIL_CONFIG["sender"]
    msg["To"]      = ", ".join(EMAIL_CONFIG["recipients"])

    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_text,  "html"))

    with smtplib.SMTP(SMTP_CONFIG["smtp_server"], SMTP_CONFIG["smtp_port"]) as smtp:
        if SMTP_CONFIG["use_tls"]:
            smtp.starttls()
        smtp.sendmail(
            EMAIL_CONFIG["sender"],
            EMAIL_CONFIG["recipients"],
            msg.as_string(),
        )
    print(f"Email sent to: {EMAIL_CONFIG['recipients']}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main() -> None:
    dry_run = "--dry-run" in sys.argv

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode = " [DRY RUN - no email]" if dry_run else ""
    print(f"[{ts}] Starting Morning Health Check{mode}")

    if not ES_USER or not ES_PASSWORD:
        raise EnvironmentError(
            "ES_USER and ES_PASSWORD environment variables must be set.\n"
            "  export ES_USER=<your_user>\n"
            "  export ES_PASSWORD=<your_password>"
        )

    es = get_es_client()
    plain_text, html_text = build_report(es)

    print("\n" + "="*60)
    print(plain_text)
    print("="*60 + "\n")

    if dry_run:
        print("Dry-run mode: email NOT sent.")
    else:
        print("Sending email ...")
        send_email(plain_text, html_text)

    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
