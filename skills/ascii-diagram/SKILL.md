---
name: ascii-diagram
description: Use after generating or editing ASCII art, box diagrams, tables, or any monospace text art to ensure all lines, corners, and boxes are properly aligned.
user-invocable: true
---

# Validate ASCII Diagram

ASCII diagrams produced by agents frequently have alignment issues — misaligned corners, uneven borders, broken connectors. **LLMs cannot reliably count characters in their head.** This skill uses a print-and-inspect loop to catch and fix alignment bugs.

## Rules

1. **One style only.** Either plain ASCII (`+`, `-`, `|`) or Unicode (`┌`, `─`, `┐`, `│`, `└`, `┘`). Never mix.
2. **Every row of a box must be the exact same width** — top border, content rows, and bottom border.
3. **Pad short content lines with spaces** so the right border `|` lands in the same column on every row.
4. **Connectors and arrows** should clearly connect to the box borders they relate to. Verify gaps are intentional.
5. **No tab characters.** Tabs render at unpredictable widths and silently break alignment. Use spaces only.
6. **No trailing whitespace.** Invisible trailing spaces cause width mismatches that look correct but aren't.

## Verification procedure

**Do NOT try to validate by counting characters in your head.** Instead, use the following print-and-inspect loop:

### Step 1: Write the diagram to a temp file

Write the diagram to a temp file using the Write tool. Use a unique path (e.g., `/tmp/diagram-<context>.txt`) to avoid clobbering other sessions.

### Step 2: Print with a column ruler

Run this Bash command to display the diagram with column numbers:

```bash
awk 'BEGIN{
  ruler1=""; ruler2=""
  for(i=0;i<120;i++){
    ruler1=ruler1 sprintf("%d", int(i/10)%10)
    ruler2=ruler2 sprintf("%d", i%10)
  }
  print "     " ruler1
  print "     " ruler2
  print "     " "----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8----+----9----+----0----+----1----+----2"
}
{printf "%3d: %s\n", NR, $0}' /tmp/diagram-UNIQUE.txt
```

This prints every line with its row number and a column ruler across the top, making it trivial to check whether corners, borders, and connectors land in the right columns.

### Step 3: Check for invisible problems

Run these checks to catch issues that are invisible in normal output:

```bash
# Tabs (will break alignment silently)
grep -P '\t' /tmp/diagram-UNIQUE.txt && echo "FAIL: tabs found" || echo "OK: no tabs"
# Trailing whitespace
grep -P ' +$' /tmp/diagram-UNIQUE.txt && echo "FAIL: trailing spaces found" || echo "OK: no trailing whitespace"
```

Fix any findings before proceeding.

### Step 4: Visually inspect the ruler output

Look at the printed output and check:
- **Box width consistency**: For each box, does the right border (`|` or `+`) appear in the same column on every row? Read the column number off the ruler.
- **Top/bottom border match**: Does the bottom `+` sit in the same column as the top `+`?
- **Side-by-side alignment**: Do adjacent boxes share consistent column positions?
- **Connectors**: Do arrows actually touch the border characters?

### Step 5: Fix and repeat

If any issue is found:
1. Fix the diagram in the file where it lives (not the temp file).
2. Write the updated diagram to `/tmp/diagram-UNIQUE.txt` again.
3. Print with the ruler again.
4. **Repeat until every check passes.** Expect 2–3 iterations.

## Common mistakes to watch for

- **Right border off by one.** An extra or missing space before `|` shifts the right border to a different column than the top/bottom `+`. Use the ruler to verify every row ends at the same column.
  ```
  +----------+
  | hello    |
  | world     |
  +----------+
  ```

- **Bottom border width mismatch.** The bottom border has fewer or more dashes than the top, so the closing `+` lands in the wrong column. Count dashes with the ruler, not by eye.
  ```
  +----------+
  | content  |
  +---------+
  ```

- **Side-by-side boxes with ragged gap.** The gap between adjacent boxes varies across rows, causing the second box to shift. Verify that the second box's `+` is in the same column on every row.
  ```
  +-------+   +-------+
  | box 1 |   | box 2 |
  +-------+    +-------+
  ```

- **Mixed box-drawing styles.** Mixing ASCII (`+`, `-`, `|`) and Unicode (`┌`, `─`, `┐`) characters in the same diagram. Pick one style and use it consistently.
  ```
  ┌──────────+
  │ content  │
  └──────────┘
  ```

- **Connectors with ambiguous gaps.** Arrows or connectors that float between boxes without clearly touching either border. Verify that connectors are intentional and visually unambiguous.
  ```
  +-------+    +-------+
  | box 1 | -> | box 2 |
  +-------+    +-------+
  ```
