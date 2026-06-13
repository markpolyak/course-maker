# course-maker — Development Conventions

This file is loaded by Claude Code when working inside this repository.
It governs how to develop and maintain the skill, not how to use it.

## Skill language: English only

All text in `skill/SKILL.md` and `skill/references/*.md` must be in English:
instructions, comments, examples, template snippets, summary lines, error messages.

The skill itself is language-agnostic — courses can be generated in any language.
But the skill machinery (every word Claude reads as instructions) is always English.

**Common mistake:** when adding new rules or examples, writing them in Russian
because the course content is in Russian. Don't. Translate every addition to English
before saving, including inline examples of forbidden phrases.

## LMS specifics live in profiles, not in references

`skill/references/*.md` describes universal workflow. Anything specific to a
single LMS (GitHub Classroom + `gh api`, Moodle, Canvas, local zip, etc.) does
not belong here. Such workflows live in `skill/profiles/<name>/lms.md` and get
copied to the course root as `lms_adapter.md` during `lab course-init`. The
`lab publish` dispatcher reads `lms_adapter.md`, not any embedded LMS workflow.

**Common mistake:** when fixing or extending the publish flow for one LMS
(usually GitHub Classroom because that's the most-used profile), patching
`references/lab_publish.md` instead of the profile's `lms.md`. Don't. The
dispatcher must stay LMS-agnostic.

## Skill instruction files are read-only at runtime

The skill never writes to `skill/SKILL.md`, `skill/references/*.md`,
`skill/templates/*`, or `skill/profiles/*` during command execution.
Those files are loaded as instructions. State and per-course artifacts go
into the user's course repo (`COURSE_STATE.md`, `history.md`, `lectures/`,
`labs/`, `lms_adapter.md`, etc.).

If you need to evolve the skill itself, that's a separate task — open the
repo and edit; do not bake "the skill should learn over time and rewrite
itself" into the workflow.
