"""
Vital IQ — Corporate Health Intelligence Platform
Real-time biometric monitoring and autonomous intervention engine
"""

import json, os, time
from datetime import datetime, timedelta
from typing import List, TypedDict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

os.environ.setdefault("ANTHROPIC_API_KEY", "")

# ─────────────────────────────────────────────
# PAGE CONFIG + CSS
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Clair Health — Health Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  /* Global */
  html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

  /* Hide Streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }

  /* Metric card */
  .metric-card {
    background: #0f1923;
    border: 1px solid #1e2d3d;
    border-radius: 6px;
    padding: 18px 20px;
    margin: 4px 0;
  }
  .metric-label {
    font-size: 0.72em;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #5a7a96;
    margin-bottom: 6px;
  }
  .metric-value {
    font-size: 1.9em;
    font-weight: 700;
    color: #e8edf2;
    line-height: 1.1;
  }
  .metric-delta {
    font-size: 0.78em;
    color: #5a7a96;
    margin-top: 4px;
  }
  .metric-delta.up   { color: #2ecc71; }
  .metric-delta.down { color: #e74c3c; }

  /* Status badges */
  .badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 3px;
    font-size: 0.72em;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  .badge-critical { background: #2d0f0f; color: #e74c3c; border: 1px solid #e74c3c; }
  .badge-warning  { background: #2d1f00; color: #f39c12; border: 1px solid #f39c12; }
  .badge-normal   { background: #0f2d1a; color: #2ecc71; border: 1px solid #2ecc71; }

  /* Issue tag */
  .issue-tag {
    display: inline-block;
    background: #1a1f2e;
    border: 1px solid #2e3a4e;
    color: #8facc8;
    border-radius: 3px;
    padding: 2px 10px;
    margin: 2px;
    font-size: 0.75em;
    font-family: 'Courier New', monospace;
    letter-spacing: 0.03em;
  }

  /* Action log item */
  .action-item {
    background: #0a1520;
    border-left: 3px solid #1a6b3c;
    padding: 8px 14px;
    margin: 3px 0;
    border-radius: 0 4px 4px 0;
    font-family: 'Courier New', monospace;
    font-size: 0.82em;
    color: #c8dce8;
  }
  .action-item.wellness {
    border-left-color: #1a4a6b;
  }

  /* Section header */
  .section-header {
    font-size: 0.7em;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #3d6b8a;
    border-bottom: 1px solid #1e2d3d;
    padding-bottom: 8px;
    margin-bottom: 16px;
    margin-top: 8px;
  }

  /* Connection status */
  .status-connected {
    background: #0a1f12;
    border: 1px solid #1a6b3c;
    border-radius: 4px;
    padding: 8px 14px;
    color: #2ecc71;
    font-size: 0.8em;
    font-weight: 600;
    letter-spacing: 0.04em;
  }
  .status-disconnected {
    background: #1a1400;
    border: 1px solid #5a4a00;
    border-radius: 4px;
    padding: 8px 14px;
    color: #f39c12;
    font-size: 0.8em;
    font-weight: 600;
    letter-spacing: 0.04em;
  }

  /* Divider */
  hr { border-color: #1e2d3d; margin: 24px 0; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #080f16;
    border-right: 1px solid #1e2d3d;
  }

  /* Summary box */
  .summary-box {
    background: #0a1520;
    border: 1px solid #1e2d3d;
    border-radius: 6px;
    padding: 16px 20px;
    color: #a0b8cc;
    font-size: 0.88em;
    line-height: 1.6;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# GOOGLE CALENDAR
# ─────────────────────────────────────────────

GCAL_SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_gcal_service():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", GCAL_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open("token.json", "w") as f: f.write(creds.to_json())
            else:
                return None
        return build("calendar", "v3", credentials=creds)
    except Exception:
        return None

def load_real_calendar(svc) -> List[dict]:
    try:
        today = datetime.now().date()
        tmin  = datetime.combine(today, datetime.min.time()).isoformat() + "Z"
        tmax  = datetime.combine(today, datetime.max.time()).isoformat() + "Z"
        items = svc.events().list(
            calendarId="primary", timeMin=tmin, timeMax=tmax,
            singleEvents=True, orderBy="startTime", maxResults=20
        ).execute().get("items", [])
        result = []
        for e in items:
            s = e["start"].get("dateTime", e["start"].get("date", ""))
            n = e["end"].get("dateTime",   e["end"].get("date", ""))
            if "T" not in s: s = f"{s}T09:00"
            if "T" not in n: n = f"{n}T10:00"
            result.append({"id": e["id"], "title": e.get("summary", "Untitled"),
                           "start": s[:16], "end": n[:16],
                           "moveable": True, "gcal": True})
        return result
    except Exception as ex:
        st.warning(f"Calendar read error: {ex}"); return []

def gcal_create(svc, title, start_dt, end_dt):
    try:
        svc.events().insert(calendarId="primary", body={
            "summary": title,
            "description": "Added by Clair Health Platform",
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/New_York"},
            "end":   {"dateTime": end_dt.isoformat(),   "timeZone": "America/New_York"},
        }).execute()
    except Exception: pass

def gcal_move(svc, event_id, new_start, new_end):
    try:
        ev = svc.events().get(calendarId="primary", eventId=event_id).execute()
        ev["start"]["dateTime"] = new_start.isoformat()
        ev["end"]["dateTime"]   = new_end.isoformat()
        svc.events().update(calendarId="primary", eventId=event_id, body=ev).execute()
    except Exception: pass


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────

STRESS_MAP = {"Low": 20, "Medium": 50, "High": 75, "Very High": 92}

@st.cache_data
def load_csvs():
    try:
        health   = pd.read_csv("personal_health_data.csv",    parse_dates=["Timestamp"])
        activity = pd.read_csv("activity_environment_data.csv", parse_dates=["Timestamp"])
        digital  = pd.read_csv("digital_interaction_data.csv",  parse_dates=["Timestamp"])
        for df in [health, activity, digital]:
            df.columns = df.columns.str.strip()
        return health, activity, digital
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}")
        st.stop()

def get_user_ids(health_df) -> List[str]:
    return sorted(health_df["User_ID"].unique().tolist())

def get_user_health(health_df, user_id: str) -> pd.DataFrame:
    df = health_df[health_df["User_ID"] == user_id].copy()
    df = df.sort_values("Timestamp").tail(14).reset_index(drop=True)
    df["sleep_score"]    = df["Health_Score"].clip(0, 100)
    df["stress_numeric"] = df["Stress_Level"].map(STRESS_MAP).fillna(50)
    return df

def get_user_activity(activity_df, user_id: str) -> pd.DataFrame:
    return activity_df[activity_df["User_ID"] == user_id].sort_values("Timestamp").tail(14).reset_index(drop=True)

def get_user_digital(digital_df, user_id: str) -> pd.DataFrame:
    return digital_df[digital_df["User_ID"] == user_id].sort_values("Timestamp").tail(14).reset_index(drop=True)

def compute_signals(health_df, digital_df):
    latest      = health_df.iloc[-1]
    sleep_score = float(latest["sleep_score"])
    stress_base = float(latest["stress_numeric"])
    screen_penalty = min(15, float(digital_df["Screen_Time"].mean()) / 2) if not digital_df.empty else 0
    stress_score   = min(100, stress_base + screen_penalty)
    return sleep_score, stress_score, latest


# ─────────────────────────────────────────────
# DETECTION ENGINE
# ─────────────────────────────────────────────

def detect(sleep: float, stress: float, cycle: str,
           today_row=None, activity_df=None) -> dict:
    issues, recs, sev = [], [], "normal"

    if sleep < 50:
        issues.append(f"POOR_SLEEP  [{sleep:.0f}/100]"); sev = "high"
        recs += ["Reschedule early meetings", "Insert recovery block 13:00-13:20", "Wind-down protocol at 21:30"]
    elif sleep < 70:
        issues.append(f"SUBOPTIMAL_SLEEP  [{sleep:.0f}/100]"); sev = "medium"
        recs.append("Insert post-lunch buffer")

    if stress > 70:
        issues.append(f"HIGH_STRESS  [{stress:.0f}/100]"); sev = "high"
        recs += ["Insert breathing break", "Order Magnesium Glycinate 400mg"]
    elif stress > 50:
        issues.append(f"ELEVATED_STRESS  [{stress:.0f}/100]")
        recs.append("Send stress check-in"); sev = sev if sev == "high" else "medium"

    if cycle in ["luteal", "menstrual"] and stress > 50:
        issues.append(f"CYCLE_AMPLIFICATION  [{cycle}]")
        recs.append("Defer non-urgent meetings")

    extra = {}
    if today_row is not None:
        hr      = today_row.get("Heart_Rate", None)
        bo      = today_row.get("Blood_Oxygen_Level", None)
        mood    = today_row.get("Mood", None)
        wakeups = today_row.get("Wakeups", None)
        if hr      and float(hr)  > 90: issues.append(f"ELEVATED_HR  [{int(hr)} bpm]")
        if bo      and float(bo)  < 95: issues.append(f"LOW_BLOOD_OXYGEN  [{float(bo):.1f}%]")
        if wakeups and int(wakeups) > 3: issues.append(f"FREQUENT_WAKEUPS  [{int(wakeups)}x]")
        extra = {"heart_rate": hr, "blood_oxygen": bo, "mood": mood, "wakeups": wakeups}

    if activity_df is not None and not activity_df.empty:
        avg_steps = float(activity_df["Steps"].mean())
        extra["avg_daily_steps"] = round(avg_steps)
        if avg_steps < 4000:
            issues.append(f"LOW_ACTIVITY  [{round(avg_steps):,} steps/day]")
            recs.append("Schedule 20-min walk")

    return dict(sleep_score=sleep, stress_score=stress, cycle_phase=cycle,
                issues=issues, recommendations=recs, severity=sev,
                extra=extra, timestamp=datetime.now().isoformat())


# ─────────────────────────────────────────────
# INTERVENTION ENGINE
# ─────────────────────────────────────────────

def run_copilot(ctx: dict, calendar: List[dict], gcal_svc=None) -> dict:
    sleep, stress, cycle = ctx["sleep_score"], ctx["stress_score"], ctx["cycle_phase"]
    extra = ctx.get("extra", {})
    today = datetime.now().date()
    log, cal = [], [e.copy() for e in calendar]

    if sleep < 60:
        for e in cal:
            if e["moveable"] and int(e["start"].split("T")[1][:2]) < 10:
                old = e["start"].split("T")[1]
                h, m = 10, 30
                ns = datetime(today.year, today.month, today.day, h, m)
                dur = (datetime.fromisoformat(e["end"]) - datetime.fromisoformat(e["start"])).seconds // 60
                ne  = ns + timedelta(minutes=dur)
                e["start"] = ns.strftime(f"{today}T%H:%M")
                e["end"]   = ne.strftime(f"{today}T%H:%M")
                if gcal_svc and e.get("gcal"): gcal_move(gcal_svc, e["id"], ns, ne)
                log.append(f"RESCHEDULED  '{e['title']}'  {old} -> 10:30"); break

    if sleep < 55:
        sd = datetime(today.year, today.month, today.day, 13, 0)
        ed = datetime(today.year, today.month, today.day, 13, 20)
        cal.append({"id":"nap","title":"Recovery Block","start":f"{today}T13:00",
                    "end":f"{today}T13:20","moveable":True,"new":True})
        if gcal_svc: gcal_create(gcal_svc, "Recovery Block", sd, ed)
        log.append("INSERTED  'Recovery Block'  13:00 - 13:20")

    if stress > 65:
        sd = datetime(today.year, today.month, today.day, 15, 0)
        ed = datetime(today.year, today.month, today.day, 15, 10)
        cal.append({"id":"breath","title":"Breathing Break","start":f"{today}T15:00",
                    "end":f"{today}T15:10","moveable":True,"new":True})
        if gcal_svc: gcal_create(gcal_svc, "Breathing Break", sd, ed)
        log.append("INSERTED  'Breathing Break'  15:00 - 15:10")

    if extra.get("avg_daily_steps", 8000) < 4000:
        sd = datetime(today.year, today.month, today.day, 17, 0)
        ed = datetime(today.year, today.month, today.day, 17, 20)
        cal.append({"id":"walk","title":"Movement Block","start":f"{today}T17:00",
                    "end":f"{today}T17:20","moveable":True,"new":True})
        if gcal_svc: gcal_create(gcal_svc, "Movement Block", sd, ed)
        log.append("INSERTED  'Movement Block'  17:00 - 17:20")

    wellness = []
    wellness.append("NOTIFICATION  [PUSH]  Schedule adjusted based on biometric signals")
    if cycle in ["luteal", "menstrual"]:
        wellness.append(f"NOTIFICATION  [PUSH]  Cycle phase ({cycle}) protocol activated")
    wellness.append("REMINDER  [21:30]  Wind-down protocol — begin sleep preparation")
    if stress > 70:
        wellness.append("ORDER  Magnesium Glycinate 400mg  — cortisol regulation support")
    if extra.get("heart_rate", 70) > 90:
        wellness.append("ALERT  [PUSH]  Elevated resting heart rate detected — reduce load")

    summary = (
        f"Intervention protocol executed. Sleep index {sleep:.0f}/100 and stress index "
        f"{stress:.0f}/100 during {cycle} phase triggered {len(log + wellness)} automated actions. "
        f"Schedule restructured, recovery blocks inserted, and wellness interventions dispatched."
    )
    return {"summary": summary, "schedule_log": log,
            "wellness_log": wellness, "updated_calendar": cal}


# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────

LAYOUT = dict(
    paper_bgcolor="#080f16", plot_bgcolor="#080f16",
    font=dict(color="#8facc8", family="Inter, Segoe UI, sans-serif", size=11),
    margin=dict(t=36, b=20, l=10, r=10),
)

def sleep_chart(df):
    colors = ["#e74c3c" if s < 50 else "#f39c12" if s < 70 else "#2ecc71"
              for s in df["sleep_score"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["sleep_score"], mode="lines+markers",
        line=dict(color="#2d7dd2", width=2),
        marker=dict(color=colors, size=7, line=dict(width=1, color="#080f16")),
        hovertemplate="<b>%{x|%b %d}</b><br>Index: %{y:.0f}<extra></extra>"))
    for v, c, l in [(70, "#2ecc71", "Optimal"), (50, "#e74c3c", "Critical")]:
        fig.add_hline(y=v, line_dash="dot", line_color=c, line_width=1,
                      annotation_text=l, annotation_position="bottom right",
                      annotation_font=dict(color=c, size=10))
    fig.update_layout(title=dict(text="HEALTH INDEX  /  14-DAY", font=dict(size=11, color="#5a7a96")),
                      yaxis_range=[0, 100],
                      xaxis=dict(gridcolor="#0f1e2e", showgrid=True),
                      yaxis=dict(gridcolor="#0f1e2e", showgrid=True), **LAYOUT)
    return fig

def hr_chart(df):
    if "Heart_Rate" not in df.columns: return go.Figure()
    colors = ["#e74c3c" if h > 90 else "#f39c12" if h > 80 else "#2ecc71"
              for h in df["Heart_Rate"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["Heart_Rate"], mode="lines+markers",
        line=dict(color="#c0392b", width=2),
        marker=dict(color=colors, size=7, line=dict(width=1, color="#080f16")),
        hovertemplate="<b>%{x|%b %d}</b><br>%{y} bpm<extra></extra>"))
    fig.add_hline(y=90, line_dash="dot", line_color="#e74c3c", line_width=1,
                  annotation_text="Elevated", annotation_font=dict(color="#e74c3c", size=10))
    fig.update_layout(title=dict(text="HEART RATE  /  BPM", font=dict(size=11, color="#5a7a96")),
                      xaxis=dict(gridcolor="#0f1e2e"),
                      yaxis=dict(gridcolor="#0f1e2e"), **LAYOUT)
    return fig

def steps_chart(df):
    if df.empty or "Steps" not in df.columns: return go.Figure()
    colors = ["#e74c3c" if s < 4000 else "#f39c12" if s < 8000 else "#2ecc71"
              for s in df["Steps"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Timestamp"], y=df["Steps"], marker_color=colors, opacity=0.85,
        hovertemplate="<b>%{x|%b %d}</b><br>%{y:,} steps<extra></extra>"))
    fig.add_hline(y=8000, line_dash="dot", line_color="#2ecc71", line_width=1,
                  annotation_text="Target", annotation_font=dict(color="#2ecc71", size=10))
    fig.update_layout(title=dict(text="DAILY STEPS", font=dict(size=11, color="#5a7a96")),
                      xaxis=dict(gridcolor="#0f1e2e"),
                      yaxis=dict(gridcolor="#0f1e2e"), **LAYOUT)
    return fig

def radar_chart(sleep, stress, cycle, hr=70):
    cyc  = {"follicular": 20, "ovulatory": 15, "luteal": 70, "menstrual": 60}.get(cycle, 30)
    hr_s = max(0, 100 - max(0, hr - 60) * 2)
    vals = [sleep, 100 - stress, 100 - cyc,
            max(0, 100 - (100 - sleep) * .6 - stress * .4), hr_s]
    cats = ["Sleep", "Stress Res.", "Cycle Res.", "Recovery", "Cardiac"]
    vp, cp = vals + [vals[0]], cats + [cats[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vp, theta=cp, fill="toself", name="Current State",
        fillcolor="rgba(45,125,210,.15)", line=dict(color="#2d7dd2", width=2)))
    fig.add_trace(go.Scatterpolar(
        r=[80] * 6, theta=cp, name="Optimal",
        fillcolor="rgba(0,0,0,0)", line=dict(color="#2ecc71", width=1, dash="dot")))
    fig.update_layout(
        title=dict(text="BIOMETRIC PROFILE", font=dict(size=11, color="#5a7a96")),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor="#1a2a3a", tickfont=dict(color="#3d6b8a", size=9)),
            angularaxis=dict(gridcolor="#1a2a3a"),
            bgcolor="#080f16",
        ),
        showlegend=True,
        legend=dict(font=dict(color="#5a7a96", size=10)),
        paper_bgcolor="#080f16",
        font=dict(color="#8facc8"),
        margin=dict(t=36, b=20, l=20, r=20),
    )
    return fig

def cal_chart(events, title, orig=None):
    orig_map = {e["id"]: e for e in (orig or [])}
    fig = go.Figure()
    for e in sorted(events, key=lambda x: x["start"]):
        s  = datetime.fromisoformat(e["start"])
        en = datetime.fromisoformat(e["end"])
        is_new   = e.get("new", False)
        is_moved = (not is_new) and e["id"] in orig_map and orig_map[e["id"]]["start"] != e["start"]
        color = "#1a4a7a" if is_new else "#1a5c35" if is_moved else "#1e2d3d"
        border = "#2d7dd2" if is_new else "#2ecc71" if is_moved else "#2e3a4e"
        label  = e["title"] + (" [NEW]" if is_new else " [MOVED]" if is_moved else "")
        dur    = max((en - s).seconds / 3600, 0.1)
        fig.add_trace(go.Bar(
            y=[label], x=[dur], base=[s.hour + s.minute / 60],
            orientation="h", marker_color=color,
            marker_line_color=border, marker_line_width=1.5,
            showlegend=False,
            hovertemplate=f"<b>{e['title']}</b><br>{s.strftime('%H:%M')} — {en.strftime('%H:%M')}<extra></extra>"))
    fig.update_layout(
        title=dict(text=title, font=dict(size=11, color="#5a7a96")),
        barmode="overlay",
        xaxis=dict(range=[8, 18], tickvals=list(range(8, 19)),
                   ticktext=[f"{h:02d}:00" for h in range(8, 19)],
                   gridcolor="#0f1e2e"),
        yaxis=dict(gridcolor="#0f1e2e"),
        height=max(200, 52 * len(events)),
        **LAYOUT,
    )
    return fig


# ─────────────────────────────────────────────
# BASE CALENDAR
# ─────────────────────────────────────────────

def base_cal():
    t = datetime.now().date()
    return [
        {"id":"ev1","title":"Team Standup",    "start":f"{t}T09:00","end":f"{t}T09:30","moveable":True},
        {"id":"ev2","title":"Deep Work Block", "start":f"{t}T10:00","end":f"{t}T12:00","moveable":False},
        {"id":"ev3","title":"1:1 with Manager","start":f"{t}T14:00","end":f"{t}T14:30","moveable":True},
        {"id":"ev4","title":"Product Review",  "start":f"{t}T16:00","end":f"{t}T17:00","moveable":True},
    ]


# ─────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────

def main():
    # ── Header ─────────────────────────────────
    st.markdown("""
    <div style="border-bottom:1px solid #1e2d3d; padding-bottom:16px; margin-bottom:24px;">
      <div style="font-size:1.35em; font-weight:700; color:#e8edf2; letter-spacing:0.02em;">
        CLAIR HEALTH
      </div>
      <div style="font-size:0.75em; color:#3d6b8a; letter-spacing:0.1em; text-transform:uppercase; margin-top:2px;">
        Health Intelligence Platform &nbsp;|&nbsp; Autonomous Biometric Intervention
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Load data ──────────────────────────────
    health_df, activity_df, digital_df = load_csvs()
    user_ids = get_user_ids(health_df)

    # ── Sidebar ────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="font-size:0.68em;font-weight:700;letter-spacing:0.12em;
                    text-transform:uppercase;color:#3d6b8a;margin-bottom:16px;">
          Platform Controls
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">Patient / User</div>', unsafe_allow_html=True)
        selected_user = st.selectbox("Select User ID", user_ids, index=0, label_visibility="collapsed")

        st.markdown('<div class="section-header">Calendar Integration</div>', unsafe_allow_html=True)
        gcal = get_gcal_service()
        if gcal:
            st.markdown('<div class="status-connected">Google Calendar  —  Connected</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-disconnected">Google Calendar  —  Not Connected</div>',
                        unsafe_allow_html=True)
            with st.expander("Setup Instructions"):
                st.markdown("""
Run `python auth_google.py` after placing `credentials.json`
in the application directory, then refresh.
                """)

        st.markdown('<div class="section-header">Signal Override</div>', unsafe_allow_html=True)
        override = st.toggle("Enable Manual Override")
        c_sleep  = st.slider("Sleep Index",  0, 100, 44) if override else None
        c_stress = st.slider("Stress Index", 0, 100, 76) if override else None
        cycle    = st.selectbox("Cycle Phase",
                                ["follicular", "ovulatory", "luteal", "menstrual"], index=2)

        st.markdown("---")
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            for k in ["res", "cal_before"]: st.session_state.pop(k, None)
            st.rerun()

        st.markdown(f"""
        <div style="font-size:0.72em;color:#3d6b8a;margin-top:12px;line-height:1.8;">
          Calendar &nbsp; {'Connected' if gcal else 'Mock Mode'}<br>
          Last Refresh &nbsp; {datetime.now().strftime('%H:%M:%S')}
        </div>""", unsafe_allow_html=True)

    # ── User data ──────────────────────────────
    user_health   = get_user_health(health_df, selected_user)
    user_activity = get_user_activity(activity_df, selected_user)
    user_digital  = get_user_digital(digital_df, selected_user)

    if user_health.empty:
        st.error(f"No records found for user {selected_user}."); return

    sleep_score, stress_score, today_row = compute_signals(user_health, user_digital)
    sl  = float(c_sleep)  if override else sleep_score
    st_ = float(c_stress) if override else stress_score

    ctx = detect(sl, st_, cycle, today_row, user_activity)
    sev = ctx["severity"]

    # ── KPI Row ────────────────────────────────
    prev_sleep = float(user_health.iloc[-2]["sleep_score"]) if len(user_health) > 1 else sl
    delta      = sl - prev_sleep
    delta_dir  = "up" if delta >= 0 else "down"
    delta_sign = "+" if delta >= 0 else ""
    hr   = today_row.get("Heart_Rate", "—")
    mood = today_row.get("Mood", "—")
    sev_class = {"high": "badge-critical", "medium": "badge-warning", "normal": "badge-normal"}[sev]
    sev_label = {"high": "Critical", "medium": "Warning", "normal": "Normal"}[sev]

    k1, k2, k3, k4, k5 = st.columns(5)
    for col, label, value, delta_html in [
        (k1, "Sleep Index", f"{sl:.0f} <span style='font-size:.5em;color:#5a7a96'>/100</span>",
         f'<div class="metric-delta {delta_dir}">{delta_sign}{delta:.0f} vs prior day</div>'),
        (k2, "Stress Index", f"{st_:.0f} <span style='font-size:.5em;color:#5a7a96'>/100</span>", ""),
        (k3, "Heart Rate", f"{hr} <span style='font-size:.5em;color:#5a7a96'>bpm</span>", ""),
        (k4, "Mood State", f"<span style='font-size:.75em'>{mood}</span>", ""),
        (k5, "Alert Level",
         f'<span class="badge {sev_class}">{sev_label}</span>', ""),
    ]:
        col.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          {delta_html}
        </div>""", unsafe_allow_html=True)

    # ── Issue Flags ────────────────────────────
    if ctx["issues"]:
        st.markdown(
            "<div style='margin:12px 0 4px;font-size:.7em;font-weight:700;"
            "letter-spacing:.1em;text-transform:uppercase;color:#3d6b8a;'>"
            "Active Flags</div>",
            unsafe_allow_html=True)
        st.markdown(
            "".join(f'<span class="issue-tag">{i}</span>' for i in ctx["issues"]),
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="margin:12px 0;padding:8px 14px;background:#0a1f12;'
            'border:1px solid #1a6b3c;border-radius:4px;font-size:.8em;color:#2ecc71;">'
            'All biometric indices within normal parameters.</div>',
            unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────
    st.markdown('<div class="section-header">Biometric Monitoring</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    hr_val = float(today_row.get("Heart_Rate", 70))
    with c1: st.plotly_chart(sleep_chart(user_health),                   use_container_width=True)
    with c2: st.plotly_chart(hr_chart(user_health),                      use_container_width=True)
    with c3: st.plotly_chart(steps_chart(user_activity),                  use_container_width=True)
    with c4: st.plotly_chart(radar_chart(sl, st_, cycle, hr_val),        use_container_width=True)

    with st.expander("Extended Health Panel"):
        s1, s2, s3, s4, s5, s6 = st.columns(6)
        for col, label, val in [
            (s1, "Deep Sleep",    f"{today_row.get('Deep_Sleep_Duration', '—')} hrs"),
            (s2, "REM Sleep",     f"{today_row.get('REM_Sleep_Duration', '—')} hrs"),
            (s3, "Wakeups",       str(today_row.get("Wakeups", "—"))),
            (s4, "Blood O2",      f"{today_row.get('Blood_Oxygen_Level', '—')}%"),
            (s5, "Avg Screen",    f"{user_digital['Screen_Time'].mean():.1f} hrs" if not user_digital.empty else "—"),
            (s6, "Avg Steps",     f"{user_activity['Steps'].mean():,.0f}" if not user_activity.empty else "—"),
        ]:
            col.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div style="font-size:1.3em;font-weight:700;color:#e8edf2;">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Calendar ───────────────────────────────
    st.markdown('<div class="section-header">Schedule Management</div>', unsafe_allow_html=True)

    if "cal_before" not in st.session_state:
        real = load_real_calendar(gcal) if gcal else []
        st.session_state.cal_before = real if real else base_cal()

    if "res" not in st.session_state:
        st.plotly_chart(
            cal_chart(st.session_state.cal_before, "CURRENT SCHEDULE"),
            use_container_width=True)
    else:
        cc1, cc2 = st.columns(2)
        with cc1:
            st.plotly_chart(
                cal_chart(st.session_state.cal_before, "PRE-INTERVENTION"),
                use_container_width=True)
        with cc2:
            st.plotly_chart(
                cal_chart(st.session_state.res["updated_calendar"],
                          "POST-INTERVENTION",
                          orig=st.session_state.cal_before),
                use_container_width=True)
        st.markdown(
            '<div style="font-size:.72em;color:#3d6b8a;margin-top:-8px;">'
            'Green = rescheduled &nbsp;|&nbsp; Blue = inserted &nbsp;|&nbsp; Grey = unchanged'
            '</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Intervention Engine ────────────────────
    st.markdown('<div class="section-header">Intervention Engine</div>', unsafe_allow_html=True)

    if sev == "normal":
        st.markdown(
            '<div style="padding:12px 16px;background:#0a1f12;border:1px solid #1a6b3c;'
            'border-radius:4px;font-size:.85em;color:#2ecc71;">'
            'No intervention required. All indices within acceptable parameters.</div>',
            unsafe_allow_html=True)
    elif "res" not in st.session_state:
        st.markdown(
            '<div style="font-size:.82em;color:#5a7a96;margin-bottom:12px;">'
            f'Detected {len(ctx["issues"])} active flag(s). '
            'Executing intervention protocol will restructure the schedule and dispatch wellness actions.</div>',
            unsafe_allow_html=True)
        if st.button("Execute Intervention Protocol", type="primary", use_container_width=True):
            with st.spinner("Running intervention engine..."):
                time.sleep(1.5)
                result = run_copilot(ctx, [e.copy() for e in st.session_state.cal_before], gcal)
            st.session_state.res = result
            st.rerun()

    if "res" in st.session_state:
        res = st.session_state.res

        ac1, ac2 = st.columns(2)
        with ac1:
            st.markdown(
                '<div style="font-size:.72em;font-weight:700;letter-spacing:.1em;'
                'text-transform:uppercase;color:#3d6b8a;margin-bottom:8px;">Schedule Actions</div>',
                unsafe_allow_html=True)
            for a in res["schedule_log"]:
                st.markdown(f'<div class="action-item">{a}</div>', unsafe_allow_html=True)
            if not res["schedule_log"]:
                st.markdown('<div style="font-size:.8em;color:#3d6b8a;">No schedule modifications required.</div>',
                            unsafe_allow_html=True)
        with ac2:
            st.markdown(
                '<div style="font-size:.72em;font-weight:700;letter-spacing:.1em;'
                'text-transform:uppercase;color:#3d6b8a;margin-bottom:8px;">Wellness Actions</div>',
                unsafe_allow_html=True)
            for a in res["wellness_log"]:
                st.markdown(f'<div class="action-item wellness">{a}</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="summary-box" style="margin-top:16px;">'
            f'<strong style="color:#8facc8;">Intervention Summary</strong><br>{res["summary"]}'
            f'</div>', unsafe_allow_html=True)

        if st.button("Reset Session", use_container_width=True):
            for k in ["res", "cal_before"]: st.session_state.pop(k, None)
            st.rerun()

    # ── Footer ─────────────────────────────────
    st.markdown("""
    <div style="margin-top:40px;border-top:1px solid #1e2d3d;padding-top:14px;
                font-size:.68em;color:#2a3d50;letter-spacing:.06em;
                display:flex;justify-content:space-between;">
      <span>CLAIR HEALTH  &nbsp;|&nbsp;  Health Intelligence Platform</span>
      <span>Data: Personal Health  /  Activity  /  Digital Interaction</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()