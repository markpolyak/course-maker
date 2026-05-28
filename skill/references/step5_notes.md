# Step 5 — Speaker Notes

## Context to gather before writing

1. `lectures/NN/plan.md` — content and timing per slide
2. `lectures/NN/slides.tex` — exact slide order and titles
   (if it exists; if not, use plan.md order)
3. `CLAUDE.md` → `## Course context` — audience, tone, language
4. `lectures/NN/history.md` — any tone or pacing feedback from previous rounds

## What speaker notes are (and are not)

**Are:** Live text the lecturer reads, adapts, and delivers aloud.
Natural spoken language, first person or direct address. Includes cues
for pacing, emphasis, and interaction with the audience.

**Are not:** A bullet-point summary of the slide. Not a formal transcript.
Not a repetition of slide content.

## Output format: `lectures/NN/speaker_notes.md`

````markdown
# Лекция N — Текст для лектора

**Общее время:** 85–90 мин

---

## Слайд 1 — [Title]

Добрый день. Сегодня мы разбираемся с тем, почему...

[*Указать на заголовок слайда. Пауза 3–5 секунд.*]

Прежде чем перейти к формулам, давайте договоримся о том, что...

**Ключевой термин** — это не просто математическое определение, это...

---

## Слайд 2 — [Title]

⏱ *Контрольная точка: ~8 мин от начала*

...

---

## Слайд N — Итоги

Итак, сегодня мы разобрали три вещи...

[*Не торопиться. Дать студентам записать.*]

На следующей лекции мы используем этот результат для...

---

## Таблица тайминга

| Блок | Слайды | Время |
|------|--------|-------|
| Вводная часть | 1–3 | 10 мин |
| ... | ... | ... |
| **Итого** | | **87 мин** |

## Что можно сократить

Если времени не хватает, слайд X можно пропустить без потери логики:
объявить, что эта тема выходит за рамки, и дать ссылку.
````

## Formatting conventions

- `[*Ремарка в скобках курсивом*]` — режиссёрская пометка:
  куда указать, какой темп, пауза, вопрос к аудитории
- `**Жирный**` — термин, который нужно выделить голосом
- `⏱ Контрольная точка` — после каждого смыслового блока
  с накопленным временем от начала
- Plain text — то, что говорить

## Tone rules (read Course context first)

- Intuition before formula: explain the meaning before showing the equation.
  "What does λ₂ tell us physically? It's the mean-square bandwidth of the
  spectrum — essentially, how spread out the signal's energy is. Now the formula:"
- Ask questions where natural: "Как вы думаете, что произойдёт если...?"
  but don't over-do it — max 1–2 per block.
- Pacing cues are not optional: at least one `[*Пауза*]` or
  `[*Дать записать*]` per complex derivation.
- Academic but alive: no "таким образом, можно заключить что" stiffness.

## Iteration handling

If the user says "too formal", "too casual", "too long for this slide":
- Fix only the affected slides
- Append to history.md what the issue was and what register was adjusted
