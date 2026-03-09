"""
post-to-bluesky.py
OBS Python Script — Posts to your Bluesky feed when you go live.
URLs and hashtags in your post text are automatically made clickable.

HOW TO INSTALL:
  1. In OBS, go to Tools → Scripts
  2. Click the "+" button and select this file
  3. Fill in your details in the config panel on the right
  4. That's it! The script posts automatically when you start streaming.

Use a Bluesky App Password — NOT your main account password.
Generate one at: Bluesky → Settings → Privacy and Security → App Passwords
"""

import obspython as obs
import urllib.request
import urllib.error
import json
import re
from datetime import datetime, timezone

# ─── Globals (populated from OBS settings UI) ────────────────────────────────
handle     = ""
password   = ""
post_text  = ""
pds_host   = "https://bsky.social"
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


def build_facets(text):
    """
    Detect URLs and hashtags and return Bluesky facet objects.
    Bluesky requires UTF-8 byte positions, not character positions.
    """
    facets  = []
    encoded = text.encode("utf-8")

    # Find URLs
    for match in re.finditer(r"https?://[^\s]+", text):
        byte_start = len(text[:match.start()].encode("utf-8"))
        byte_end   = len(text[:match.end()].encode("utf-8"))
        facets.append({
            "index":    {"byteStart": byte_start, "byteEnd": byte_end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": match.group()}]
        })

    # Find hashtags
    for match in re.finditer(r"#\w+", text):
        byte_start = len(text[:match.start()].encode("utf-8"))
        byte_end   = len(text[:match.end()].encode("utf-8"))
        facets.append({
            "index":    {"byteStart": byte_start, "byteEnd": byte_end},
            "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": match.group()[1:]}]
        })

    return facets


def create_post():
    """Authenticate and create a post on Bluesky."""
    try:
        session = create_session()
        record  = {
            "$type":     "app.bsky.feed.post",
            "text":      post_text,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "facets":    build_facets(post_text)
        }
        body = json.dumps({
            "repo":       session["did"],
            "collection": "app.bsky.feed.post",
            "record":     record
        }).encode()
        req = urllib.request.Request(
            f"{pds_host}/xrpc/com.atproto.repo.createRecord",
            data=body,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {session['accessJwt']}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read())
        print(f"[Bluesky] ✅ Post created: {result['uri']}")
    except Exception as e:
        print(f"[Bluesky] ❌ Post failed: {e}")


# ─── OBS Event Hook ──────────────────────────────────────────────────────────

def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED:
        create_post()


# ─── OBS Script Lifecycle ────────────────────────────────────────────────────

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)


def script_unload():
    obs.obs_frontend_remove_event_callback(on_event)


def script_update(settings):
    global handle, password, post_text
    handle    = obs.obs_data_get_string(settings, "handle")
    password  = obs.obs_data_get_string(settings, "password")
    post_text = obs.obs_data_get_string(settings, "post_text")


def script_defaults(settings):
    obs.obs_data_set_default_string(
        settings, "post_text",
        "https://twitch.tv/yourchannel Come hang! #YourHashtag"
    )


def script_description():
    return (
        "<h3>Bluesky Stream Announcement</h3>"
        "Automatically posts to your Bluesky feed when you start streaming. "
        "URLs and #hashtags in your post text are made clickable automatically.<br><br>"
        "Keep your post under <b>300 characters</b>.<br><br>"
        "Use a Bluesky <b>App Password</b>, not your main account password.<br>"
        "Generate one at: <b>Bluesky → Settings → Privacy and Security → App Passwords</b>"
    )


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "handle",    "Bluesky Handle", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "password",  "App Password",   obs.OBS_TEXT_PASSWORD)
    obs.obs_properties_add_text(props, "post_text", "Post Text (max 300 characters)", obs.OBS_TEXT_MULTILINE)

    return props
