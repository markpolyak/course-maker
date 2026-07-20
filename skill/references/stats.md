# /course-maker stats

Show course progress as completion bars across pipelines. Read-only.

## Inputs

1. `course_plan.md` — planned totals:
   - `## Overview` line (`**Lectures:** N  **Labs:** N` …), or count rows in the
     `## Sessions` table by `Type` if the Overview counts are missing/TODO.
   - `## Lectures` subsections — `**Estimated time:** N min` per lecture, for the
     hours figure. If estimated times are absent, omit the hours line entirely.
2. `COURSE_STATE.md` — completion status:
   - A **lecture is complete** when all of `plan`, `visuals`, `figures`,
     `slides`, `notes` are `✅`.
   - A **lab is complete** when `tests`, `validated`, and `published` are `✅`.
   - A **quiz is complete** when `plan`, `questions`, and `published` are `✅`.
   - A **homework is complete** when `task`, `rubric`, and `published` are `✅`.
   - Count `🔄`/`⚠️`/partially-✅ rows as in-progress, not complete.

## Output

One bar per pipeline that has at least one planned item, then totals. Use a
10-cell bar (`█` filled, `░` empty), rounding to the nearest cell:

```
Course progress — {course name}

Lectures  ████████░░  8/12 complete   (66%)
Labs      ██████░░░░  2/3  complete   (66%)
Hours covered: 12 / 18 lectures planned → 720 / 1080 min

In progress: lectures 09 (slides), 10 (figures); lab 3 (validated)
```

Rules:
- Show the "Hours" line only if `## Lectures` subsections carry estimated times.
  "Covered" = sum of estimated time over complete lectures; "planned" = sum over
  all planned lectures.
- The "In progress" line lists items with mixed statuses and names the first
  not-yet-✅ step for each. Omit the line if nothing is in progress.
- Do not modify any file. If `course_plan.md` totals and `COURSE_STATE.md` rows
  disagree (e.g. plan says 12 lectures but state lists 10), note the discrepancy
  and suggest `/course-maker doctor`.
