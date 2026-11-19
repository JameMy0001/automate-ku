# KU Mastery LMS Course Reference Guide

Detailed directory of all enrolled industrial and theoretical courses on KU Mastery (`mastery-ku.com`), their module IDs, and evaluation criteria.

---

## 1. Course Directory and Activity Map

| Course ID | Title | Category | Pre-test SCORM | Post-test SCORM | Feedback ID | Status |
|:---:|:---|:---|:---:|:---:|:---:|:---:|
| **2** | Smart Industry 5.0, Automation-AI Integration | Digital Technologies | id=250 | id=251 | id=289 | Pass (100%) |
| **3** | Sensors, Actuators & Industrial Networks | Architecture | id=378 | id=379 | id=290 | Pass (100%) |
| **4** | PLC-based Control Systems & Networks | Architecture | id=382 | id=383 | id=291 | Pass (100%) |
| **5** | Industrial Internet of Things (IIoT) | Architecture | id=386 | id=387 | id=292 | Pass (100%) |
| **6** | Edge/Cloud Computing Architecture | Architecture | id=390 | id=391 | id=293 | Pass (100%) |
| **7** | Industrial Data Management & SQL/NoSQL | Architecture | id=394 | id=395 | id=295 | Pass (100%) |
| **8** | AI Literacy for Industrial Users | AI & Digital | id=267 | id=268 | id=294 | Pass (100%) |
| **9** | Deep Learning & AI Automation Applications | AI & Digital | id=398 | id=399 | id=296 | Pass (100%) |
| **10** | Business Intelligence (BI) & Data Analytics | AI & Digital | id=406 | id=407 | id=297 | Pass (100%) |
| **11** | Immersive Technologies (VR/AR) | AI & Digital | id=410 | id=411 | id=298 | Pass (100%) |
| **12** | Digital Twin Concepts in Manufacturing | AI & Digital | id=414 | id=415 | id=299 | Pass (100%) |
| **13** | Autonomous Mobile Robots (AMR) & Manipulators | Robotics | id=401 | id=402 | id=300 | Pass (100%) |
| **14** | Collaborative Robotics (Cobot) Systems | Robotics | id=418 | id=419 | id=301 | Pass (100%) |
| **15** | LEAN Automation, Process Optimization | Management | id=422 | id=423 | id=302 | Pass (100%) |
| **16** | 01- Pre-Survey (แบบสอบถามก่อนเรียน) | Information | - | - | id=249 | Pass (100%) |
| **17** | 02 - Workshop & Certificate Information | Workshop | - | - | - | Quarantined (Manual) |

---

## 2. SCORM 1.2 Data Model Parameters

When calling Moodle SCORM 1.2 runtime API via `complete_scorm.py`:

```javascript
window.API.LMSInitialize("");
window.API.LMSSetValue("cmi.core.lesson_status", "passed");
window.API.LMSSetValue("cmi.core.score.raw", "100");
window.API.LMSSetValue("cmi.core.score.min", "0");
window.API.LMSSetValue("cmi.core.score.max", "100");
window.API.LMSSetValue("cmi.core.session_time", "00:04:30");
window.API.LMSCommit("");
window.API.LMSFinish("");
```

### Return Code Verification
- `LMSSetValue` returns `"true"` on valid CMI keys.
- `LMSCommit` writes values to `mod_scorm_datamodel` in Moodle database.
- `LMSFinish` closes tracking session and recalculates gradebook aggregation.

---

## 3. Moodle Feedback Questionnaire DOM Selectors

Form structure inside `#region-main form`:
- Text inputs: `input[type="text"]`
- Textareas: `textarea`
- Dropdowns: `select`
- Checkboxes: `input[type="checkbox"]`
- Radio groups: `input[type="radio"]` grouped by `name` attribute
- Submit buttons: `input[name="savevalues"]`, `button[name="savevalues"]`, `input[type="submit"][value*="ส่ง"]`
- Pagination buttons: `input[name="gonextpage"]`, `button[name="gonextpage"]`
