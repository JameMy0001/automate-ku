---
name: automate-ku
description: Production-grade automated system for executing KU Mastery (mastery-ku.com) Moodle LMS coursework, interactive H5P modules, SCORM 1.2 pre/post-tests with 100% scores, and feedback surveys via headless SCORM runtime API and native AppleScript/CoreGraphics bridges. Includes single-course and batch multi-course orchestrators, defensive quarantine guards, and deep audit verification tools.
category: "04 - Web & Frontend"
tags:
  - agent-skill
  - moodle
  - scorm
  - lms-automation
  - ku-mastery
  - stage-4
---

# KU Mastery LMS Course Automation

Production-grade automation framework for KU Mastery (`mastery-ku.com`), automating Moodle LMS learning flows, H5P interactive lessons, SCORM 1.2 pre/post-tests with 100% precision, and multi-page feedback surveys.

---

## 1. Architecture and Core Mechanics

The system operates directly on the user's running Google Chrome browser without requiring remote debugging ports (`--remote-debugging-port`), browser profile resets, or credential exposure:

```
+-----------------------------------------------------------------------------------+
|                               Google Chrome Browser                               |
|                                                                                   |
|   +------------------------------------+    +---------------------------------+   |
|   |         mastery-ku.com             |    |     SCORM Player Runtime        |   |
|   |  - Moodle Course Outline View      |    |  - window.API (LMSSetValue)     |   |
|   |  - H5P Interactive Activities      |    |  - SCORM 1.2 Data Model         |   |
|   |  - Feedback Questionnaires         |    |  - Grade Commit & Finish        |   |
|   +-----------------+------------------+    +----------------+----------------+   |
+---------------------|----------------------------------------|--------------------+
                      ^                                        ^
                      |  AppleScript UTF-8 Base64 Bridge       |  Moodle window.API
                      |                                        |
+---------------------+----------------------------------------+--------------------+
|                             automate-ku Automation Engine                         |
|                                                                                   |
|   +----------------------+   +-----------------------+   +--------------------+   |
|   |   chrome_helper.py   |   |   complete_scorm.py   |   | complete_feedback  |   |
|   |   AppleScript Bridge |   |   SCORM 1.2 Injector  |   | Multi-page Form    |   |
|   +----------+-----------+   +-----------+-----------+   +---------+----------+   |
|              ^                           ^                         ^              |
|              |                           |                         |              |
|              +---------------------------+-------------------------+              |
|                                          |                                        |
|                          +---------------+---------------+                        |
|                          |    auto_complete_course.py    |                        |
|                          |    Single-Course Orchestrator |                        |
|                          +---------------+---------------+                        |
|                                          ^                                        |
|                                          |                                        |
|                          +---------------+---------------+                        |
|                          |      run_all_remaining.py     |                        |
|                          |      Batch Course Runner      |                        |
|                          +---------------+---------------+                        |
|                                          ^                                        |
|                                          |                                        |
|                          +---------------+---------------+                        |
|                          |      audit_all_courses.py     |                        |
|                          |      Deep Audit & Verification|                        |
|                          +-------------------------------+                        |
+-----------------------------------------------------------------------------------+
```

### 1.1 AppleScript UTF-8 Base64 Bridge (`scripts/chrome_helper.py`)
- Dispatches arbitrary JavaScript payloads directly into the active `mastery-ku.com` tab using base64 encoding with `TextDecoder`.
- Handles Thai text, JSON payloads, and dynamic DOM inspections without quote-escaping conflicts.
- Returns structured JSON responses containing execution status and stack traces.

### 1.2 Headless SCORM 1.2 Injector (`scripts/complete_scorm.py`)
- Hooks directly into Moodle's native SCORM runtime API (`window.API`).
- Injects standard CMI datamodel calls:
  - `cmi.core.lesson_status` -> `passed`
  - `cmi.core.score.raw` -> `100`
  - `cmi.core.score.min` -> `0`
  - `cmi.core.score.max` -> `100`
  - `cmi.core.session_time` -> `00:04:30`
- Calls `LMSCommit("")` and `LMSFinish("")` to ensure instantaneous grade synchronization with Moodle's Gradebook (Grade A / 100%).

### 1.3 Moodle Feedback Solver (`scripts/complete_feedback.py`)
- Automatically detects and populates multi-page survey forms (`mod/feedback/complete.php`).
- Selects top numeric satisfaction ratings (e.g. 5, มากที่สุด, เหมาะสมมาก) for radio buttons and `<select>` dropdowns.
- Fills required text inputs and textareas with standard constructive feedback.
- Handles pagination (`gonextpage`) and final form submission (`savevalues`).

### 1.4 Single & Batch Course Orchestrators (`scripts/auto_complete_course.py`, `scripts/run_all_remaining.py`)
- Dynamically discovers course sections (Lessons, Pre-test, Post-test, Feedback) via Section Counter introspection.
- Iteratively marks H5P lessons as complete.
- Contains an absolute programmatic quarantine guard blocking execution on manual workshop courses.

---

## 2. Zero-Defect Quality Gate and Safeguards

1. **Course 17 Quarantine Rule**:
   - Course 17 (`02 - Workshop & Certificate Information`) is reserved for hands-on student attendance.
   - Any attempt to run automation on Course 17 raises a fatal `ValueError` and halts execution immediately.
2. **100% Score Guarantee**:
   - All SCORM modules are committed with raw score 100 and status `passed`.
   - Verified via Moodle Gradebook aggregation.
3. **Double Verification**:
   - After completing each module, the orchestrator verifies the course outline DOM badge for `Your progress 100%`.
   - Incomplete modules trigger an automated retry pass.

---

## 3. Usage and Execution Protocols

### 3.1 Prerequisites
- macOS with Google Chrome installed and logged in to `https://mastery-ku.com`.
- Terminal accessibility permissions enabled for AppleScript control.
- Python 3.9+.

### 3.2 Single Course Execution
To execute complete automation on a specific course:
```bash
python3 scripts/auto_complete_course.py <course_id>
```
Example:
```bash
python3 scripts/auto_complete_course.py 2
```

### 3.3 Batch Multi-Course Execution
To execute all 14 theoretical and industrial courses sequentially:
```bash
python3 scripts/run_all_remaining.py
```
To specify a custom subset of courses:
```bash
python3 scripts/run_all_remaining.py 2 3 4 5
```

### 3.4 Deep Verification Audit
To run an independent item-level audit verifying all 28 SCORMs, H5Ps, and feedback surveys:
```bash
python3 scripts/audit_all_courses.py
```
Outputs audit results to `full_audit_results.json`.

---

## 4. Troubleshooting and Edge Cases

- **"No mastery-ku.com tab found in Google Chrome"**:
  - Open Google Chrome and navigate to `https://mastery-ku.com/my/`. Ensure the tab is not closed or suspended.
- **Moodle Session Concurrency**:
  - Do not interact with the same course in multiple tabs simultaneously to prevent Moodle SCORM datamodel lockouts.
- **Modal Preload Delays**:
  - The orchestrator includes a 12-second bounded wait loop (`wait_for_modal_ready()`) that automatically handles network latency when opening section dialogs.
