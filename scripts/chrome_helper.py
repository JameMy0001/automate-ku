#!/usr/bin/env python3
"""
Chrome Helper - AppleScript Bridge for KU Mastery Automation
Provides seamless execution of JavaScript in the active mastery-ku.com tab
and programmatic navigation without requiring remote debugging ports.
"""

import subprocess
import base64
import json
import time

def run_applescript(scpt: str) -> str:
    """Execute raw AppleScript command and return stripped stdout."""
    p = subprocess.run(['osascript', '-e', scpt], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"AppleScript error: {p.stderr}")
    return p.stdout.strip()

def exec_js_in_mastery_tab(js_code: str):
    """
    Execute JavaScript inside the active Google Chrome tab pointing to mastery-ku.com.
    Uses UTF-8 base64 encoding to support complex logic, quotes, and Thai strings.
    """
    b64 = base64.b64encode(js_code.encode('utf-8')).decode('ascii')
    applescript = f'''
    tell application "Google Chrome"
        repeat with w in every window
            repeat with t in every tab of w
                if (URL of t as text) contains "mastery-ku.com" then
                    tell t
                        set res to execute javascript "(() => {{
                            try {{
                                const raw = atob('{b64}');
                                const bytes = new Uint8Array(raw.length);
                                for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
                                const code = new TextDecoder().decode(bytes);
                                const fn = new Function(code);
                                const val = fn();
                                return JSON.stringify({{ ok: true, value: val }});
                            }} catch (e) {{
                                return JSON.stringify({{ ok: false, error: e.toString(), stack: e.stack }});
                            }}
                        }})()"
                        return res
                    end tell
                end if
            end repeat
        end repeat
        error "No mastery-ku.com tab found in Google Chrome"
    end tell
    '''
    raw = run_applescript(applescript)
    data = json.loads(raw)
    if not data.get('ok'):
        raise RuntimeError(f"JS Execution Error: {data.get('error')}\n{data.get('stack')}")
    return data.get('value')

def get_current_url() -> str:
    """Retrieve the current URL of the active mastery-ku.com tab."""
    applescript = '''
    tell application "Google Chrome"
        repeat with w in every window
            repeat with t in every tab of w
                if (URL of t as text) contains "mastery-ku.com" then
                    return URL of t as text
                end if
            end repeat
        end repeat
        error "No mastery-ku.com tab found in Google Chrome"
    end tell
    '''
    return run_applescript(applescript)

def navigate_to(url: str) -> str:
    """Navigate the mastery-ku.com tab to the specified URL."""
    applescript = f'''
    tell application "Google Chrome"
        repeat with w in every window
            repeat with t in every tab of w
                if (URL of t as text) contains "mastery-ku.com" then
                    set URL of t to "{url}"
                    return "OK"
                end if
            end repeat
        end repeat
        error "No mastery-ku.com tab found in Google Chrome"
    end tell
    '''
    return run_applescript(applescript)

if __name__ == '__main__':
    url = get_current_url()
    print("Current URL:", url)
    title = exec_js_in_mastery_tab("return document.title;")
    print("Page Title:", title)
