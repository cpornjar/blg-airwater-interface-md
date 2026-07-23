Generate or review a data figure to real publication standard — grounded in the user's own accepted ChemPhysChem figures, not generic advice. Acts as the project's figure-quality role: do not skip the verification step even under time pressure.

Arguments: $ARGUMENTS — one of:
- A description of what to plot + the analysis data source (e.g. `plot Rg vs time from results/analysis/blg_rg_CENTER.npz`)
- `review <path-to-existing-figure.png>` — audit an existing figure against the checklist below without regenerating anything, report findings only

## Ground truth: the user's own accepted figure

Before generating or reviewing anything, if you have not already seen it this session, read:
`/Users/mac2022-1/Computational_Study_of_Carbon_Dioxide_Capture_by_Tertiary_Amines.pdf.pdf`
(Pornjariyawatch et al., *ChemPhysChem* 2024 — real, accepted, published. If this exact path
has moved, ask the user where their reference paper now lives rather than guessing or
skipping this step — it is the standard, not optional reading.)

What that paper's figures actually do, confirmed by direct inspection (Figures 3, 4, 6):
- Bar charts: **one solid color**, no gradient, no pattern fill, categories identified by
  x-axis tick labels, never a legend when direct labeling works
- Scatter/line plots: one color per genuine data series (e.g. 4 temperatures, 3 model
  complexities) — never more colors than there are real categories
- **Zero boxed/bordered annotations anywhere.** The one exception (Fig. 4a) is a plain,
  unboxed regression equation + R² sitting in genuinely empty white space
- **No grid lines**, no in-figure titles — the external caption carries the title and all
  detailed numbers
- Panel letters (a), (b), (c)... referenced in the multi-part caption
- Legends appear only where categories cannot be told apart by position (Fig. 6a, three
  overlapping series) — this is a data-driven judgment call, not a blanket ban

## Step 1 — Confirm the data source

Never fabricate or approximate a number. Identify the exact `.npz`/`.csv`/cached-result file
the figure will be built from. If it doesn't exist yet, say so and stop — don't invent
plausible-looking data.

## Step 2 — Apply the shared style, additively

Use `scripts/plot_style.py` (`from plot_style import apply_style, COLORS, ...; apply_style()`).
If a genuinely new color role is needed (a semantic meaning that doesn't already exist in
`COLORS`), **add a new key — never redefine an existing one.** Other scripts in this repo
depend on the current values; changing them silently breaks already-committed figures.

## Step 3 — The checklist (apply while writing the plotting code)

- [ ] No `fig.suptitle()` / `ax.set_title()` — the destination (LaTeX caption, slide header,
      report caption) owns the title. Exception: none.
- [ ] **One color = one meaning across the entire figure SET being produced together**, not
      just within one panel. If replica/run identity already has a color family in this
      figure set, DSSP/composition/reference-marker colors must come from a different family
      — check `COLORS` for keys already in use by sibling figures before picking one.
  If no existing role fits, extend `COLORS` (see below) rather than reusing a hue that
  already means something else nearby.
- [ ] No bordered/boxed text annotation sitting on top of data. A plain, unboxed label is
      allowed only in a position you've *checked* is empty (read the actual data range —
      don't eyeball it) — detailed stats belong in the caption, not stamped on the plot.
- [ ] Legend only if you've checked that direct/positional labeling would actually collide
      (e.g. compare terminal values of overlapping series — see the SASA-endpoint check
      example: three replicas landed within 0.6 nm² of each other, so a legend was the
      correct call there, confirmed by checking the numbers, not assumed).
- [ ] No grid lines (`axes.grid: False` — already set by `apply_style()`, don't override it).
- [ ] Panel letters small, bold, in the corner — not narrated again in a boxed title.
- [ ] Math notation: if using `\langle ... \rangle` or any LaTeX macro, sanity-check the
      rendered output actually shows what you intended — empty `\langle\rangle` silently
      renders as `()`, and this exact bug has shipped before.

## Step 4 — Mandatory visual verification (do not skip)

Generate the figure, then **use the Read tool on the actual rendered PNG** and check it
against Step 3's list one item at a time. Code review is not enough — every bug this
checklist exists to prevent (title collision, clipped annotation text, color reuse,
overlapping legend, broken math notation) was invisible in the source and only caught by
looking at the rendered image. If anything fails, fix and re-render before reporting done.

## Step 5 — Know which destination you're building for

- **Paper / slide deck / internal report figure**: full quality, no size constraint, PNG
  @300dpi + PDF, goes in `results/figures/pubready/` (or ask if a different location is
  intended) — this is what Steps 1–4 above produce.
- **IFSC2026 abstract figure**: a *separate*, deliberately compressed pass — one A4 page for
  the whole abstract, each figure ≤200 KB, `.jpg`/`.png`/`.tif` only (see
  `progress-reports/Abstract_17th-IFSC_2026_Template.docx`). Do not assume a pubready figure
  can be reused directly for this — check the file size and format before offering it.

If it's unclear which destination is needed, ask rather than guessing.

## Rules

- Never fabricate or approximate a data value — load from the real cached result file
- Never edit an existing key in `scripts/plot_style.py`'s `COLORS` dict — additive only
- Never overwrite `results/figures/paper/` (finalized, referenced by `main.tex`) — new
  publication-quality work goes to `results/figures/pubready/` or a clearly new subfolder
- Always regenerate and re-view the PNG after any code edit — a diff alone is not
  verification
- If reviewing an existing figure (`review` mode), report findings only — do not
  regenerate/modify anything unless asked
