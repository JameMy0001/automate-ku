#!/usr/bin/env python3
"""
Run All Remaining Courses - Batch Multi-Course Automation Orchestrator
Iterates sequentially through all 14 theoretical/industrial courses on KU Mastery,
executing complete_course() for each, while enforcing a strict quarantine exclusion of Course 17.
"""

import sys
import time
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from auto_complete_course import complete_course
from chrome_helper import navigate_to, exec_js_in_mastery_tab

# All 14 theoretical and industrial courses
ALL_THEORETICAL_COURSES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

def get_dashboard_summary():
    """Fetch all courses and completion percentages from my/courses.php."""
    navigate_to('https://mastery-ku.com/my/courses.php')
    for _ in range(20):
        time.sleep(1)
        has_real_cards = exec_js_in_mastery_tab('return document.querySelectorAll(".dashboard-card a.coursename, .dashboard-card a[href*=\\"/course/view.php?id=\\"]").length;')
        if has_real_cards and has_real_cards > 0:
            break
            
    js = r'''
    const map = {};
    document.querySelectorAll('.dashboard-card').forEach(card => {
        const a = card.querySelector('a.coursename') || card.querySelector('a[href*="/course/view.php?id="]');
        if (!a) return;
        const match = a.href.match(/id=(\d+)/);
        if (!match) return;
        const id = match[1];
        const text = card.innerText;
        let progress = 'unknown';
        const pMatch = text.match(/(\d+)% complete/);
        if (pMatch) progress = pMatch[1] + '%';
        const title = card.querySelector('.coursename')?.innerText || a.innerText;
        map[id] = { id: parseInt(id), title: title.replace(/\s+/g, ' ').trim(), progress };
    });
    const list = Object.values(map);
    list.sort((a, b) => a.id - b.id);
    return list;
    '''
    return exec_js_in_mastery_tab(js)

def main():
    if len(sys.argv) > 1:
        target_courses = [int(x) for x in sys.argv[1:] if int(x) != 17]
    else:
        target_courses = ALL_THEORETICAL_COURSES
        
    # Strictly enforce exclusion of Course 17
    target_courses = [cid for cid in target_courses if cid != 17]
    
    print("==================================================")
    print("STARTING PROCESSING OF ALL THEORETICAL COURSES")
    print(f"Target Course IDs ({len(target_courses)} courses): {target_courses}")
    print("SKIPPING Course 17 completely as instructed.")
    print("==================================================")
    
    results = {}
    
    for cid in target_courses:
        print(f"\n>>>>>>>>>> PROCESSING COURSE {cid} <<<<<<<<<<")
        success = complete_course(cid)
        if not success:
            print(f"[RETRY] Course {cid} did not reach 100%, retrying one more time...")
            time.sleep(3)
            success = complete_course(cid)
        results[cid] = success
        print(f">>>>>>>>>> COURSE {cid} RESULT: {'SUCCESS' if success else 'FAILED'} <<<<<<<<<<\n")
        time.sleep(2)
        
    print("\n==================================================")
    print("ALL REMAINING COURSES PROCESSED!")
    print("Summary of execution results:")
    for cid, ok in results.items():
        print(f"Course {cid}: {'SUCCESS (100%)' if ok else 'FAILED'}")
    print("==================================================")
    
    print("\nFetching final Dashboard status...")
    summary = get_dashboard_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
