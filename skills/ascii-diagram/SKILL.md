---
name: ascii-diagram
description: Validate and fix alignment issues in ASCII diagrams. Use after generating or editing ASCII art, box diagrams, tables, or any monospace text art to ensure all lines, corners, and boxes are properly aligned.
user-invocable: true
---

# Validate ASCII Diagram

ASCII diagrams produced by agents frequently have alignment issues — misaligned corners, uneven borders, broken connectors. This skill validates and fixes them.

## How to draw correct ASCII diagrams

When creating or fixing diagrams, follow these rules strictly:

1. **Pick one style and stick to it.** Either plain ASCII (`+`, `-`, `|`) or Unicode box-drawing (`┌`, `─`, `┐`, `│`, `└`, `┘`). Never mix them.

2. **Plan the grid before drawing.** Before writing any characters:
   - Determine the content of every box (longest line sets the box width)
   - Add padding: box width = longest content line + 2 spaces (1 left pad + 1 right pad)
   - Border width = content width + 2 (for the left and right border characters)
   - Write down the column positions where each box starts and ends

3. **Every row of a box must be the exact same length.** Count characters explicitly:
   ```
   +------------+    ← top border: 14 chars
   | content    |    ← content row: 14 chars (padded with spaces)
   | more stuff |    ← content row: 14 chars (padded with spaces)
   +------------+    ← bottom border: 14 chars (must match top)
   ```

4. **Corners must connect.** Every `+` (or `┌┐└┘`) must have:
   - A `-` (or `─`) adjacent horizontally on the sides that have borders
   - A `|` (or `│`) adjacent vertically on the sides that have borders

5. **Side-by-side boxes** must use consistent spacing between them:
   ```
   +-------+     +-------+
   | box 1 |     | box 2 |
   +-------+     +-------+
       ↑ same gap ↑
   ```

6. **Connectors and arrows** (`-->`, `<--`, `←`, `→`, `|`, `↓`, `↑`) must touch the box border they connect to. No floating arrows.

## Validation procedure

After drawing or finding a diagram, validate it by performing these checks:

### Step 1: Identify all boxes
For each box, record:
- Top-left corner position (row, column)
- Width (number of characters from left border to right border, inclusive)
- Height (number of rows from top border to bottom border, inclusive)

### Step 2: Check border consistency
For each box:
- Count the top border width (e.g., `+----+` = 6 chars)
- Count the bottom border width — must equal top border width exactly
- For every content row, verify: left border char at same column as top-left corner, right border char at same column as top-right corner

### Step 3: Check corner connections
For each corner character:
- Verify it has the correct adjacent characters (horizontal border on horizontal sides, vertical border on vertical sides)

### Step 4: Check connectors
For each arrow or line connecting boxes:
- Verify it starts at a box border and ends at a box border
- Verify the line is straight (all characters on the same row or same column)

### Step 5: Fix and re-validate
If any check fails:
1. Redraw the broken box(es) by recalculating widths from content
2. Re-validate from Step 1
3. Repeat until all checks pass

## Common mistakes to watch for

- **Off-by-one on right border**: The `|` or `+` on the right side is one column too far left or right
- **Forgetting to pad short lines**: Content lines shorter than the longest line must be space-padded to match
- **Inconsistent gap between side-by-side boxes**: Use the same number of spaces between all adjacent boxes
- **Dangling connectors**: Arrows that don't reach the box border
- **Mixed character styles**: Using `+` corners with `─` horizontal lines, or `┌` corners with `-` lines
