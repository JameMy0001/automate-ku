#!/usr/bin/env python3
"""
Complete Feedback - Automated Moodle Feedback Questionnaire Solver
Fills all feedback items with high ratings, handles multi-page questionnaires,
select dropdowns, checkboxes, text fields, and submits the feedback form.
"""

import sys
import time
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from chrome_helper import exec_js_in_mastery_tab, get_current_url, navigate_to

def complete_current_feedback(course_id=None, feedback_cmid=None):
    """
    Automate post-course feedback submission:
    1. Navigate to feedback complete form if cmid provided.
    2. Fill text inputs, textareas with positive feedback.
    3. Select highest numeric ratings for radio buttons and select dropdowns.
    4. Check required checkboxes.
    5. Click next page or final submit button until finished.
    """
    if feedback_cmid:
        url = f"https://mastery-ku.com/mod/feedback/complete.php?id={feedback_cmid}"
        if course_id:
            url += f"&courseid={course_id}"
        print(f"Navigating to feedback: {url}")
        navigate_to(url)
        time.sleep(3)
        
    for step in range(25):  # safety limit
        curr_url = get_current_url()
        print(f"[Feedback Step {step+1}] URL: {curr_url}")
        
        # Check if already completed
        check_js = r'''
        const text = document.querySelector('#region-main')?.innerText || document.body.innerText;
        const isDone = text.includes('บันทึกคำตอบของท่านเรียบร้อยแล้ว') || 
                       text.includes('Done: Submit feedback') ||
                       text.includes('ส่งคำตอบแล้ว') || 
                       text.includes('ขอบคุณสำหรับ') || 
                       text.includes('ข้อเสนอแนะของท่านได้รับการบันทึกแล้ว') || 
                       text.includes('ท่านส่งแบบสอบถามไปเรียบร้อยแล้ว') ||
                       text.includes('Your response has been submitted');
        return { isDone, textSnippet: text.slice(0, 300) };
        '''
        st = exec_js_in_mastery_tab(check_js)
        if st.get('isDone'):
            print("Feedback completed successfully!")
            return True
            
        # Fill form elements on the current page
        fill_js = r'''
        const form = document.querySelector('#region-main form');
        if (!form) return { status: 'no_form' };
        
        // 1. Text inputs
        form.querySelectorAll('input[type="text"]').forEach(inp => {
            if (!inp.value) {
                const label = (inp.labels && inp.labels[0]?.innerText) || inp.placeholder || '';
                if (label.includes('บริษัท') || label.includes('มหาวิทยาลัย')) {
                    inp.value = 'มหาวิทยาลัยเกษตรศาสตร์';
                } else {
                    inp.value = 'ดีมาก ชัดเจน';
                }
            }
        });
        
        // 2. Textareas
        form.querySelectorAll('textarea').forEach(ta => {
            if (!ta.value) {
                ta.value = 'เนื้อหาดีมากและมีประโยชน์มากครับ';
            }
        });

        // 2.1 Select dropdowns
        form.querySelectorAll('select').forEach(sel => {
            if (!sel.value && sel.options.length > 1) {
                sel.selectedIndex = sel.options.length - 1;
                sel.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });

        // 2.2 Checkboxes
        form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            if (!cb.checked) {
                cb.checked = true;
                cb.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
        
        // 3. Radio buttons: group by name, choose highest numeric value
        const radioGroups = {};
        form.querySelectorAll('input[type="radio"]').forEach(r => {
            if (!radioGroups[r.name]) radioGroups[r.name] = [];
            radioGroups[r.name].push(r);
        });
        
        for (const name in radioGroups) {
            const radios = radioGroups[name];
            radios.sort((a, b) => (parseInt(b.value) || 0) - (parseInt(a.value) || 0));
            radios[0].checked = true;
        }
        
        // Find next or submit button
        const saveBtn = form.querySelector('input[name="savevalues"], button[name="savevalues"], input[type="submit"][value*="ส่ง"], input[type="submit"][value*="Submit"], input[type="submit"][value*="บันทึก"]');
        if (saveBtn) {
            saveBtn.click();
            return { status: 'submitted_savevalues' };
        }
        
        const nextBtn = form.querySelector('input[name="gonextpage"], button[name="gonextpage"], input[type="submit"][value*="Next"]');
        if (nextBtn) {
            nextBtn.click();
            return { status: 'clicked_next' };
        }
        
        return { status: 'no_buttons' };
        '''
        res = exec_js_in_mastery_tab(fill_js)
        print("Form action status:", res)
        time.sleep(3)
        
    return False

if __name__ == '__main__':
    cid = sys.argv[1] if len(sys.argv) > 1 else None
    cmid = sys.argv[2] if len(sys.argv) > 2 else None
    complete_current_feedback(course_id=cid, feedback_cmid=cmid)
