# Lab Step 1b-3 — Datasets Info Generation (Optional)

Read `references/lab_context.md` before starting.

This step is optional. Run it when the lab uses datasets with complex download procedures
or when students need reference information about the data.

---

## When This File Is Needed

Generate `datasets_info.md` when at least one of the following applies:
- Dataset requires non-trivial download (API keys, manual download, custom classes)
- Dataset has known pitfalls (non-standard splits, domain shift, label quirks)
- Different variants need different quality thresholds or parameters
- Dataset is large and the student needs to know expected load times

If datasets are simple and the loading code is self-evident from Block 0 — skip this step.

---

## Context to Read Before Generating

1. Read `labs/labN/lab_spec.md` — datasets section.
2. Read `labs/labN/starter/exercises.ipynb` — Block 0 (dataset list, sources, loading code).
3. Read `course_conventions.md` from the course root — course language.
4. Read `lab_templates.md` from the course root — section titles.

Note: if the previous step (`/lab spec N`) was long and context was heavy, run this as
a separate command in the same or a new session.

---

## Prompt to Execute

Generate `labs/labN/starter/datasets_info.md` — a reference file for students.
The file is written for the student, not for autotests. Language: course language (from `course_conventions.md`).

**File structure:**

1. Header and introductory paragraph: what datasets are used, how variants are assigned,
   whether there are common parameters for all datasets (normalization, image sizes, etc.)

2. A separate section for each dataset:
   - Name and task
   - Source with link
   - Classes / target variable
   - Size (train / val / test if applicable)
   - Quirks and pitfalls (⚠️ if any)
   - Ready-to-use loading code — working, verified, with comments
   - Access to labels (if non-trivial)
   - Quality thresholds or expected metrics (if applicable)

3. If all datasets share common transforms, normalization parameters, or utilities — put them
   in a separate section at the end; do not duplicate in each dataset section

4. Comparison table of all datasets at the end

5. Section with title per `lab_templates.md` ("Common Issues and Solutions" or course-language equivalent) — specific errors and how to fix them

**Requirements:**
- All numbers (dataset sizes, class counts, image dimensions) — verified only; use web search
  if unsure
- Loading code must be working and consistent with `exercises.ipynb`
- Links to sources — verified and working only
- Known-issue warnings: mark with ⚠️

---

## After Saving

Append to `labs/labN/history.md`:
```markdown
## [YYYY-MM-DD] Step 1b-3: Datasets info generated

**File:** labs/labN/starter/datasets_info.md
**Datasets covered:** <list>
**Notes:** <any non-obvious issues documented>
```

(No COURSE_STATE.md column for this step; it is noted implicitly when the starter/ contents are committed.)
