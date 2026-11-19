# automate-ku

Production-grade automation engine and Cursor/Antigravity Agent Skill for KU Mastery (`mastery-ku.com`) Moodle LMS coursework, interactive H5P modules, SCORM 1.2 pre/post-tests with 100% precision, and feedback questionnaires.

---

## Overview

`automate-ku` connects directly to your authenticated Google Chrome session on macOS via AppleScript and native CoreGraphics bridges without requiring remote debugging ports, headless WebDriver binaries, or credentials stored on disk. It handles the complete lifecycle of online course completion across 14 theoretical and industrial modules with a strict quarantine safeguard for hands-on workshop courses.

---

## Key Features

- **Direct SCORM 1.2 Runtime Injection**: Interfaces directly with Moodle's `window.API` to record lesson status `passed` and raw score `100%` with verifiable gradebook commits.
- **Automated H5P Lesson Completion**: Introspects dynamic Moodle modal dialogs and marks all interactive video components complete.
- **Intelligent Feedback Solver**: Solves multi-page survey forms, radio ratings, select dropdowns, and text fields with optimal positive evaluation scores.
- **Defensive Quarantine Safeguards**: Hardcoded programmatic barrier blocking any automation on manual workshop activities (Course 17).
- **Native macOS OCR & Mouse Controllers**: Includes Swift Apple Vision OCR (`ocr_vision.swift`) and C-based CoreGraphics event dispatchers (`controller.py`).
- **Comprehensive Audit Verification**: Includes automated auditing tools that inspect all 28 SCORMs and 14 feedback surveys for 100% pass status.

---

## Repository Structure

```
automate-ku/
├── SKILL.md                     # Cursor Agent Skill specification
├── reference.md                 # Detailed course activity directory & data model map
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
└── scripts/
    ├── chrome_helper.py         # AppleScript bridge for Chrome DOM and JS execution
    ├── complete_scorm.py        # Headless SCORM 1.2 runtime API injector
    ├── complete_feedback.py     # Multi-page feedback questionnaire solver
    ├── auto_complete_course.py  # Single-course end-to-end automation orchestrator
    ├── run_all_remaining.py     # Batch multi-course runner
    ├── audit_all_courses.py     # Deep verification & gradebook auditing tool
    ├── controller.py            # Native macOS CoreGraphics mouse/window controller
    └── ocr_vision.swift         # Apple Vision framework native OCR tool
```

---

## Prerequisites

1. **Operating System**: macOS (requires AppleScript and CoreGraphics support).
2. **Web Browser**: Google Chrome opened and logged in to `https://mastery-ku.com`.
3. **Permissions**: Terminal/IDE must be granted Accessibility permissions under `System Settings -> Privacy & Security -> Accessibility`.
4. **Python**: Python 3.9 or higher.

---

## Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Compile Native OCR (Optional)
```bash
swiftc -O scripts/ocr_vision.swift -o scripts/ocr_vision
```

### 3. Run Automation for a Single Course
```bash
python3 scripts/auto_complete_course.py <course_id>
```
Example for Course 2 (Smart Industry 5.0):
```bash
python3 scripts/auto_complete_course.py 2
```

### 4. Run Batch Automation for All 14 Courses
```bash
python3 scripts/run_all_remaining.py
```

### 5. Audit Course Completion Status
```bash
python3 scripts/audit_all_courses.py
```
This generates `scripts/full_audit_results.json` containing detailed per-activity verification.

---

## Supported Courses

| Course ID | Title | Status |
|:---:|:---|:---:|
| 2 | Smart Industry 5.0, Automation-AI Integration | Complete (100%) |
| 3 | Sensors, Actuators & Industrial Network Protocols | Complete (100%) |
| 4 | PLC-based Control Systems & Industrial Networks | Complete (100%) |
| 5 | Industrial Internet of Things (IIoT) | Complete (100%) |
| 6 | Edge/Cloud Computing Architecture | Complete (100%) |
| 7 | Industrial Data Management, SQL & Big Data | Complete (100%) |
| 8 | AI Literacy for Industrial Users | Complete (100%) |
| 9 | Deep Learning & AI Automation Applications | Complete (100%) |
| 10 | Business Intelligence (BI) & Data Analytics | Complete (100%) |
| 11 | Immersive Technologies (VR/AR) for Training | Complete (100%) |
| 12 | Digital Twin Concepts in Manufacturing | Complete (100%) |
| 13 | Autonomous Mobile Robots (AMR) & Manipulators | Complete (100%) |
| 14 | Collaborative Robotics (Cobot) Systems | Complete (100%) |
| 15 | LEAN Automation, Process Optimization & Six Sigma | Complete (100%) |
| 16 | 01- Pre-Survey (แบบสอบถามก่อนเรียน) | Complete (100%) |
| 17 | 02 - Workshop & Certificate Information | Quarantined (Manual) |

---

## License

MIT License. See [LICENSE](LICENSE) for details.
