"""
bsky-live-status.py
OBS Python Script — Sets and clears your Bluesky LIVE status automatically.

HOW TO INSTALL:
  1. In OBS, go to Tools → Scripts
  2. Click the "+" button and select this file
  3. Fill in your details in the config panel on the right
  4. That's it! The script runs automatically when you go live or end your stream.

Use a Bluesky App Password — NOT your main account password.
Generate one at: Bluesky → Settings → Privacy and Security → App Passwords
"""

import obspython as obs
import urllib.request
import urllib.error
import json
from datetime import datetime, timezone

# ─── Globals (populated from OBS settings UI) ────────────────────────────────
handle         = ""
password       = ""
stream_url     = ""
stream_title   = ""
stream_desc    = ""
duration_mins  = 240
pds_host       = "https://bsky.social"
# ─────────────────────────────────────────────────────────────────────────────


def create_session():
    """Authenticate with Bluesky and return the session."""
    payload = json.dumps({"identifier": handle, "password": password}).encode()
    req = urllib.request.Request(
        f"{pds_host}/xrpc/com.atproto.server.createSession",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())


def set_live_status():
    """Write the LIVE status record to the user's PDS."""
    try:
        session = create_session()
        record = {
            "$type":    "app.bsky.actor.status",
            "status":   "app.bsky.actor.status#live",
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "embed": {
                "$type": "app.bsky.embed.external",
                "external": {
                    "uri":         stream_url,
                    "title":       stream_title,
                    "description": stream_desc
                }
            },
            "durationMinutes": duration_mins  # Required for badge to appear. Max is 240 (4 hrs).
        }
        body = json.dumps({
            "repo":       session["did"],
            "collection": "app.bsky.actor.status",
            "rkey":       "self",
            "record":     record
        }).encode()
        req = urllib.request.Request(
            f"{pds_host}/xrpc/com.atproto.repo.putRecord",
            data=body,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {session['accessJwt']}"
            },
            method="POST"
        )
        urllib.request.urlopen(req)
        print("[Bluesky] ✅ Status set to LIVE")
    except Exception as e:
        print(f"[Bluesky] ❌ Failed to set status: {e}")


def clear_live_status():
    """Delete the LIVE status record from the user's PDS."""
    try:
        session = create_session()
        body = json.dumps({
            "repo":       session["did"],
            "collection": "app.bsky.actor.status",
            "rkey":       "self"
        }).encode()
        req = urllib.request.Request(
            f"{pds_host}/xrpc/com.atproto.repo.deleteRecord",
            data=body,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {session['accessJwt']}"
            },
            method="POST"
        )
        try:
            urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            if e.code != 400:  # 400 RecordNotFound is fine — already cleared
                raise
        print("[Bluesky] ✅ Status cleared")
    except Exception as e:
        print(f"[Bluesky] ❌ Failed to clear status: {e}")


# ─── OBS Event Hook ──────────────────────────────────────────────────────────

def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED:
        set_live_status()
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPED:
        clear_live_status()


# ─── OBS Script Lifecycle ────────────────────────────────────────────────────

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)


def script_unload():
    obs.obs_frontend_remove_event_callback(on_event)


def script_update(settings):
    global handle, password, stream_url, stream_title, stream_desc, duration_mins
    handle        = obs.obs_data_get_string(settings, "handle")
    password      = obs.obs_data_get_string(settings, "password")
    stream_url    = obs.obs_data_get_string(settings, "stream_url")
    stream_title  = obs.obs_data_get_string(settings, "stream_title")
    stream_desc   = obs.obs_data_get_string(settings, "stream_desc")
    duration_mins = obs.obs_data_get_int(settings,    "duration_mins")


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "stream_title",  "Live Now!")
    obs.obs_data_set_default_string(settings, "stream_desc",   "Come hang!")
    obs.obs_data_set_default_int(   settings, "duration_mins", 240)


def script_description():
    return (
        "<h3>Bluesky Live Status</h3>"
        "Automatically sets your Bluesky profile to <b>LIVE</b> when you start "
        "streaming, and clears it when you stop.<br><br>"
        "Fill in your details below. Use a Bluesky <b>App Password</b>, "
        "not your main account password.<br>"
        "Generate one at: <b>Bluesky → Settings → Privacy and Security → App Passwords</b>"
    )


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "handle",       "Bluesky Handle",   obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "password",     "App Password",     obs.OBS_TEXT_PASSWORD)
    obs.obs_properties_add_text(props, "stream_url",   "Stream URL",       obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "stream_title", "Link Card Title",  obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "stream_desc",  "Link Card Description", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int( props, "duration_mins","Duration (minutes, max 240)", 1, 240, 1)

    return props
