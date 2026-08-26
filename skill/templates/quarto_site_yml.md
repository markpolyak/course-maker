# Course site project file

Copied to `site/_quarto.yml` by `/course-maker site init`. Fill the placeholders
from `AGENTS.md` and `course_plan.md`.

**This file belongs in `site/`, never in the course root.** A `_quarto.yml` at
the root turns the whole course into a Quarto project, and rendering a single
deck then writes its output into the project's `output-dir` instead of next to
the source — which breaks `/course-maker slides N export`.

```yaml
project:
  type: website
  output-dir: _site
  resources:
    - decks/**
    # ^ decks are staged here already rendered, as static files. They are not
    #   re-executed by the site build.

website:
  title: "[Course name]"
  description: "[One line from course_plan.md]"
  navbar:
    left:
      - href: index.qmd
        text: Home
      - href: syllabus.qmd
        text: Syllabus
      - href: lectures.qmd
        text: Lectures
      - href: labs.qmd
        text: Labs
      - href: homework.qmd
        text: Homework
  page-footer: "[Institution] · [Course name]"

format:
  html:
    theme: cosmo
    toc: true

execute:
  freeze: auto
  # The site's own pages carry no heavy computation, but freeze keeps a project
  # render from re-running anything that is added later.
```

Drop navbar entries the course does not have — a `Labs` tab leading to an empty
page is worse than no tab.

## .gitignore

`site init` appends these; the staged copies and the built site are generated
artifacts, and the sources they come from are already in the repository:

```
site/_site/
site/.quarto/
site/decks/
site/_freeze/
```
