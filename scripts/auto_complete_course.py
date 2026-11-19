#!/usr/bin/env python3
"""
Auto Complete Course - End-to-End Single Course Automation Orchestrator
Automates all sections of a specified KU Mastery course:
1. Pre-test SCORM (100% score)
2. Interactive H5P lessons
3. Post-test SCORM (100% score)
4. Feedback Survey submission
5. Course progress verification (100% Complete)
Includes programmatic defensive guard preventing any mutation on Course 17.
"""

import sys
import time
import json
import re
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from chrome_helper import exec_js_in_mastery_tab, navigate_to, get_current_url
from complete_scorm import complete_scorm
from complete_feedback import complete_current_feedback

def get_scorm_status_and_info(cmid):
    """Fetch scoid, currentorg and completion status from SCORM view page."""
    url = f"https://mastery-ku.com/mod/scorm/view.php?id={cmid}"
    navigate_to(url)
    time.sleep(2)
    js = r'''
    const text = document.querySelector('#region-main')?.innerText || '';
    const isDone = text.includes('Done: Pass') || text.includes('ผ่านกิจกรรม') || (text.includes('สูงสุด: 100') && !text.includes('To do'));
    const enterForm = document.querySelector('form[action*="player.php"]');
    const inputs = {};
    if (enterForm) {
        enterForm.querySelectorAll('input').forEach(i => { inputs[i.name] = i.value; });
    }
    return { isDone, inputs };
    '''
    info = exec_js_in_mastery_tab(js)
    return info

def wait_for_modal_ready():
    """Wait until modal active section has finished loading."""
    for _ in range(12):
        time.sleep(1)
        is_ready = exec_js_in_mastery_tab(r'''
        const modal = document.querySelector('#mb2modalsection');
        if (!modal) return false;
        const active = modal.querySelector('.single-section.active');
        if (!active) return false;
        return !active.querySelector('.preload');
        ''')
        if is_ready:
            return True
    return False

def detect_sections():
    """Detect dynamic section counters for lessons, pretest, posttest, and feedback."""
    detect_js = r'''
    const btns = Array.from(document.querySelectorAll("button.mb2modalsection[data-counter]"));
    function findCounter(type) {
        const b = btns.find(btn => {
            const label = ((btn.getAttribute("aria-label") || "") + " " + btn.innerText).toLowerCase();
            if (type === "pretest") return label.includes("pre-test") || label.includes("ก่อนเรียน");
            if (type === "lessons") return label.includes("บทเรียน") || label.includes("h5p");
            if (type === "posttest") return (label.includes("post-test") || label.includes("หลังเรียน")) && !label.includes("แบบสอบถาม");
            if (type === "feedback") return label.includes("แบบสอบถาม") || label.includes("feedback") || label.includes("ความพึงพอใจ") || label.includes("แบบสำรวจ");
            return false;
        });
        return b ? b.getAttribute("data-counter") : null;
    }
    return {
        lessons: findCounter("lessons") || "1",
        pretest: findCounter("pretest") || "2",
        posttest: findCounter("posttest") || "3",
        feedback: findCounter("feedback") || "4"
    };
    '''
    return exec_js_in_mastery_tab(detect_js)

def complete_h5p_in_course(course_id, counter="1"):
    """Iteratively complete all H5P activities in Lessons section."""
    print(f"\n--- Completing Lessons (H5P) [Section {counter}] ---")
    for attempt in range(50):
        # Open modal if not open
        exec_js_in_mastery_tab(f'''
        const modal = document.querySelector('#mb2modalsection');
        const active = modal ? modal.querySelector('.single-section.active') : null;
        if (!active || active.querySelector('.preload')) {{
            const b = document.querySelector('button.mb2modalsection[data-counter="{counter}"]') || document.querySelector('button[data-counter="{counter}"]');
            if (b) b.click();
        }}
        ''')
        
        if not wait_for_modal_ready():
            print(f"[H5P loop {attempt+1}] Refreshing page to recover modal...")
            navigate_to(f"https://mastery-ku.com/course/view.php?id={course_id}")
            time.sleep(3)
            exec_js_in_mastery_tab(f'''
            const b = document.querySelector('button.mb2modalsection[data-counter="{counter}"]') || document.querySelector('button[data-counter="{counter}"]');
            if (b) b.click();
            ''')
            if not wait_for_modal_ready():
                print(f"[H5P loop {attempt+1}] Modal failed to become ready.")
                continue
            
        # Find all mark-as-done buttons and click
        click_script = r'''
        const modal = document.querySelector('#mb2modalsection');
        const active = modal ? modal.querySelector('.single-section.active') : null;
        if (!active) return { count: 0, cmids: [] };
        const markBtns = Array.from(active.querySelectorAll('button[data-action="toggle-manual-completion"], button[data-toggletype="manual:mark-done"]')).filter(b => {
            const txt = b.innerText.trim();
            return txt.includes('Mark as done') || txt.includes('ทำเครื่องหมายว่าเสร็จแล้ว');
        });
        const cmids = markBtns.map(b => b.getAttribute('data-cmid'));
        markBtns.forEach(b => b.click());
        return { count: markBtns.length, cmids: cmids };
        '''
        res = exec_js_in_mastery_tab(click_script)
        print(f"[H5P loop {attempt+1}]", res)
        if not res or res.get('count', 0) == 0:
            print(f"No more 'Mark as done' buttons found in Section {counter}!")
            break
        time.sleep(5)

def complete_course(course_id):
    """Execute complete workflow for a given course ID."""
    if int(course_id) == 17:
        raise ValueError("Course 17 (02 - Workshop & Certificate Information) is strictly excluded and must NOT be processed.")

    print(f"\n==========================================")
    print(f"STARTING COMPLETION FOR COURSE ID: {course_id}")
    print(f"==========================================")
    
    # 1. Open course view
    navigate_to(f"https://mastery-ku.com/course/view.php?id={course_id}")
    time.sleep(3)
    
    js_boxes = r'''
    return {
        title: document.title,
        progress: document.querySelector('.section-box-progress')?.innerText || '',
        boxes: Array.from(document.querySelectorAll('.section-box.theme-box')).map(b => b.innerText.replace(/\n+/g, ' | '))
    };
    '''
    info = exec_js_in_mastery_tab(js_boxes)
    print(f"Course Title: {info.get('title')}")
    print(f"Initial Progress: {info.get('progress')}")
    
    sections = detect_sections()
    print("Detected sections:", json.dumps(sections))
    
    # 2. Check Pre-test
    pre_cnt = sections.get('pretest', '2')
    print(f"\n--- Checking Section {pre_cnt} (Pre-test) ---")
    exec_js_in_mastery_tab(f'''
    const b = document.querySelector('button.mb2modalsection[data-counter="{pre_cnt}"]') || document.querySelector('button[data-counter="{pre_cnt}"]');
    if (b) b.click();
    ''')
    if wait_for_modal_ready():
        js_s2 = r'''
        const modal = document.querySelector('#mb2modalsection');
        const a = modal ? modal.querySelector('a[href*="/mod/scorm/"]') : null;
        return a ? a.href : null;
        '''
        pre_scorm_link = exec_js_in_mastery_tab(js_s2)
        if pre_scorm_link:
            m = re.search(r'id=(\d+)', pre_scorm_link)
            if m:
                pre_cmid = m.group(1)
                print(f"Pre-test SCORM cmid: {pre_cmid}")
                sinfo = get_scorm_status_and_info(pre_cmid)
                if sinfo.get('isDone'):
                    print(f"Pre-test SCORM {pre_cmid} is already passed!")
                elif sinfo.get('inputs') and 'scoid' in sinfo['inputs']:
                    inputs = sinfo['inputs']
                    complete_scorm(pre_cmid, inputs['scoid'], inputs.get('currentorg', 'B0'))
                    
    # 3. Complete H5P lessons
    lessons_cnt = sections.get('lessons', '1')
    complete_h5p_in_course(course_id, counter=lessons_cnt)
    
    # 4. Check Post-test
    post_cnt = sections.get('posttest', '3')
    print(f"\n--- Checking Section {post_cnt} (Post-test) ---")
    navigate_to(f"https://mastery-ku.com/course/view.php?id={course_id}")
    time.sleep(3)
    exec_js_in_mastery_tab(f'''
    const b = document.querySelector('button.mb2modalsection[data-counter="{post_cnt}"]') || document.querySelector('button[data-counter="{post_cnt}"]');
    if (b) b.click();
    ''')
    if wait_for_modal_ready():
        js_s3 = r'''
        const modal = document.querySelector('#mb2modalsection');
        const a = modal ? modal.querySelector('a[href*="/mod/scorm/"]') : null;
        return a ? a.href : null;
        '''
        post_scorm_link = exec_js_in_mastery_tab(js_s3)
        if post_scorm_link:
            m = re.search(r'id=(\d+)', post_scorm_link)
            if m:
                post_cmid = m.group(1)
                print(f"Post-test SCORM cmid: {post_cmid}")
                sinfo = get_scorm_status_and_info(post_cmid)
                if sinfo.get('isDone'):
                    print(f"Post-test SCORM {post_cmid} is already passed!")
                elif sinfo.get('inputs') and 'scoid' in sinfo['inputs']:
                    inputs = sinfo['inputs']
                    complete_scorm(post_cmid, inputs['scoid'], inputs.get('currentorg', 'B0'))
                    
    # 5. Check Feedback
    fb_cnt = sections.get('feedback', '4')
    print(f"\n--- Checking Section {fb_cnt} (Feedback Survey) ---")
    navigate_to(f"https://mastery-ku.com/course/view.php?id={course_id}")
    time.sleep(3)
    exec_js_in_mastery_tab(f'''
    const b = document.querySelector('button.mb2modalsection[data-counter="{fb_cnt}"]') || document.querySelector('button[data-counter="{fb_cnt}"]');
    if (b) b.click();
    ''')
    if wait_for_modal_ready():
        js_s4 = r'''
        const modal = document.querySelector('#mb2modalsection');
        const a = modal ? modal.querySelector('a[href*="/mod/feedback/"]') : null;
        return a ? a.href : null;
        '''
        feedback_link = exec_js_in_mastery_tab(js_s4)
        if feedback_link:
            m = re.search(r'id=(\d+)', feedback_link)
            if m:
                fb_cmid = m.group(1)
                print(f"Feedback cmid: {fb_cmid}")
                complete_current_feedback(course_id=course_id, feedback_cmid=fb_cmid)
                
    # 6. Final verification of course progress
    print("\n--- Verifying Course Progress ---")
    navigate_to(f"https://mastery-ku.com/course/view.php?id={course_id}")
    time.sleep(3)
    final_info = exec_js_in_mastery_tab(js_boxes)
    print(f"Final Progress: {final_info.get('progress')}")
    print(f"Boxes: {json.dumps(final_info.get('boxes'), indent=2, ensure_ascii=False)}")
    
    return '100%' in final_info.get('progress', '')

if __name__ == '__main__':
    cid = sys.argv[1] if len(sys.argv) > 1 else '2'
    success = complete_course(cid)
    print(f"\nCourse {cid} completion result: {'SUCCESS' if success else 'FAILED'}")
