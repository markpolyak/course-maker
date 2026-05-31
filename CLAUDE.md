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
