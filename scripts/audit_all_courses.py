#!/usr/bin/env python3
"""
Audit All Courses - Deep LMS Activity & Gradebook Auditor
Performs item-level verification across all course modules:
- Verifies every SCORM pre-test and post-test status ('Done: Pass') and grade ('100%')
- Verifies feedback questionnaires ('Done: Submit feedback')
- Verifies Course Outline overall progress badge ('Your progress 100%')
- Exports detailed audit findings to JSON
"""

import sys
import time
import json
import re
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from chrome_helper import exec_js_in_mastery_tab, navigate_to

ALL_COURSES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17]

def check_course(cid):
    navigate_to(f"https://mastery-ku.com/course/view.php?id={cid}")
    time.sleep(2)
    
    info = exec_js_in_mastery_tab(r'''
    return {
        title: document.title,
        progress: document.querySelector('.section-box-progress')?.innerText || '',
        scorm_links: Array.from(document.querySelectorAll('a[href*="/mod/scorm/view.php?id="]')).map(a => ({ name: a.innerText.trim(), href: a.href })),
        feedback_links: Array.from(document.querySelectorAll('a[href*="/mod/feedback/view.php?id="]')).map(a => ({ name: a.innerText.trim(), href: a.href })),
        buttons: Array.from(document.querySelectorAll('button.mb2modalsection[data-counter]')).map(b => ({
            counter: b.getAttribute('data-counter'),
            label: ((b.getAttribute('aria-label') || '') + ' ' + b.innerText).trim()
        }))
    };
    ''')
    
    scorms = []
    feedbacks = []
    h5ps = []
    
    for btn in info.get("buttons", []):
        counter = btn["counter"]
        exec_js_in_mastery_tab(f'''
        const b = document.querySelector('button.mb2modalsection[data-counter="{counter}"]') || document.querySelector('button[data-counter="{counter}"]');
        if (b) b.click();
        ''')
        for _ in range(10):
            time.sleep(0.3)
            ready = exec_js_in_mastery_tab(r'''
            const modal = document.querySelector('#mb2modalsection');
            const active = modal ? modal.querySelector('.single-section.active') : null;
            return active && !active.querySelector('.preload');
            ''')
            if ready:
                break
                
        sec_items = exec_js_in_mastery_tab(r'''
        const modal = document.querySelector('#mb2modalsection');
        const active = modal ? modal.querySelector('.single-section.active') : null;
        if (!active) return [];
        const res = [];
        active.querySelectorAll('.activity').forEach(act => {
            const link = act.querySelector('a')?.href || '';
            const name = act.querySelector('.instancename')?.innerText || act.innerText;
            const completion = act.querySelector('.automatic-completion-conditions, .manual-completion')?.innerText || '';
            res.push({ id: act.id, name: name.replace(/\s+/g, ' ').trim(), link, completion: completion.replace(/\s+/g, ' ').trim() });
        });
        return res;
        ''')
        
        for it in (sec_items or []):
            if '/mod/scorm/' in it['link']:
                scorms.append(it)
            elif '/mod/feedback/' in it['link']:
                feedbacks.append(it)
            elif '/mod/h5pactivity/' in it['link']:
                h5ps.append(it)
                
    # Check each SCORM view page
    scorm_details = []
    for sc in scorms:
        navigate_to(sc['link'])
        time.sleep(1.5)
        text = exec_js_in_mastery_tab(r'''
        const el = document.querySelector('#region-main');
        return el ? el.innerText : '';
        ''')
        passed = 'Done: Pass' in text or 'ผ่านกิจกรรม' in text
        m = re.search(r'Grade reported:\s*(\d+)%', text)
        grade = m.group(1) if m else ('100' if 'สูงสุด: 100' in text else 'unknown')
        scorm_details.append({
            "name": sc['name'],
            "link": sc['link'],
            "passed": passed,
            "grade": grade,
            "raw_snippet": text[:200].replace('\n', ' ')
        })
        
    # Check each feedback view page
    fb_details = []
    for fb in feedbacks:
        navigate_to(fb['link'])
        time.sleep(1.5)
        text = exec_js_in_mastery_tab(r'''
        const el = document.querySelector('#region-main');
        return el ? el.innerText : '';
        ''')
        submitted = 'ท่านส่งแบบสอบถามไปเรียบร้อยแล้ว' in text or 'Done: Submit feedback' in text or 'Your response has been submitted' in text
        fb_details.append({
            "name": fb['name'],
            "link": fb['link'],
            "submitted": submitted,
            "raw_snippet": text[:200].replace('\n', ' ')
        })
        
    return {
        "course_id": cid,
        "title": info.get("title", ""),
        "progress": info.get("progress", ""),
        "h5p_count": len(h5ps),
        "scorms": scorm_details,
        "feedbacks": fb_details
    }

def main():
    target = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else ALL_COURSES
    results = []
    print(f"Auditing courses: {target}")
    for cid in target:
        print(f"Auditing Course {cid}...")
        res = check_course(cid)
        results.append(res)
        print(f"Result for Course {cid}: Progress={res['progress']}, SCORMs={len(res['scorms'])}, Feedbacks={len(res['feedbacks'])}")
        
    out_file = Path(__file__).resolve().parent / "full_audit_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"\nAudit complete! Saved to {out_file}")

if __name__ == '__main__':
    main()
