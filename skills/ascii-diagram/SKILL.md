---
name: ascii-diagram
description: Use after generating or editing ASCII art, box diagrams, tables, or any monospace text art to ensure all lines, corners, and boxes are properly aligned.
user-invocable: true
---

# Validate ASCII Diagram

ASCII diagrams produced by agents frequently have alignment issues — misaligned corners, uneven borders, broken connectors. **LLMs cannot reliably count characters in their head.** This skill uses a print-and-inspect loop to catch and fix alignment bugs.

## Rules

1. **Prefer Unicode box-drawing characters.** Use `┌`, `┐`, `└`, `┘` for corners, `─` for horizontal borders, `│` for vertical borders, and `┬`, `┴`, `├`, `┤`, `┼` for junctions. Only fall back to plain ASCII (`+`, `-`, `|`) if the user explicitly requests it or the target format cannot render Unicode. **Never mix styles** in the same diagram.
2. **Every row of a box must be the exact same width** — top border, content rows, and bottom border.
3. **Pad short content lines with spaces** so the right border `│` lands in the same column on every row.
4. **Connectors and arrows** should clearly connect to the box borders they relate to. Verify gaps are intentional.
5. **No tab characters.** Tabs render at unpredictable widths and silently break alignment. Use spaces only.
6. **No trailing whitespace.** Invisible trailing spaces cause width mismatches that look correct but aren't.

## Verification procedure

**Do NOT try to validate by counting characters in your head.** Instead, use the following print-and-inspect loop:

### Step 1: Write the diagram to a temp file

Write the diagram to a temp file using the Write tool. Use a unique path like `/tmp/diagram-<context>.txt` (replace `<context>` with something specific to this session, e.g., `/tmp/diagram-auth-flow.txt`) to avoid clobbering other sessions. Use that same path in every command below.

### Step 2: Print with a column ruler

Run this Bash command to display the diagram with column numbers (replace `<path>` with your temp file path):

```bash
awk 'BEGIN{
  ruler1=""; ruler2=""
  for(i=0;i<120;i++){
    ruler1=ruler1 sprintf("%d", int(i/10)%10)
    ruler2=ruler2 sprintf("%d", i%10)
  }
  print "     " ruler1
  print "     " ruler2
}
{printf "%3d: %s\n", NR, $0}' <path>
```

This prints every line with its row number and a two-row column ruler (tens digit, ones digit) across the top, making it trivial to check whether corners, borders, and connectors land in the right columns. If your diagram is wider than 120 columns, bump the `120` in the loop.

### Step 3: Check for invisible problems

Run these checks to catch issues that are invisible in normal output (replace `<path>` with your temp file path):

```bash
# Tabs (will break alignment silently)
grep -F $'\t' <path> && echo "FAIL: tabs found" || echo "OK: no tabs"
# Trailing whitespace
grep ' $' <path> && echo "FAIL: trailing spaces found" || echo "OK: no trailing whitespace"
```

Fix any findings before proceeding.

### Step 4: Visually inspect the ruler output

Look at the printed output and check:

- **Box width consistency**: For each box, does the right border (`│` or `┐`/`┘`) appear in the same column on every row? Read the column number off the ruler.
- **Top/bottom border match**: Does the bottom corner (`└`/`┘`) sit in the same column as the top corner (`┌`/`┐`)?
- **Side-by-side alignment**: Do adjacent boxes share consistent column positions?
- **Connectors**: Do arrows actually touch the border characters?

### Step 5: Fix and repeat

If any issue is found:

1. Fix the diagram in the file where it lives (not the temp file).
2. Write the updated diagram to the same temp file again.
3. Print with the ruler again.
4. **Repeat until every check passes or you hit 3 iterations** — whichever comes first. If issues remain after 3 iterations, move on.

## Common mistakes to watch for

- **Right border off by one.** An extra or missing space before `│` shifts the right border to a different column than the top/bottom corner. Use the ruler to verify every row ends at the same column.

  ```
  WRONG:                                  CORRECT:
  ┌──────────┐                            ┌──────────┐
  │ hello    │                            │ hello    │
  │ world     │  ← col 13                 │ world    │
  └──────────┘   ← col 12                 └──────────┘
  ```

- **Bottom border width mismatch.** The bottom border has fewer or more `─` than the top, so the closing corner lands in the wrong column. Count with the ruler, not by eye.

  ```
  WRONG:                                  CORRECT:
  ┌──────────┐  ← col 12                  ┌──────────┐
  │ content  │                            │ content  │
  └─────────┘   ← col 11                  └──────────┘
  ```

- **Side-by-side boxes with ragged gap.** The gap between adjacent boxes varies across rows, causing the second box to shift. Verify that the second box's corner is in the same column on every row.

  ```
  WRONG:                                  CORRECT:
  ┌───────┐   ┌───────┐                   ┌───────┐   ┌───────┐
  │ box 1 │   │ box 2 │                   │ box 1 │   │ box 2 │
  └───────┘    └───────┘  ← extra         └───────┘   └───────┘
  ```

- **Mixed box-drawing styles.** Mixing ASCII (`+`, `-`, `|`) and Unicode (`┌`, `─`, `┐`) characters in the same diagram. Pick one style and use it consistently.

  ```
  WRONG:                                  CORRECT:
  ┌──────────+  ← ASCII +                 ┌──────────┐
  │ content  │                            │ content  │
  └──────────┘                            └──────────┘
  ```

- **Connector not touching box border.** Arrows or lines that float with a gap between them and the box they should connect to. Every connector must start and end at a border character.

  ```
  WRONG:                                  CORRECT:
  ┌───────┐     ┌───────┐                 ┌───────┐   ┌───────┐
  │ box 1 │  -> │ box 2 │                 │ box 1 │──>│ box 2 │
  └───────┘     └───────┘                 └───────┘   └───────┘
       gap ^  ^ gap                             no gaps
  ```
