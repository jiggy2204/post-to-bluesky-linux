# Bluesky Auto Live Status for Streamers — Linux

Automatically set your Bluesky profile to **LIVE** when you start streaming, and clear it when you're done — directly inside OBS. No terminal. No extra software. No file editing.

---

## What You'll Need

- [OBS](https://obsproject.com/) *(already installed if you're streaming)*
- Python 3 *(pre-installed on Ubuntu, Debian, Fedora, Arch, and most other distros)*
- A [Bluesky](https://bsky.app) account

---

## Step 1 — Get a Bluesky App Password

You'll use an **App Password** instead of your real Bluesky password. This keeps your account safe — if it's ever accidentally exposed, you just delete it and make a new one without changing your login.

1. Log into Bluesky
2. Go to **Settings → Privacy and Security → App Passwords**
3. Click **Add App Password**, give it a name like `stream-bot`
4. Copy the password it gives you — it looks like `xxxx-xxxx-xxxx-xxxx`

---

## Step 2 — Download the Scripts

Save these files somewhere stable on your computer, for example `~/streaming/bluesky/`:

- `bsky-live-status.py` — sets your LIVE badge when you go live, clears it when you stop
- `post-to-bluesky.py` *(optional)* — posts to your Bluesky feed when you go live

You don't need to open or edit them. All setup is done inside OBS.

---

## Step 3 — Check Your Python Path

Before adding the scripts, OBS needs to know where Python is installed on your system.

1. Open a terminal and run:
   ```
   which python3
   ```
2. Copy the result — it will look like `/usr/bin/python3`
3. In OBS, go to **Tools → Scripts**
4. Click the **Python Settings** tab at the top of the Scripts window
5. Paste your Python path into the **Python Install Path** field
6. Click **Close**

> If you don't see a Python Settings tab, your version of OBS has Python support built in and you can skip this step.

---

## Step 4 — Add the Scripts to OBS

For each script you want to use:

1. In OBS, go to **Tools → Scripts**
2. Click the **+** button at the bottom left of the window
3. Navigate to where you saved the `.py` file and select it
4. The script will appear in the list — click it to see its settings on the right

---

## Step 5 — Fill In Your Details

Click each script in the list to see its settings panel. Fill in the fields on the right side of the window.

**bsky-live-status.py:**

| Field | What to enter |
|---|---|
| Bluesky Handle | Your handle, e.g. `yourname.bsky.social` |
| App Password | The password from Step 1 *(shown as dots)* |
| Stream URL | Your stream link, e.g. `https://twitch.tv/yourchannel` |
| Link Card Title | Shown on the clickable card, e.g. `Live Now!` |
| Link Card Description | e.g. `Come hang!` |
| Duration (minutes) | Leave at `240` — this is the maximum Bluesky allows |

**post-to-bluesky.py** *(if using)*:

| Field | What to enter |
|---|---|
| Bluesky Handle | Same as above |
| App Password | Same as above |
| Post Text | Your announcement, e.g. `https://twitch.tv/yourchannel Come hang! #YourHashtag` |

> **Post Text tips:** URLs and `#hashtags` are made clickable automatically. Keep it under **300 characters** (Bluesky's limit). Update this field whenever your stream content changes.

Settings save automatically — there's no save button needed.

---

## Step 6 — Test It

1. In OBS, start a stream as normal
2. Check your Bluesky profile — the LIVE badge should appear within a few seconds *(you may need to refresh)*
3. End the stream — the badge clears automatically

If you want to check for errors, click **Script Log** at the bottom of the Tools → Scripts window. Any issues will be shown there.

---

## Troubleshooting

**The badge never shows up**
Make sure the Duration field is set to `240`. Bluesky requires a duration value to display the LIVE badge — it won't appear without one.

**Auth failed error in the Script Log**
Double-check your Bluesky Handle and App Password in the settings panel. Make sure you're using an App Password, not your regular login password.

**OBS doesn't load the script / Python error**
Make sure the Python path is set correctly in the Python Settings tab (see Step 3). Run `which python3` in a terminal to confirm your path.

**Script loads but the badge never fires**
These scripts respond to streaming events specifically — not recordings. Make sure you're starting an actual stream, not just a local recording.

**I installed OBS via Flatpak and Python isn't working**
Flatpak OBS runs in a sandbox that can make Python support tricky. The easiest fix is to install OBS via your distro's package manager instead (e.g. `sudo apt install obs-studio` on Ubuntu/Debian). Alternatively, check the [OBS Flatpak Python guide](https://obsproject.com/forum/resources/flatpak-obs-python-scripting.1571/) on the OBS forums.

---

## Notes

- Bluesky enforces a maximum status duration of **4 hours (240 minutes)** regardless of what you set. The badge clears automatically when you end your stream — the duration is just a safety fallback in case OBS closes unexpectedly.
- Each streamer needs their own copy of the scripts with their own credentials filled in via the OBS settings panel.
- If your App Password is ever accidentally shared or exposed, revoke it immediately in Bluesky settings and generate a new one. Your main account password is never at risk.

---

*Built using the [AT Protocol](https://atproto.com/) and [Bluesky lexicons](https://github.com/bluesky-social/atproto/tree/main/lexicons/app/bsky/actor).*
