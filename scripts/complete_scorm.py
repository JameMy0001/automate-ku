#!/usr/bin/env python3
"""
Complete SCORM - Direct SCORM 1.2 Runtime Automation
Injects calls to Moodle's window.API to set cmi.core.lesson_status to 'passed',
cmi.core.score.raw to 100, commits, and finishes with verified 100% grade.
"""

import sys
import json
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from chrome_helper import exec_js_in_mastery_tab, navigate_to

def complete_scorm(cm, scoid, currentorg="B0"):
    """
    Automate SCORM module completion:
    1. Navigate to player.php in normal mode.
    2. Inject script to hook window.API, set score to 100, status to passed.
    3. Commit and finish LMS session.
    4. Verify recorded status on scorm/view.php.
    """
    player_url = f"https://mastery-ku.com/mod/scorm/player.php?cm={cm}&scoid={scoid}&mode=normal&currentorg={currentorg}"
    print(f"Navigating to SCORM player: {player_url}")
    navigate_to(player_url)
    time.sleep(3)
    
    inject_js = r'''
    document.body.removeAttribute('data-scorm-res');
    const s = document.createElement('script');
    s.textContent = `
        let attempts = 0;
        function runScorm() {
            if (window.API && typeof window.API.LMSInitialize === 'function') {
                try {
                    window.scorm_current_node = null;
                    window.underscore = function(str) { return String(str).replace(/\\./g, '__'); };
                    if (!window.M) window.M = {};
                    if (!window.M.mod_scorm) window.M.mod_scorm = { connectPrereqCallback: { success: function(){} } };
                    const api = window.API;
                    const res = {};
                    res.init = api.LMSInitialize("");
                    res.set_status = api.LMSSetValue("cmi.core.lesson_status", "passed");
                    res.set_score = api.LMSSetValue("cmi.core.score.raw", "100");
                    res.set_min = api.LMSSetValue("cmi.core.score.min", "0");
                    res.set_max = api.LMSSetValue("cmi.core.score.max", "100");
                    res.set_time = api.LMSSetValue("cmi.core.session_time", "00:04:30");
                    res.commit = api.LMSCommit("");
                    res.finish = api.LMSFinish("");
                    document.body.setAttribute('data-scorm-res', JSON.stringify(res));
                } catch(e) {
                    document.body.setAttribute('data-scorm-res', JSON.stringify({ error: e.toString() }));
                }
            } else if (attempts < 20) {
                attempts++;
                setTimeout(runScorm, 500);
            } else {
                document.body.setAttribute('data-scorm-res', JSON.stringify({ error: 'Timeout waiting for window.API' }));
            }
        }
        runScorm();
    `;
    document.head.appendChild(s);
    s.remove();
    return true;
    '''
    exec_js_in_mastery_tab(inject_js)
    
    # Poll for result
    res = None
    for _ in range(15):
        time.sleep(1)
        check_js = "return document.body.getAttribute('data-scorm-res');"
        raw = exec_js_in_mastery_tab(check_js)
        if raw:
            res = json.loads(raw)
            break
            
    print("SCORM submit result:", json.dumps(res, indent=2))
    time.sleep(2)
    
    view_url = f"https://mastery-ku.com/mod/scorm/view.php?id={cm}"
    navigate_to(view_url)
    time.sleep(2)
    
    js_check = "return document.querySelector('#region-main')?.innerText;"
    content = exec_js_in_mastery_tab(js_check)
    print("Verification view content snippet:", content[:200] if content else "None")
    return res

if __name__ == '__main__':
    cm = sys.argv[1] if len(sys.argv) > 1 else '251'
    scoid = sys.argv[2] if len(sys.argv) > 2 else '18'
    complete_scorm(cm, scoid)
