# /course-maker lab update N

Use when a lab needs to be updated AFTER publishing.

1. Make the needed changes in `<LAB_DIR>starter/`.
2. Run `/course-maker lab validate N <student_id>` to verify the fix.
3. Run `/course-maker lab publish N` to sync to the LMS (see `lms_adapter.md`).
4. Append a post-publish-update entry to `<LAB_DIR>history.md`.
5. `COURSE_STATE.md`: set `validated → 🔄` if re-validation is needed.
