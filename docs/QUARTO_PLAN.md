# Поддержка Quarto в course-maker — план реализации

**Дата:** 2026-08-24
**Статус:** план согласован, реализация не начата.
**Предусловие:** `quarto` не установлен на машине разработчика (`quarto not found`;
`pandoc 3.10` и `node v22` есть). Перед этапом 1 — `brew install quarto`.

Документ самодостаточен: после очистки контекста достаточно прочитать его и
названные в нём файлы, чтобы продолжить работу с любого шага.

---

## 1. Цель

Добавить Quarto как **третий равноправный формат слайдов** (наряду с `beamer` и
`slidev`), как **опциональный бэкенд экспорта документов** (PDF без LaTeX через
Typst) и как **генератор сайта курса** (GitHub Pages).

Мотивация заказчика (курс «Прикладное глубокое обучение»), в порядке важности:
PDF без LaTeX → HTML-презентации (reveal.js) → сайт курса → pptx как побочная
выгода.

**Почему Quarto, а не расширение Slidev:** один источник → reveal.js + beamer-PDF
+ pptx через `--to`; нет зависимости от Node; исполняемые code-chunks прямо в
слайдах, в том числе интерактивные; академический аппарат (формулы, `[@ref]`,
bibliography, перекрёстные ссылки); тот же тулчейн собирает сайт курса. За Slidev
остаётся презентационная механика (Monaco-редактор в слайде, click-анимации,
Vue-компоненты), поэтому **Slidev не удаляется**.

---

## 2. Базовая линия (что есть в репозитории на 2026-08-24)

Проверено чтением файлов; при возобновлении работы перепроверить `git log`.

- **Форматы слайдов — два.** Резолв в `skill/SKILL.md` (§ `/course-maker slides
  N [format]`): явный аргумент → поле `Slides format:` в `AGENTS.md` → дефолт
  `beamer`. При `slides N next` поле игнорируется, формат определяется по
  существующему файлу: `slides.tex` → beamer, `slides.md` → slidev.
- **Reference-файлы шага 4:** `skill/references/step4_slides.md` (beamer, 179
  строк), `skill/references/step4_slides_slidev.md` (slidev, 150 строк).
- **Шаблоны преамбулы:** `skill/templates/slides_preamble_pdflatex.tex`,
  `slides_preamble_xelatex.tex`, `slides_headmatter_slidev.md`. Копируются в
  корень курса на `course init` как `slides_preamble.tex` / `slides_headmatter.md`.
- **Шаги 2–3 (визуализации и фигуры):** `references/step2_visuals.md` (51 строка),
  `references/step3_figures.md` (119 строк). Модель жёсткая: `figures.py` → PNG,
  без вариантов.
- **Шаг 5 (заметки):** `references/step5_notes.md` (195 строк) — `speaker_notes.md`,
  режимы `minimal/medium/detailed`, чанки по 5 слайдов, таблица таймингов,
  кандидаты на выброс, объём считается от `Speech rate:`.
- **Экспорт:** `references/slides_export.md` (57 строк) — детект формата по
  файлу, ветки beamer (`latexmk`) и slidev (`npx slidev export`).
- **`pptx` объявлен нереализованным** в `SKILL.md` и в
  `docs/IMPROVEMENT_PLAN.md` (волна 7.1).
- **Экспорт документов — pandoc.** Команды продублированы в
  `references/syllabus.md` (строки ~51–62) и `references/homework.md`
  (строки ~170–181): `pdf` / `latex` / `docx`. `references/quiz_publish.md`
  умеет только `markdown`.
- **Сайта курса нет** — команды `site` не существует.
- **Скрипты:** `skill/scripts/validate_state.py` сверяет `COURSE_STATE.md` с
  диском (в частности `figures ✅` ⇒ PNG на диске), `skill/scripts/lint_plan.py`
  проверяет самосогласованность `course_plan.md`.
- **Тесты:** `tests/static/test_structure.py` требует, чтобы каждый новый
  `references/*.md` был назван в `SKILL.md` (иначе orphan) и чтобы все
  упомянутые в `SKILL.md` reference-файлы существовали.
  `tests/static/test_english_only.py` запрещает не-латиницу в `skill/`.
  `tests/unit/test_validate_state.py` покрывает скрипт.
  `tests/e2e/test_slides_smoke.py` — beamer-смоук.

**Конвенции репозитория** (`CLAUDE.md` в корне, соблюдать строго):
1. Всё в `skill/SKILL.md`, `skill/references/`, `skill/templates/`,
   `skill/profiles/` — **только по-английски**, включая примеры и комментарии.
   `docs/` (в том числе этот файл) — по-русски.
2. Специфика конкретной LMS живёт в `skill/profiles/<name>/lms.md`, а не в
   `references/`.
3. Скил не пишет в свои же инструкционные файлы во время выполнения команд.

---

## 3. Проверенные факты о Quarto

Проверено по официальной документации 2026-08-24 (не по блогам). Источники — в
§ 10. Неподтверждённое явно помечено как «проверить при реализации».

### Слайды

| Факт | Следствие |
|---|---|
| Слайд — это заголовок `##`; `#` даёт слайд-разделитель секции; `---` создаёт слайд **без заголовка** | Чанкинг: чанк = 5 блоков `##`. Привычка ставить `---` между слайдами даст молчаливо сломанный дек |
| Титульный слайд генерируется автоматически из YAML `title` / `subtitle` / `author` / `institute`; без них титульного слайда нет | Чанк 0 = headmatter + слайд «План»; `##` для титульного не пишется |
| Две колонки: `:::: {.columns}` + вложенные `::: {.column width="40%"}` | Синтаксис Slidev (`layout: two-cols`, `::right::`) не применим |
| Заметки докладчика: `::: {.notes}` — работает в revealjs (presenter mode по клавише S) и pptx (панель заметок) | Основание для D6 |
| **Проверено рендером 2026-08-25 (quarto 1.10.18):** `::: {.notes}` → `\note{...}` и в beamer. Шаблон Quarto **уже подключает `pgfpages`**, поэтому для показа достаточно добавить через `include-in-header` одну строку `\setbeameroption{show notes on second screen=right}` | Инъекция заметок (D6) валидна для всех трёх таргетов; в шаблоне headmatter — закомментированная опция без лишнего `\usepackage` |
| Опции revealjs (подтверждены справочником формата): `theme`, `css`, `logo`, `footer`, `syntax-highlighting`, `embed-resources`, `slide-number`, `slide-level`; из руководства — `incremental`, пауза `. . .` | В шаблон headmatter кладём **только** подтверждённые опции |
| Опции beamer: `theme`, `colortheme`, `fonttheme`, `innertheme`, `outertheme`, `aspectratio`, `navigation`, `logo`, `titlegraphic`, `section-titles`, `themeoptions` | То же |
| pptx: 7 предопределённых layout'ов (Title Slide, Title and Content, Section Header, Two Content, Comparison, Content with Caption, Blank), кастомизация только через `reference-doc` | Контроль вёрстки ограничен — честно написать в reference |
| Мультиформат: `format:` с несколькими ключами; `quarto render doc.qmd --to <fmt>` рендерит один | Экспорт **всегда** с явным `--to` |
| beamer-таргет требует LaTeX, но Quarto ставит свой TinyTeX: `quarto install tinytex`; `pdf-engine: xelatex` задаётся в YAML; Quarto сам гоняет движок нужное число раз и доставляет недостающие пакеты | Текст ошибки в `slides_export.md`; `xelatex` в шаблоне |

### Исполняемый код

| Факт | Следствие |
|---|---|
| `execute: error` по умолчанию **`false`** — упавший чанк валит рендер, а не выдаёт пустую картинку. **Проверено 2026-08-25:** `quarto render` даёт `exit 1`, печатает traceback и **не создаёт выходной файл** | Это и есть проверка исполнением, основание для D5 |
| **Проверено 2026-08-25:** inline-чанк с matplotlib даёт PNG в `<deck>_files/figure-<format>/`, ссылка подставляется автоматически; Jupyter-ядро `python3` стартует само | Отдельный `figures.py` для quarto действительно не нужен |
| Опции исполнения: `eval`, `echo`, `output`, `warning`, `error`, `include`; глобально в `execute:`, на чанк — комментариями `#| key: value` в первых строках блока | Синтаксис для reference шага 4 |
| `execute: cache: true` — кэш на документ (jupyter-cache), сброс флагом `--cache-refresh` | Для дорогих чанков (график из обученной модели) |
| `execute: freeze: auto` — уровень **проекта**, результаты в `_freeze/`, коммитятся в git; при рендере одиночного документа игнорируется | Понадобится на этапе 3 (сайт), не на этапе 1 |
| Условный контент: `::: {.content-visible when-format="html"}` / `.content-hidden`, атрибуты `when-format` / `unless-format`; работает на div'ах, span'ах и **на code-блоках** (`` ```{.python .content-visible when-format="html"} ``) | Механизм «интерактив для HTML, статика для PDF» |
| Алиасы форматов: `html` покрывает `html*`, **`revealjs`**, `dashboard`, `email`; `pdf` / `latex` / `beamer` считаются одним | В условных блоках писать `html` и `pdf`, а не `revealjs`/`beamer` |
| `.content-visible` / `.content-hidden` скрывают **вывод, но не отменяют выполнение** кода | Статический fallback стоит времени рендера — сказать об этом честно |

### Документы и публикация

| Факт | Следствие |
|---|---|
| `format: typst` — Typst CLI **встроен в Quarto**, отдельная установка не нужна, LaTeX не нужен | «PDF без LaTeX» для этапа 2 |
| У Typst известное ограничение: размеры картинок по умолчанию отличаются от других форматов, рекомендуется задавать ширину явно | Правило «всегда явная ширина у картинки» |
| GitHub Pages — три пути: `output-dir: docs` + `.nojekyll`; `quarto publish gh-pages`; GitHub Action (`quarto-dev/quarto-actions/publish@v2`) | Выбор при инициализации сайта, этап 3 |

---

## 4. Решения

| # | Решение | Обоснование |
|---|---|---|
| **D1** | Quarto — третий равноправный формат. `beamer` и `slidev` не трогаем | Существующие курсы не ломаются |
| **D2** | Файл дека — `lectures/NN/slides.qmd`. Резолв при `next` по расширению: `.tex`/`.md`/`.qmd` | Коллизий нет, механизм детекта не меняется |
| **D3** | Headmatter курса — `slides_headmatter.qmd` в корне (шаблон `templates/slides_headmatter_quarto.qmd`). Все три таргета объявлены в нём | Симметрично slidev; тема курса правится в одном месте |
| **D4** | Экспорт всегда с явным `--to`. Аргументы команды: `pdf` (→ beamer, дефолт), `html` (→ revealjs), `pptx`. `png` не поддержан — сказать прямо | Голый `quarto render` собрал бы все три таргета. Дефолт `pdf` совпадает с beamer/slidev |
| **D5** | **Инвариант шага фигур переформулируется:** «каждая визуализация проверена исполнением, а не заявлена». Два режима: `script` (`figures.py` → PNG; для beamer/slidev **обязателен**, правило не меняется ни на слово) и `inline` (только quarto: `{python}`-чанк в деке, проверяется чистым `quarto render`). Для quarto `figures.py` — вторичен и опционален | См. § 5 |
| **D6** | Заметки авторствуются в `speaker_notes.md` (шаг 5 без изменений) и **механически инжектятся** в `slides.qmd` как `::: {.notes}` в конце шага 5; повторно — `/course-maker notes N inject` | См. § 6 |
| **D7** | Разделитель слайда — `##`. Перед каждым — маркер `<!-- Slide NN -->` | Нужен для `slides N next` (в beamer это `% Slide NN`) и для инъекции заметок |
| **D8** | Сырой LaTeX и TikZ в quarto-деке запрещены **в общем контенте**; допустимы только внутри `::: {.content-visible when-format="pdf"}` и обязательно со статическим fallback для `html` | Один источник рендерится в HTML и pptx, где LaTeX-врезки не работают |
| **D9** | Бэкенд экспорта документов — поле `Doc export: pandoc\|quarto` в `AGENTS.md`, дефолт `pandoc`. Отсутствие выбранного инструмента — явная ошибка, без молчаливого переключения | Не ломает существующие курсы; молчаливый фолбэк противоречит стилю скила («не падать молча» = сказать, а не подменить) |
| **D10** | Команды pandoc сводятся в новый общий `references/doc_export.md`; `syllabus.md`, `homework.md`, `quiz_publish.md` ссылаются на него | Сейчас блок продублирован в двух файлах; третий потребитель делает дублирование неприемлемым |
| **D11** | Сайт — команда `/course-maker site`, без строки в `COURSE_STATE.md` | Как `syllabus`: производный артефакт, не этап пайплайна |
| **D12** | GitHub Pages описывается в универсальном `references/site.md`, а не в профиле | Статический сайт ортогонален LMS; правило «специфика LMS → profiles» сюда не распространяется |

### Не-цели (обсуждено и отклонено)

- `.qmd` вместо `.ipynb` в лабах и семинарах. Пайплайн завязан на `.ipynb`
  (Block 0, `nbconvert` → `pytest`, изоляция `lab validate`, автогрейдинг);
  промежуточный формат добавляет риск без выигрыша.
- Удаление Slidev или pandoc.
- Рендер `.ipynb` лаб в HTML/PDF-раздатку — не отклонено, но вне этой работы.

---

## 5. Обоснование D5 — визуализации

Инвариант скила — не «PNG обязан существовать», а **«каждая визуализация
проверена исполнением, а не заявлена»**. У него два способа исполнения:

| Режим | Где | Чем проверяется |
|---|---|---|
| `script` | beamer, slidev — обязателен; quarto — допустим | `figures.py` отработал начисто, PNG на диске (существующее правило) |
| `inline` | только quarto | чистый `quarto render`: `error: false` по умолчанию валит рендер на исключении |

Inline-проверка **строже** проверки существования PNG: она проверяет код фигуры
в том контексте, где он используется. Отсюда — `figures.py` для quarto-курса
вторичен и опционален.

**Следствия по пайплайну:**

1. Шаг 2 (`visuals.md`) остаётся — решать *что* показывать не то же, что *как*.
   У каждой визуализации появляется поле `render: inline | png`.
2. Шаг 3 (`figures`) для quarto — условный. Все визуализации `inline` → шаг
   пропускается, в `COURSE_STATE.md` он `n/a` (новое значение статуса), а не ❌.
   Есть `png` → шаг работает как сейчас, для них.
3. Шаг 4 пишет чанки с кодом. После последнего чанка — один `quarto render`,
   чинить до чистого прогона. Это замена проверке «PNG на месте».
4. Интерактив (plotly / altair / bokeh) живёт только в HTML. Штатный ответ —
   `.content-visible when-format=`: интерактивная версия для `html`, статическая
   для `pdf`, из одного источника. Обе ветки выполняются — fallback стоит
   времени рендера.
5. Для inline-лекции порядок становится `plan → visuals → slides`; шаг figures
   необязателен.

**Отклонённая альтернатива:** оставить `figures.py` обязательным и для quarto.
Отклонено — это выбрасывает главное преимущество формата (динамические
визуализации, код рядом с содержанием) ради единообразия с LaTeX-веткой, где
`figures.py` обязателен по необходимости, а не по замыслу.

**Главный риск всей работы — правка Inviolable rules в `SKILL.md`.** Это
единственная правка, способная испортить уже работающие курсы: блок читается при
каждой команде и при каждом формате, и он существует именно как страховка на
случай, что reference не прочитан. Конкретный сценарий отказа: обобщённая
формулировка вида «убедись, что визуализация отрисовалась» позволяет агенту на
beamer-курсе рассудить «дек скомпилировался — значит с картинками порядок», а
компилируется он и со **старыми** PNG от прошлого прогона; лекция уезжает с
устаревшими графиками. Тестами это не ловится: Level 0 проверяет структуру и
ссылки, Level 1 — скрипты, семантическое ослабление правила на естественном
языке видно только в e2e или по плохой лекции.

**Способ снижения риска (обязателен к соблюдению):**
- существующее предложение про `figures.py` остаётся **побайтово тем же**;
- quarto добавляется **отдельным пунктом**, а не переписыванием старого в
  обобщённую форму;
- ветка включается по **наблюдаемому факту** (файл дека — `slides.qmd`), а не по
  намерению или режиму, который надо вывести.

---

## 6. Обоснование D6 — заметки лектора

`::: {.notes}` даёт presenter mode в reveal.js и панель заметок в pptx — от этого
отказываться незачем. Но авторство заметок прямо в `slides.qmd` ломает шаг 5: у
него есть режимы `minimal/medium/detailed`, расчёт объёма под тайминг из
`plan.md` по `Speech rate:`, итоговая таблица таймингов и список кандидатов на
выброс. Ничему из этого не место в панели докладчика. Плюс шаг 4 **дописывает**
дек чанками, а заметки надо вставлять между слайдами — это правка одобренного
файла в двадцати местах.

**Решение: один авторский источник + механическая проекция в дек.**

- `speaker_notes.md` остаётся тем, что пишет шаг 5, — без изменений.
- В конце шага 5 для quarto-дека заметки вставляются в `slides.qmd` как
  `::: {.notes}` после каждого `##`. Это часть шага 5, в рамках его
  единственного одобрения — правило «не переходить к следующему шагу самому» не
  нарушается.
- Повторный запуск: `/course-maker notes N inject`. Идемпотентно: каждый
  вставленный блок помечен `<!-- course-maker:notes NN -->`, повторная вставка
  сносит помеченные блоки и пишет заново.
- В дек уходит только текст по слайдам. Таблица таймингов и кандидаты на выброс
  остаются в `speaker_notes.md`.
- Ручная правка внутри помеченного блока не затирается молча: сравнить с тем,
  что дал бы `speaker_notes.md`, и сообщить — как существующее правило про
  `git diff` на файле-предпосылке.

**Отклонённая альтернатива:** сделать `slides.qmd` источником заметок, а
`speaker_notes.md` генерировать из него. Отклонено — таблице таймингов, режимам
и кандидатам на выброс негде жить в деке, и шаг 5 стал бы править чужой
артефакт вместо создания своего.

---

## 7. Этап 1 — Quarto как формат слайдов

Ядро. После него курс можно вести целиком на Quarto.

### Шаг 1.1. Шаблон headmatter
**Файл (новый):** `skill/templates/slides_headmatter_quarto.qmd`
YAML-блок с плейсхолдерами `[Course name]`, `[Author]`, `[Institution]`,
`[Lecture] N. [Title]` (те же имена, что в beamer/slidev-шаблонах) и с тремя
объявленными таргетами `revealjs` / `beamer` / `pptx`. Только подтверждённые
опции из § 3. `lang:` — BCP 47. В beamer-блоке `pdf-engine: xelatex` и
закомментированный `mainfont`. В pptx-блоке — закомментированный `reference-doc`
со списком обязательных имён layout'ов. Блок `execute:` с закомментированным
`cache: true` и пояснением про `--cache-refresh`.
**Критерий:** проходит `tests/static/test_english_only.py`; YAML валиден.

### Шаг 1.2. Reference шага 4
**Файл (новый):** `skill/references/step4_slides_quarto.md` (~200 строк, по
образцу `step4_slides_slidev.md`). Разделы:
1. Шапка: что производит, когда используется, ссылки на два других пути.
2. Note про `seminars/NN/` как зеркало `lectures/NN/`.
3. «Context to gather» — headmatter = `slides_headmatter.qmd`; список PNG
   обязателен только для визуализаций с `render: png`.
4. Headmatter: подстановка плейсхолдеров, stop-сообщение при отсутствии файла.
5. **Slide syntax:** `##` = слайд, `#` = секция; явное предупреждение, что `---`
   даёт слайд без заголовка и разделителем быть не должен; маркер
   `<!-- Slide NN -->`; нумерация (1 = титульный из YAML, 2 = план, первый
   содержательный = 3), запрет перенумерации.
6. **Figures — два режима (D5).** `png`: ссылка `![](figures/figNN_name.png){width="70%"}`,
   только на существующие файлы. `inline`: `{python}`-чанк, опции через `#|`,
   `#| echo: false` для слайдов, где код не является содержанием.
   После последнего чанка — обязательный `quarto render`, чинить до чистого
   прогона.
7. **Интерактивные визуализации и мультиформат.** Паттерн
   `.content-visible when-format="html"` / `when-format="pdf"`; оговорка, что
   обе ветки выполняются; рекомендация: если курс регулярно экспортируется в
   pptx/PDF, статика по умолчанию, интерактив — осознанное решение с fallback.
8. **Portability checklist:** запрет сырого LaTeX/TikZ в общем контенте (D8),
   явная ширина у каждой картинки, ≤2 display-формулы на слайд, отказ от
   HTML/CSS-трюков, не переживающих pptx.
9. Layout: `:::: {.columns}` / `::: {.column width="…"}`; плотность (≤6–7
   буллетов, ≤3 callout-блока).
10. Заметки: `::: {.notes}` пишет **шаг 5**, а не шаг 4 (ссылка на D6).
11. Чанкинг: чанк 0 = headmatter + слайд «План»; чанк K = 5 блоков `##`;
    последний = финальный слайд. Дописывать сразу, не останавливаться между
    чанками, одобрение — за дек целиком.
12. Title / outline / closing; правила перекрёстных ссылок; логирование итераций
    в `history.md`.
**Критерий:** структурные тесты зелёные после шага 1.6.

### Шаг 1.3. Шаг 2 — режим визуализации
**Файл:** `skill/references/step2_visuals.md`
Добавить у каждой визуализации поле `render: inline | png`. Для beamer/slidev
поле отсутствует или всегда `png` (формат не поддерживает inline). Для quarto —
дефолт `inline`, `png` выбирается осознанно (например, картинка нужна и в
раздатке, и в лабораторной).
**Критерий:** файл не навязывает `png` там, где формат курса — quarto.

### Шаг 1.4. Шаг 3 — условность для quarto
**Файл:** `skill/references/step3_figures.md`
Шаг остаётся обязательным для beamer/slidev **дословно как сейчас**. Для quarto:
если в `visuals.md` нет ни одной визуализации с `render: png` — шаг пропускается,
статус `n/a`; если есть — `figures.py` генерирует только их.
**Критерий:** beamer-ветка файла не изменена по смыслу; quarto-ветка не требует
пустого `figures.py`.

### Шаг 1.5. Шаг 5 — инъекция заметок
**Файл:** `skill/references/step5_notes.md`
Добавить финальную фазу для quarto-деков: инъекция `::: {.notes}` с маркерами
`<!-- course-maker:notes NN -->`, идемпотентность, обработка ручных правок,
что инжектится и что остаётся только в `speaker_notes.md`.
**Проверено (2026-08-25):** `::: {.notes}` работает во всех трёх таргетах, в
beamer превращается в `\note{...}`. Инжектим для всех. Для показа заметок в
beamer нужна одна строка `\setbeameroption{show notes on second screen=right}`
через `include-in-header` — `pgfpages` Quarto подключает сам; идёт в шаблон
headmatter закомментированной.
**Критерий:** повторный `notes N inject` не плодит дубли блоков.

### Шаг 1.6. SKILL.md
**Файл:** `skill/SKILL.md`
- Таблица команд: строка `slides N [format]` — третий формат; строка
  `slides N export` — аргументы зависят от формата дека; новая строка
  `notes N inject`.
- § `slides N [format]`: ветка `quarto → references/step4_slides_quarto.md`
  (produces `slides.qmd`); в резолве `beamer|slidev|quarto`; в детекте при
  `next` — `slides.qmd` → quarto; **убрать** «`pptx` is not implemented» и
  заменить указанием, что pptx получается экспортом quarto-дека.
- CRITICAL-блок шага 4: в пункт про преамбулу добавить `slides_headmatter.qmd`.
  **Блок не переписывать и не сокращать** — только дополнить перечисление.
- **Inviolable rules → «Slides & figures» — самая рискованная правка (§ 5).**
  Существующие пункты про PNG и `figures.py` оставить побайтово. Добавить
  отдельный пункт: для дека `slides.qmd` визуализация может быть исполняемым
  чанком, и тогда `figures → ✅` требует чистого `quarto render`; PNG-пункты
  продолжают действовать для всех PNG-ссылок в любом формате.
- § `slides N export`: quarto в детекте.
- § Seminar workflows: третья ветка в резолве формата.
- § `notes N`: упомянуть фазу инъекции для quarto.
**Критерий:** структурные тесты зелёные; `grep` не находит «pptx not
implemented»; diff по блоку Inviolable rules — только добавления.

### Шаг 1.7. course init
**Файл:** `skill/references/course_init.md`
- Phase 1, проверка 4: третий вариант headmatter (`slides_headmatter.qmd`).
- Phase 2c, вопрос 7: `beamer` / `slidev` / `quarto` с описанием quarto; вопрос 8
  (LaTeX-движок) остаётся только для `beamer` — для quarto движок задаётся в
  headmatter и ставится через `quarto install tinytex`.
- Phase 3: ветка копирования `templates/slides_headmatter_quarto.qmd` →
  `slides_headmatter.qmd` + confirm-сообщение.
**Критерий:** формат `quarto` проходит визард, не заходя в beamer-ветку.

### Шаг 1.8. Экспорт
**Файл:** `skill/references/slides_export.md`
- Детект: `slides.qmd` → quarto.
- Ветка quarto: `pdf`→`--to beamer`, `html`→`--to revealjs`, `pptx`→`--to pptx`;
  `png` не поддержан — предложить `pdf` + `pdftoppm`.
- Ошибки: нет `quarto` → как поставить (`brew install quarto`,
  https://quarto.org/docs/get-started/); beamer-таргет без LaTeX →
  `quarto install tinytex`; упавший чанк → показать вывод и чинить, не
  маскировать через `error: true`.
- В шапку, где сказано, что показ Slidev вживую — дело пользователя, добавить
  `quarto preview` в том же смысле.
**Критерий:** ни один отказной сценарий не завершается молча.

### Шаг 1.9. doctor
**Файл:** `skill/references/doctor.md`, Step 2, проверка 2
Сейчас жёстко зашит `slides_preamble.tex` — уже неверно для slidev-курсов.
Сделать формато-зависимой по полю `Slides format:`: `beamer` →
`slides_preamble.tex`, `slidev` → `slides_headmatter.md`, `quarto` →
`slides_headmatter.qmd`. Добавить проверку наличия `quarto` в PATH для
quarto-курсов (совет, не ошибка).
**Критерий:** doctor на slidev- и quarto-курсе не требует `slides_preamble.tex`.

### Шаг 1.10. validate_state.py
**Файлы:** `skill/scripts/validate_state.py`, `tests/unit/test_validate_state.py`
Единственная правка кодом в этапе 1. Сейчас `figures ✅` ⇒ PNG на диске, и
inline-лекция даст ложный `DRIFT`. Сделать проверку формато-зависимой: если дек
лекции — `slides.qmd` и содержит исполняемые чанки, отсутствие PNG законно.
Плюс поддержать новое значение статуса `n/a` для шага figures.
Добавить unit-тесты на оба случая.
**Критерий:** `pytest tests/unit` зелёный; искусственная inline-лекция не даёт
`DRIFT`, а beamer-лекция без PNG — даёт.

### Шаг 1.11. Шаблон контекста и layout
**Файлы:** `skill/COURSE_AGENTS_TEMPLATE.md`, `skill/references/repository_layout.md`
- Комментарий к `Slides format:` дополнить вариантом `quarto`, убрать «pptx is
  planned».
- В «Course root» добавить `slides_headmatter.qmd`; в «Lectures» — `slides.qmd`;
  отметить, что `figures/` для quarto-лекции может отсутствовать.
- Документировать значение статуса `n/a`.
**Критерий:** ни один файл не описывает набор форматов как «два».

### Шаг 1.12. E2E-смоук
**Файл:** `tests/e2e/test_slides_quarto_smoke.py` (новый)
По образцу существующего: сгенерировать quarto-дек, распарсить `![](…)`-ссылки и
потребовать существования файлов, затем `quarto render slides.qmd --to revealjs`
и проверить появление `slides.html`. Отдельный кейс: дек с inline-чанком
рендерится чисто. `pytest.skip`, если `quarto` не в PATH — как сделано для
`xelatex`.
**⚠️ E2E запускает пользователь вручную** (Level 3, opt-in `COURSE_MAKER_E2E`).
Агент их пишет, но не выполняет.

### Шаг 1.13. Документация
`CHANGELOG.md`; `docs/IMPROVEMENT_PLAN.md` (волна 7.1 — pptx закрыт через
Quarto); `docs/PROJECT_CONTEXT.md` (дерево файлов); `README.md` и `README.ru.md`.

**Критерий готовности этапа 1:** на тестовом курсе с `Slides format: quarto`
проходит цепочка `course init` → `plan` → `visuals` → `slides` →
`slides export html` → `slides export pdf` → `slides export pptx` → `notes` →
`notes inject`, причём хотя бы одна визуализация — inline-чанк, а шаг `figures`
пропущен. Level 0 и Level 1 зелёные. Beamer- и slidev-курсы работают без
изменений.

---

## 8. Этап 2 — Quarto как бэкенд экспорта документов

### Шаг 2.1. Общий reference экспорта
**Файл (новый):** `skill/references/doc_export.md` — единственное место,
описывающее «markdown-файл → pdf / latex / docx»:
- резолв бэкенда: поле `Doc export:` в `AGENTS.md` → дефолт `pandoc` (D9);
- ветка pandoc — команды, перенесённые из `syllabus.md` / `homework.md` без
  изменения поведения;
- ветка quarto — `quarto render <file> --to typst` (PDF без LaTeX), `--to docx`,
  `--to latex`; оговорка про явную ширину картинок в Typst;
- отказные сценарии: нет выбранного инструмента → сказать какой и как поставить,
  оставить markdown на месте, **не** переключаться на другой бэкенд.

### Шаг 2.2. syllabus
**Файл:** `skill/references/syllabus.md` — заменить встроенный pandoc-блок
ссылкой на `doc_export.md`, сохранив состав аргументов команды.

### Шаг 2.3. homework
**Файл:** `skill/references/homework.md` — то же. **Осторожно:** рядом
CRITICAL-проверка на утечку рубрики в `homework_student.md` — не трогать.

### Шаг 2.4. quiz publish
**Файл:** `skill/references/quiz_publish.md` — добавить `pdf` / `docx` через
`doc_export.md`. **Осторожно:** Inviolable rule про отсутствие ответов в
студенческом файле — проверка на утечку выполняется **до** конвертации, и
конвертируется уже очищенный файл. Обновить строку таблицы в `SKILL.md`.

### Шаг 2.5. Поле в шаблоне контекста
**Файл:** `skill/COURSE_AGENTS_TEMPLATE.md` — `**Doc export:** pandoc` с
комментарием; плюс `SKILL.md`, где перечислены поля `AGENTS.md`.

**Критерий готовности этапа 2:** `syllabus pdf`, `homework publish N pdf`,
`quiz publish N pdf` дают PDF на машине **без установленного LaTeX**, если
`Doc export: quarto`; при `Doc export: pandoc` поведение идентично текущему.

---

## 9. Этап 3 — сайт курса

Самый объёмный этап; главная работа здесь не рендер, а защита от утечки.

### Шаг 3.0. Проверить риск `_quarto.yml` в корне — **до всего остального**
`_quarto.yml` в корне курса превращает **всё дерево** в Quarto-проект: меняется
`output-dir`, и рендер отдельного дека `lectures/NN/slides.qmd` может начать
складывать результат в каталог сайта, а не рядом с исходником. Это ломает этап 1.
Проверить экспериментально; если подтвердится — держать проект сайта в
подкаталоге (`site/`) со своим `_quarto.yml`, а не в корне. Здесь же
пригодится `freeze: auto`, чтобы сборка сайта не перевыполняла дорогие чанки.

### Шаг 3.1. Команда и диспетчер
`/course-maker site [init|render|preview|publish]` в `SKILL.md` (таблица +
диспетчер + `help`).

### Шаг 3.2. Reference
**Файл (новый):** `skill/references/site.md`: `site init` (создать `_quarto.yml`,
выбрать способ публикации), `site render`, `site preview` (запускает
пользователь), `site publish`.

### Шаг 3.3. Allow-list содержимого
**Ключевое решение этапа.** Явный список того, что попадает на публичный сайт:
`syllabus.md`, публичная часть `course_plan.md`, отрендеренные деки
лекций/семинаров, `README.md` лаб, `homework_student.md`, студенческие версии
квизов.
Явный deny-list: `rubric.md`, `quizzes/NN/quiz_questions.md`, `lab_spec.md`,
`tests.py`, `conftest.py`, `speaker_notes.md`, `history.md`, `COURSE_STATE.md`,
`lms_adapter.md`, содержимое `labs/*/starter/` сверх README.
**Отдельно:** инжектированные `::: {.notes}` (D6) не должны попасть в
опубликованный HTML — проверить, что `embed-resources`/reveal не выкладывает их
в исходник страницы, и при необходимости рендерить публичную версию дека без
заметок.

### Шаг 3.4. CRITICAL-проверка перед публикацией
`grep`-guard по собранному сайту перед `publish`, по образцу проверки в
`homework publish`. Публикация блокируется при любом совпадении. Правило
продублировать в `SKILL.md` inline, не только в reference.

### Шаг 3.5. Шаблон `_quarto.yml`
**Файл (новый):** `skill/templates/quarto_site_yml.md` — `project: type: website`,
навигация по разделам курса, `output-dir`, `.nojekyll`, `freeze: auto`.

### Шаг 3.6. Способы публикации
Три варианта из § 3, выбор фиксируется при `site init`.

**Критерий готовности этапа 3:** `site render` собирает сайт; grep-guard ловит
искусственно подложенный `rubric.md`; экспорт отдельного дека
(`slides N export pdf`) после появления `_quarto.yml` продолжает класть файл в
`lectures/NN/`; заметок лектора нет в опубликованном HTML.

---

## 10. Чеклист прогресса

Обновлять по мере выполнения — это точка возобновления после очистки контекста.

**Этап 1 — формат слайдов** — выполнен 2026-08-25, ветка `quarto-support`
- [x] 1.1 `templates/slides_headmatter_quarto.qmd` — проверен рендером во все три таргета
- [x] 1.2 `references/step4_slides_quarto.md`
- [x] 1.3 `references/step2_visuals.md` — колонка `Render`
- [x] 1.4 `references/step3_figures.md` — условность для quarto
- [x] 1.5 `references/step5_notes.md` — инъекция заметок
- [x] 1.6 `SKILL.md` — диспетчеры, таблицы, Inviolable rule (диффом проверено: только добавления)
- [x] 1.7 `references/course_init.md`
- [x] 1.8 `references/slides_export.md`
- [x] 1.9 `references/doctor.md`
- [x] 1.10 `scripts/validate_state.py` + 5 unit-тестов
- [x] 1.11 `COURSE_AGENTS_TEMPLATE.md` + `references/repository_layout.md`
- [x] 1.12 e2e-смоук написан (`tests/e2e/test_slides_quarto_smoke.py`) — **не запускался, запускает пользователь**
- [x] 1.13 CHANGELOG, IMPROVEMENT_PLAN, PROJECT_CONTEXT, оба README

Не сделано на этапе 1 и осознанно отложено: критерий готовности требует прогона
полной цепочки команд на тестовом курсе — это e2e, запускает пользователь.

**Этап 2 — экспорт документов**
- [ ] 2.1 `references/doc_export.md`
- [ ] 2.2 `references/syllabus.md`
- [ ] 2.3 `references/homework.md`
- [ ] 2.4 `references/quiz_publish.md` + `SKILL.md`
- [ ] 2.5 `COURSE_AGENTS_TEMPLATE.md` — поле `Doc export:`

**Этап 3 — сайт**
- [ ] 3.0 Проверить риск `_quarto.yml` в корне
- [ ] 3.1 Команда и диспетчер в `SKILL.md`
- [ ] 3.2 `references/site.md`
- [ ] 3.3 Allow-list / deny-list содержимого
- [ ] 3.4 CRITICAL grep-guard перед публикацией
- [ ] 3.5 `templates/quarto_site_yml.md`
- [ ] 3.6 Способы публикации на GitHub Pages

---

## 11. Открытые вопросы

1. **Нужно ли поле `Quarto target:` в `AGENTS.md`?** Пока нет: дефолт экспорта —
   `pdf`, остальное явным аргументом. Если основным режимом показа окажется
   reveal.js, дефолт стоит сделать настраиваемым.
2. **Тема оформления.** Сейчас всё в `slides_headmatter.qmd`. Если понадобится
   общий `.scss`, появится ещё один файл в корне курса — решать по факту.
3. **Библиография.** `[@ref]` + `.bib` — заметное преимущество Quarto для курса
   по DL, в план не включено. Кандидат в отдельную задачу после этапа 1.
4. **Окружение исполнения.** Inline-чанки требуют Jupyter-движка. У заказчика
   `/opt/anaconda3/bin/python` со всеми пакетами. Нужно решить, фиксируется ли
   интерпретатор в headmatter курса или берётся из окружения.

---

## 12. Источники

- Revealjs: https://quarto.org/docs/presentations/revealjs/
- Справочник опций revealjs: https://quarto.org/docs/reference/formats/presentations/revealjs.html
- Beamer: https://quarto.org/docs/presentations/beamer.html
- PowerPoint: https://quarto.org/docs/presentations/powerpoint.html
- Опции исполнения: https://quarto.org/docs/computations/execution-options.html
- Freeze и cache: https://quarto.org/docs/projects/code-execution.html
- Условный контент: https://quarto.org/docs/authoring/conditional.html
- Typst: https://quarto.org/docs/output-formats/typst.html
- PDF-движки и TinyTeX: https://quarto.org/docs/output-formats/pdf-engine.html
- Мультиформатный вывод: https://quarto.org/docs/output-formats/html-multi-format.html
- `quarto render` CLI: https://quarto.org/docs/cli/render.html
- Публикация на GitHub Pages: https://quarto.org/docs/publishing/github-pages.html
