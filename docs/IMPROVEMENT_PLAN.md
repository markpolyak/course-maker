# course-maker — обзор, разбор и план улучшений

**Дата:** 2026-06-13
**Контекст:** комплексный обзор скила, обсуждение в чате, и план реализации.
**Статус:** план готов к выполнению.

Документ состоит из трёх частей:
1. **Полный обзор скила** (архитектура, сильные стороны, проблемы, универсализация).
2. **Разбор вопроса про SKILL.md** (почему «всё критическое в SKILL.md» — неверный рецепт).
3. **План реализации** — волны, атомарные шаги, критерии готовности.

---

# Часть I. Полный обзор скила

## 1. TL;DR

Скил уровня выше среднего: продуманная схема state-tracking через `history.md`, идемпотентные инициализаторы, грамотная chunked-генерация Beamer, недавняя языковая абстракция через `course_conventions.md` и `lab_templates.md`. Но есть несколько **серьёзных архитектурных косяков**:

- `SKILL.md` раздулся до 978 строк (а должен быть ≤300).
- Критические шаблоны (`conftest_base.py`, `tests.yaml`) — **нерабочие placeholder'ы**, скил не bootstrap'ится из коробки.
- `tests_template.py` всё ещё захардкожен на русском.
- Весь lab-пайплайн жёстко связан с GitHub Classroom + специфической CI-строкой `ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА В ЖУРНАЛ`.

Универсальной системой это пока не является — это персональный пайплайн преподавателя, который пытается выглядеть универсальным.

---

## 2. Архитектура: что сделано хорошо

| | Решение | Почему сильно |
|---|---|---|
| ✅ | `history.md` как анти-повтор-память | Главное «лекарство» от классической боли — Claude не забывает, что уже отвергли |
| ✅ | Chunked-генерация slides и notes по 5 слайдов | Реально решает проблему таймаутов на 20-слайдовых лекциях |
| ✅ | Идемпотентные `course init` / `lab course-init` с auto-detect фазой | Безопасно перезапускается, не ломает существующее |
| ✅ | Per-course `course_conventions.md` + `lab_templates.md` | Правильный шаг к language-agnostic ядру |
| ✅ | Жёсткое разделение `lab_spec.md` (instructor-only) vs `starter/` (студенту) | Принципиально верное архитектурное решение |
| ✅ | Защита validate-фазы: `/clear` + `git status` + `git restore` | Учтены реальные грабли |
| ✅ | Auto-mode (plan vs notebook) в `lab spec` | Хорошее объединение `spec` и `reverse-spec` |
| ✅ | Per-engine LaTeX preamble (`pdflatex`/`xelatex`) | Грамотный отказ от хардкода |
| ✅ | Web-search версий PyPI перед `requirements.txt` | Защита от старых локальных кэшей |
| ✅ | Inline критические правила для validate (коммит `1781bd7`) | Правильный паттерн защиты от пропуска reference-файлов |

---

## 3. Архитектура: что плохо или сомнительно

### 🚨 SKILL.md распух до 978 строк

В `PROJECT_CONTEXT.md` декларируется: «SKILL.md под ~300 строк, детали в references/». Сейчас все полные workflow продублированы прямо в SKILL.md (особенно `course plan`, `course init`, `lab course-init`). Это:
- съедает контекст при каждом запуске;
- создаёт два источника правды (например `lab spec` описан и в SKILL.md, и в `lab_step1b_spec.md`);
- ломает обещанный паттерн «lazy-load reference files»;
- **топит реально критические правила** среди второстепенного workflow-материала.

Корень проблемы — не «всё постепенно переехало наверх», а «init/plan-workflow'ы никогда не выносились в references/».

### 🚨 Шаблоны `conftest_base.py` и `tests.yaml` — нерабочие placeholder'ы

`conftest_base.py` буквально содержит `# PLACEHOLDER — paste from real lab here`, а `lab course-init` делает workaround: «если нет реального — копируй из существующей лаборатории». **Для нового пользователя нет существующей лаборатории.** Скил не bootstrap'ится из коробки. Это критический discoverability-блокер.

### 🚨 `tests_template.py` — полностью на русском

Файл — единственный источник стиля тестов для Stage 2, и он целиком на русском (docstrings, классы `TestVariableExample` с русскими докстрингами, сообщения об ошибках). Противоречит правилу из `CLAUDE.md`: «skill/ — English only». Языковая абстракция была сделана наполовину.

### 🚨 Жёсткая связка с конкретным CI преподавателя

`conftest_base.py` и `lab_step2_tests.md` обязывают сохранять verbatim:
```
print(f"  TASKID is {dataset_id + 1}")
print(f"  ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА В ЖУРНАЛ: ...")
```
Это конкретная внешняя CI-grading-система. Для любого другого преподавателя эти строки бессмысленны, но скил подаёт их как «critical invariant — никогда не менять». При этом `lab_templates_*.md` уже содержит локализованную версию строки — но `conftest_base.py` всё равно жёстко требует verbatim русскую строку.

### 🚨 Внедрение скила в курсовое CLAUDE.md через `SKILL:START`/`SKILL:END`

`COURSE_CLAUDE_TEMPLATE.md` обещает встроить контент `SKILL.md` между маркерами, а при обновлении — «запустить `/skill update`». Команды `/skill update` **не существует**. Разваливается при первом же обновлении скила в `~/.claude/skills/`. Лучше убрать встройку — скил уже подхватывается из `~/.claude/skills/` глобально.

### ⚠️ Атомарность стейта не гарантирована

`COURSE_STATE.md` обновляется «в конце команды», но если Claude упадёт на `gh api` в `lab publish` — половина файлов засинхронизирована, история не записана, флаг `published` не выставлен. Никакого rollback'а нет.

### ⚠️ `history.md` растёт неограниченно

В `status` показываются «последние 3 записи», но сам файл — append-only. На 20-й итерации лекции это сотни строк, читаемых в каждом step. Нужна стратегия compaction (свернуть старые итерации в сводку, оставить полностью только последние N).

### ⚠️ Манипуляция git subtree из инструкций

`lab publish` использует `git subtree push` — известная острая команда, при конфликтах требует ручного `git subtree split`. Обработки конфликтов в инструкциях нет. На GitHub Classroom с force-history это рано или поздно сломается.

### ⚠️ Не определён workflow при failed validation

`lab validate` помечает `validated → ⚠️`, но дальше нет команды «исправь по итогам валидации». Преподаватель сам должен понимать, в какой step возвращаться.

### ⚠️ Нет sanity-check перед `slides` chunk 0

Скил проверяет наличие PNG, но не проверяет, что `figures.py` действительно был запущен (а не просто помечен ✅). Помеченное ✅ ≠ актуальное. Решение: сравнить mtime PNG с mtime `figures.py`.

---

## 4. Дрейф документации

| Файл | Проблема |
|---|---|
| `README.md` | Упоминает `examples/stochastic-processes/`, которого в репозитории нет |
| `docs/getting-started.md` | Документирует `/course-maker lab reverse-spec` — команда удалена |
| `docs/PROJECT_CONTEXT.md` | Использует устаревший layout (`course-maker/SKILL.md`) |
| `docs/LAB_PIPELINE_PLAN.md` | На русском в `docs/` — допустимо, но противоречит общему английскому правилу |
| `docs/TEMPLATE_MIGRATION_PLAN.md` | Описывает уже завершённую миграцию — кандидат на архивацию |
| `COURSE_CLAUDE_TEMPLATE.md` | Ссылается на несуществующую команду `/skill update` |
| `CHANGELOG.md` | Даты `2026-05-31` и `2026-06-13` — путаница с будущими датами |

---

## 5. Универсализация vs персональные требования

### Что специфично и плохо обобщается

1. **GitHub Classroom + `gh api` синхронизация** — большинство преподавателей вузов используют LMS (Moodle, Canvas, OpenEdX).
2. **`Student_ID = (Student_ID - 1) % len(datasets)` как «critical invariant»** — конкретная система вариантов. У других — жеребьёвка, фиксированное распределение, командные проекты.
3. **`ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА В ЖУРНАЛ`** — конкретная строка для конкретной CI.
4. **Beamer-only output** — большинство преподавателей предпочитают PowerPoint/Google Slides.
5. **Jupyter notebook + pytest + autograding** — STEM-уклон. У гуманитариев другой формат.
6. **«Master's-level» аудитория в `lab_context.md`** — захардкожено в роль.

### Стратегия совмещения

Разделить на **три уровня**, не два:

```
skill/                        ← универсальное ядро (любой курс)
  SKILL.md                    ← тонкий диспетчер (~250 строк)
  references/                 ← step1..step5 для лекций + init-workflow'ы
  templates/                  ← language-нейтральные шаблоны
profiles/                     ← новое: профили преподавателей
  polyak/                     ← персональный профиль
    lab_grading.yaml          ← TASKID / ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА
    lms_adapter.md            ← GHC + gh API
    conftest_base.py          ← реальный conftest
    tests_template.py         ← реальный шаблон тестов
    course_defaults.yaml      ← Master's, ITMO и т.п.
  generic/                    ← минимальный пустой профиль
    conftest_base.py          ← generic pytest
    lms_adapter.md            ← локальный grading (без LMS)
    tests_template.py         ← English universal
```

В курсовом `CLAUDE.md` — поле `profile: polyak` / `profile: generic`. Скил подмешивает профильные файлы. Тогда:
- персональные сценарии полностью поддерживаются;
- другие преподаватели получают работающий минимум;
- между ними нет конфликта.

Это честнее, чем нынешнее «универсальный скил с русской строкой как critical invariant».

---

## 6. Полный список улучшений (по приоритету)

### 🔴 P0 — починить, чтобы скил работал для не-тебя

1. Реальный `conftest_base.py` в `skill/templates/` — рабочий универсальный pytest-хук.
2. Реальный `tests.yaml` в `skill/templates/` — рабочий GitHub Actions CI.
3. Перевести `tests_template.py` на английский (или вынести в `lab_templates_*.md`).
4. Удалить «critical invariant» на русскую строку. Сделать формат grade-output параметром из `lab_templates.md`.
5. Удалить упоминания несуществующих команд: `/skill update`, `lab reverse-spec`.
6. Создать `examples/` хотя бы с одним полным примером — `lectures/01/` со всеми артефактами.

### 🟠 P1 — архитектурная гигиена

7. Сократить `SKILL.md` до ≤300 строк — оставить Quick Reference + диспетчер.
8. Вынести workflow'ы `course init` / `course plan` / `lab course-init` в references/.
9. Добавить глобальный блок `## Inviolable rules` в SKILL.md (10–15 пунктов).
10. Убрать встройку SKILL.md в COURSE_CLAUDE_TEMPLATE.md (`SKILL:START`/`END`).
11. Скрипт `scripts/validate_state.py` — проверка COURSE_STATE.md против реальных файлов.
12. Compaction для `history.md` — команда сворачивания старых итераций.
13. Sanity check перед `slides`: PNG mtime > figures.py mtime.

### 🟡 P2 — недостающие части пайплайна

14. Pipeline для тестов/контрольных (`/course-maker quiz N`).
15. Pipeline для семинаров (`/course-maker seminar N`).
16. Pipeline для домашних заданий (`/course-maker homework N`).
17. `/course-maker lab triage N` — после неудачной валидации.
18. Syllabus PDF — `/course-maker syllabus`.

### 🟢 P3 — универсализация

19. Профили преподавателей (`profiles/polyak/` + `profiles/generic/`).
20. PowerPoint output параллельно с Beamer.
21. LMS-адаптеры как первоклассный концепт.
22. Альтернативные среды лабораторных — R Markdown, MATLAB Live Scripts.
23. Расширенные языки: fallback на английский, шаблоны для DE/FR/ES.

### 🔵 P4 — качество жизни

24. `/course-maker doctor` — проверка согласованности курса.
25. Линтер для `course_plan.md`.
26. `/course-maker stats` — прогресс-bar по курсу.
27. Lock-файл для COURSE_STATE.md.
28. Accessibility-чек слайдов.
29. `/course-maker translate-course <lang>` — перевод готовых материалов.

---

# Часть II. Разбор вопроса про SKILL.md

## Контекст

В чате прозвучало: «Claude уверял меня, что упоминание необходимости загрузить файл с подробным описанием действий для конкретной подкоманды внутри `/course-maker` не означает, что этот файл будет прочитан. Поэтому все критические вещи должны обязательно помещаться в сам SKILL.md». Это привело к раздуванию SKILL.md.

## Разбор

Это реальная проблема, но вывод «всё критическое в SKILL.md» — **правильный диагноз, неправильный рецепт**.

### Что действительно происходит

- `SKILL.md` гарантированно загружается при срабатывании скила.
- Файлы из `references/` подгружаются по требованию инструкции «read X». Эти инструкции иногда игнорируются — особенно при заполненном контексте или слабой формулировке (`see X for details`).
- **Но даже правило внутри SKILL.md может быть проигнорировано**, если оно похоронено в 100-строчном workflow и не подсвечено. Шанс соблюдения у такого правила ненамного выше, чем у вынесенного.

«Положить в SKILL.md» ≠ «гарантировано соблюсти». Гарантию даёт не местоположение, а **форма правила**.

### Правильный паттерн уже найден

Коммит `1781bd7 Harden lab validate: inline critical rules to prevent silent skips` — идеальная модель:
- В SKILL.md остался тонкий диспетчер: `Read: references/lab_step3_validate.md`.
- Плюс компактный блок `**CRITICAL rules — apply regardless of whether the reference file was read:**` из 4 строк.
- Полный 163-строчный workflow — в reference-файле.

Это и есть нужная архитектура. Лаконично, наглядно, защищено от пропуска.

### Что разрушает паттерн в остальной части SKILL.md

`course init`, `course plan`, `lab course-init` — не «inlined critical rules», а полные workflow'ы целиком в SKILL.md, без выноса в references/. Это ~500 строк среднеценного материала. Они:
1. Загружаются в каждой сессии (раздувают контекст).
2. **Топят в себе реально критические правила**.
3. Не помечены как inviolable — формулировки разбросаны по шагам.

### Что делает правило «липким» — независимо от файла

| Признак | Слабая форма | Сильная форма |
|---|---|---|
| Длина | 5–7 строк объяснения | 1 строка приказа |
| Видимость | Внутри workflow-шага | Отдельный блок `## Inviolable rules` |
| Рамка | «Не следует X» / «При X сделай Y» | `NEVER do X` / `STOP before X` |
| Чекпоинт | Нет | «Confirm in chat you read refs/X.md before proceeding» |
| Позиция | Середина файла | Топ, до workflow-секций |

### Вывод

Защищать надо **правила**, а не **workflow'ы**. SKILL.md должен содержать:
- Quick Reference таблицы команд.
- Глобальный блок `## Inviolable rules` (10–15 коротких пунктов).
- Тонкие диспетчеры команд: «Read: references/X.md».
- Для команд с историей провалов — короткий inline-блок `**CRITICAL — even if reference was skipped:**`.

Всё остальное — в references/.

---

# Часть III. План реализации

План разбит на **волны**. Каждая волна — логически связанная группа изменений, после которой состояние репозитория консистентно. Внутри волны — атомарные шаги, каждый — один коммит.

## Волна 1. Архитектура SKILL.md (P1)

**Цель:** SKILL.md сокращён до ≤300 строк, критические правила выделены явно, workflow'ы вынесены.

### Шаг 1.1. Создать `references/course_init.md`
Перенести Phase 1–4 команды `/course-maker course init` из SKILL.md.
В SKILL.md оставить:
```
### `/course-maker course init`
Read: references/course_init.md
**CRITICAL — even if reference was skipped:**
- Never overwrite existing files (course_plan.md, CLAUDE.md, course_conventions.md)
- Phase 2 questions skipped only if answer is in CLAUDE.md
```

### Шаг 1.2. Создать `references/course_plan.md`
Перенести Phase 1–4 команды `/course-maker course plan` из SKILL.md.
В SKILL.md — тонкий диспетчер + CRITICAL.

### Шаг 1.3. Создать `references/lab_course_init.md`
Перенести Phase 1–6 команды `/course-maker lab course-init` из SKILL.md.

### Шаг 1.4. Добавить глобальный блок `## Inviolable rules` в SKILL.md
Собрать из существующих SKILL.md и references/ топ-15 критических правил:
- NEVER modify `dataset_id = (Student_ID - 1) % len(DATASETS)`
- NEVER read `history.md` during lab validate
- NEVER read `lab_spec.md` during lab validate
- NEVER reference PNG files that don't exist in `figures/`
- NEVER skip running `figures.py` before marking figures → ✅
- NEVER start lab validate without committed `<LAB_DIR>starter/`
- NEVER auto-advance to next step after approval
- NEVER use short-form commands (`/lecture …`, `/lab …`)
- NEVER skip `history.md` read before any step
- NEVER overwrite existing files in init wizards
- ALWAYS update COURSE_STATE.md at end of every command
- ALWAYS detect manual edits via git diff at start of next step
- ALWAYS ask user before saving any generated output
- ALWAYS use full command form when suggesting next command
- ALWAYS load `course_conventions.md` and `lab_templates.md` for lab commands

### Шаг 1.5. Добавить правило наблюдаемости
В `## Inviolable rules`:
```
In the first chat message of each step, list which reference files
you read and name the sections you consulted.
```

### Шаг 1.6. Привести в порядок диспетчеры всех команд
Для каждой команды в SKILL.md: оставить только заголовок, ссылку на references/, опциональный inline-блок CRITICAL.

**Критерий готовности волны 1:** `wc -l skill/SKILL.md` < 300. Все workflow'ы — в references/.

---

## Волна 2. Bootstrap-блокеры (P0)

**Цель:** Скил работает out-of-the-box для нового пользователя.

### Шаг 2.1. Реальный `conftest_base.py`
Заменить placeholder в `skill/templates/conftest_base.py` рабочим универсальным шаблоном:
- `import_student_notebook` — реализация через `nbformat` + exec
- `student_module` fixture
- `pytest_runtest_makereport` hook
- `pytest_sessionfinish` hook с настраиваемой grade output строкой
- Английские комментарии, английские сообщения по умолчанию
- Параметризуемые строки: `TASKID_LABEL`, `GRADE_OUTPUT_FORMAT` — читаются из переменных в начале файла

### Шаг 2.2. Реальный `tests.yaml`
Заменить placeholder в `skill/templates/tests.yaml` рабочим GitHub Actions workflow:
- Setup Python
- Install requirements.txt
- nbconvert ipynb → py
- Run pytest
- Upload artifacts

### Шаг 2.3. Перевести `tests_template.py` на английский
Все docstrings, классы, сообщения об ошибках — английский.
Удалить русские строки. Класс-имена оставить (TestVariableExample и т.п.).

### Шаг 2.4. Расхардкодить grade output строку
В `conftest_base.py`: использовать константу из `lab_templates.md`.
В `lab_step2_tests.md`: удалить требование verbatim русской строки, заменить на «format from `lab_templates.md`».
Обновить «critical invariants» в комментариях `conftest_base.py`.

### Шаг 2.5. Убрать упоминания несуществующих команд
- `COURSE_CLAUDE_TEMPLATE.md`: убрать упоминание `/skill update`. Заменить пояснением, что скил подхватывается из `~/.claude/skills/`.
- `docs/getting-started.md`: убрать пример с `/course-maker lab reverse-spec`.
- Проверить, что в SKILL.md нет упоминания reverse-spec (уже в git status видно `D lab_reverse_spec.md`).

### Шаг 2.6. Создать `examples/stochastic-processes/`
Хотя бы один полный пример курса:
- `CLAUDE.md` с заполненным контекстом
- `course_plan.md`
- `COURSE_STATE.md`
- `lectures/01/` со всеми артефактами (plan, visuals, figures, slides, notes, history)

Опция: вынести из существующего реального курса (с разрешения автора), почистив персональные данные.

**Критерий готовности волны 2:** `git clone` → `course init` → `lab init` → `lab tests` работает без «paste from real lab» workaround'а.

---

## Волна 3. Дрейф документации (P1)

**Цель:** Документация согласована с актуальным состоянием скила.

### Шаг 3.1. Обновить `docs/PROJECT_CONTEXT.md`
- Исправить layout (`course-maker/skill/SKILL.md` вместо `course-maker/SKILL.md`).
- Обновить статусы в «Known issues».
- Добавить пометку о завершении lab-pipeline (он уже сделан).

### Шаг 3.2. Архивировать завершённые планы
- `docs/TEMPLATE_MIGRATION_PLAN.md` → `docs/archive/TEMPLATE_MIGRATION_PLAN.md` (миграция завершена).
- `docs/LAB_PIPELINE_PLAN.md` → `docs/archive/LAB_PIPELINE_PLAN.md` (пайплайн реализован).

### Шаг 3.3. Обновить `README.md`
- Удалить упоминание `examples/stochastic-processes/` (если examples/ ещё не готов) или согласовать с реальностью.
- Привести таблицу команд в соответствие с актуальным SKILL.md.

### Шаг 3.4. Привести даты в `CHANGELOG.md` в порядок
- Проверить согласованность с `git log` (а не с интуицией про «будущие» даты).
- Добавить в CHANGELOG отсутствующие записи за коммиты, которые произошли
  между последней записью и текущим состоянием.

### Шаг 3.5. Решить судьбу `docs/LAB_PIPELINE_PLAN.md` (русский язык)
- Либо архив (см. 3.2).
- Либо перевод на английский, если документ всё ещё активный.

**Критерий готовности волны 3:** Любой пункт документации согласован с актуальным состоянием кода. Нет упоминаний несуществующих команд / файлов.

---

## Волна 4. Профили преподавателей (P3, но архитектурно фундаментальная)

**Цель:** Разделить персональный слой и универсальное ядро. Это разблокирует honest universalization без потери поддержки персональных сценариев.

> **Замечание после реализации (2026-06-14):** первая итерация волны 4 (коммит `35a37c1`) использовала схему «профиль = инструктор + LMS» с именами `polyak/` и `generic/`. Это оказалось плохой архитектурой: имя `polyak` бессмысленно для других преподавателей, а смешение инструктор-специфики и LMS-специфики в одну ось приводит к комбинаторному взрыву (`uni1-polyak`, `uni2-polyak`, …).
>
> Архитектура была пересмотрена (коммит «refactor profile system», след. за `35a37c1`):
> - Профиль = только LMS adapter. Имена LMS-нейтральные: `local-zip/`, `github-classroom/`.
> - Инструктор-специфика (`default_language`, `default_latex_engine`, `default_style`, etc.) живёт в **user_defaults** — отдельный файл `~/.course-maker/defaults.yaml` (с override через `$COURSE_MAKER_HOME`).
> - Профиль содержит: `lms.md` + `lab_questions.yaml` (LMS-config questions) + `lms_defaults.yaml` (LMS-config defaults) + `README.md`.
> - При `course init` user_defaults подмешиваются как suggestions; в конце предлагается сохранить ответы как новый user_defaults.
>
> Шаги 4.1–4.4 ниже описывают изначальный замысел; реальная реализация использует пересмотренную архитектуру.

### Шаг 4.1. Спроектировать структуру profiles/
```
skill/profiles/
  polyak/
    lab_grading.yaml          # TASKID_LABEL, GRADE_OUTPUT_FORMAT, etc.
    lms_adapter.md            # GHC + gh API workflow
    conftest_base.py          # реальный conftest
    tests_template.py         # реальный шаблон тестов
    course_defaults.yaml      # дефолты (audience, institution)
  generic/
    lab_grading.yaml          # минимальный (local grade output)
    lms_adapter.md            # local zip (без LMS)
    conftest_base.py          # generic
    tests_template.py         # generic
    course_defaults.yaml      # пусто / placeholders
```

### Шаг 4.2. Добавить поле `profile:` в `CLAUDE.md`
В `COURSE_CLAUDE_TEMPLATE.md` добавить:
```
### Profile
profile: generic   # one of: generic, polyak, ...
```

### Шаг 4.3. Обновить init wizards для чтения профиля
`course init` спрашивает / читает профиль; копирует профильные файлы в курсовой корень аналогично `course_conventions.md`.

### Шаг 4.4. Удалить персональные хардкоды из universal-слоя
- Из `lab_step2_tests.md`: убрать русскую CI-строку как invariant (теперь она в `profiles/polyak/lab_grading.yaml`).
- Из `lab_context.md`: «Master's-level» → параметр из профиля.

**Критерий готовности волны 4:** Скил работает с `profile: generic` без единого упоминания персональной CI / русской строки / GHC.

---

## Волна 5. Недостающие части пайплайна (P2)

**Цель:** Закрыть пробелы — тесты, семинары, домашки, syllabus.

### Шаг 5.1. `/course-maker syllabus` ✅ реализовано
Канонический `syllabus.md` из `course_plan.md` + экспорт через pandoc (pdf/latex/docx).
Reference: `references/syllabus.md`.

### Шаг 5.2. `/course-maker seminar N` ✅ реализовано
Семинар = колода (зеркало лекционного пайплайна, цель `seminars/NN/`) + практика
(`seminar practice N` → `practice.ipynb`, demo-ноутбук). Модель «полное зеркало»
выбрана вместо «разбора задач» из исходной формулировки.
Reference: `references/seminar_practice.md` (+ переиспользуемые `step1..step5`).

### Шаг 5.3. `/course-maker quiz N` ✅ реализовано
Пайплайн контрольной/теста: варианты, ключи, рубрика.
References: `references/quiz_plan.md`, `quiz_generate.md`, `quiz_publish.md`.

### Шаг 5.4. `/course-maker homework N`
Лёгкий вариант lab-пайплайна — без CI-сборки. Reuse `references/lab_*.md` с флагом `homework: true`.

### Шаг 5.5. `/course-maker lab triage N`
После failed validation: анализ результатов + рекомендация куда возвращаться (spec, tests, notebook).

**Критерий готовности волны 5:** Каждая команда: реализована, документирована, есть acceptance-пример.

---

## Волна 6. Качество жизни и наблюдаемость (P1+P4)

**Цель:** Защита от дрейфа состояния, видимость прогресса.

### Шаг 6.1. `scripts/validate_state.py`
Проверка COURSE_STATE.md vs реальных файлов: статусы соответствуют наличию артефактов.

### Шаг 6.2. `/course-maker doctor`
Расширенная проверка: TODO в `course_plan.md`, drift между state и реальностью, отсутствующие зависимости.

### Шаг 6.3. Compaction для `history.md`
Команда `/course-maker compact-history N` — сворачивает старые итерации в сводку, оставляет последние 5 полностью.

### Шаг 6.4. Sanity check перед `slides`
В `step4_slides.md`: добавить проверку mtime PNG > mtime figures.py. Если PNG старее — предупреждение.

### Шаг 6.5. `/course-maker stats`
Прогресс-bar по курсу: сколько лекций готово, сколько часов покрыто.

### Шаг 6.6. Lock-файл
`COURSE_STATE.md.lock` создаётся в начале команды, удаляется в конце. Защита от параллельных запусков.

**Критерий готовности волны 6:** `doctor` и `validate_state.py` ловят искусственно созданный drift.

---

## Волна 7. Альтернативные форматы (P3)

**Цель:** Снять Beamer/Jupyter монополию.

### Шаг 7.1. PowerPoint output
`/course-maker slides N --format=pptx` через python-pptx или Marp.

### Шаг 7.2. LMS-адаптеры
`profiles/<X>/lms_adapter.md` как первоклассный концепт: GitHub Classroom, Moodle, Canvas, OpenEdX, local zip.

### Шаг 7.3. Расширенные языки
Шаблоны `course_conventions_*.md` и `lab_templates_*.md` для DE, FR, ES. Fallback на английский для остальных.

### Шаг 7.4. Альтернативные среды лабораторных
R Markdown, MATLAB Live Scripts, Observable. Может быть отдельной волной — большой объём работы.

**Критерий готовности волны 7:** Преподаватель PowerPoint + Moodle может вести курс без LaTeX и GitHub.

---

## Порядок исполнения

Рекомендованный порядок:

| Очередь | Волна | Объём | Что разблокирует |
|---|---|---|---|
| 1 | Волна 1 (SKILL.md) | средний | Все последующие волны (меньше контекста, чище правила) |
| 2 | Волна 2 (bootstrap) | средний | Универсальную пригодность скила |
| 3 | Волна 3 (документация) | малый | Согласованность репозитория |
| 4 | Волна 4 (профили) | большой | Честную универсализацию + сохранение персонального слоя |
| 5 | Волна 6 (QoL) | средний | Защита от drift'а при росте использования |
| 6 | Волна 5 (новые пайплайны) | большой | Расширение функциональности |
| 7 | Волна 7 (форматы) | большой | Аудиторию вне STEM |

Волны 1–3 — можно делать подряд за день-два. Волна 4 — недельная задача (требует проектирования формата профилей). Дальше — по мере необходимости и реальных потребностей.

---

## Критерии успешности проекта в целом

1. Новый пользователь может склонировать course-maker, поставить скил, инициализировать курс и сделать первую лабораторную **без обращения к автору и без paste'а файлов из реальных лабораторий**.
2. SKILL.md занимает < 350 строк (цель поднята с 300 после появления 4-го пайплайна: 300 недостижимо без вырезания inline-CRITICAL предохранителей).
3. Все workflow'ы живут в `references/`.
4. Все критические правила собраны в одном блоке SKILL.md и помечены `NEVER`/`ALWAYS`.
5. Персональная CI / LMS / язык — отделены в `profiles/` и не блокируют generic-сценарии.
6. Каждая команда документирована в `references/`, упомянута в SKILL.md, имеет рабочий пример в `examples/`.
7. `doctor` + `validate_state.py` ловят любой drift между state и реальностью.

---

## Что НЕ делать

- Не переписывать всё разом — атомарными коммитами в порядке волн.
- Не ломать обратную совместимость текущих курсов без миграционных команд.
- Не выносить рабочие части в profiles/, пока generic-слой не покрывает их.
- Не браться за P2-P4, пока P0 не закрыты.
- Не добавлять новые языки/форматы, пока core SKILL.md не сжат.
