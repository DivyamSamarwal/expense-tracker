# Theme notes — Golden & Black

This file documents the theme variables used by the app and how to change them.

Location
- Primary variables live in `static/css/style.css` (defined under the `:root { ... }` block).

Key CSS variables
- `--bg-color` — overall page background (deep black). Default: `#070707`
- `--panel-bg` — card/panel background. Default: `#0f0f0f`
- `--accent-gold` — main gold accent used for buttons, badges, and brand. Default: `#d4af37`
- `--muted-gold` — hover/secondary gold color. Default: `#bfa75a`
- `--text-color` — primary text color (off-white / golden tint). Default: `#f7f1e1`
- `--muted-text` — secondary text color. Default: `#cfc6ad`

How to tweak colors
1. Open `static/css/style.css` and find the `:root { ... }` block near the top.
2. Replace the hex values with your preferred colors. Example (brighter gold):

```css
:root {
  --accent-gold: #ffd700; /* vivid gold */
  --muted-gold: #e6c85a;
}
```

Notes and tips
- The site uses `navbar-dark` + custom overrides so text contrasts correctly. If you change the background to a much lighter color, update `layout.html` to use `navbar-light` and adjust text colors accordingly.
- Buttons use `--accent-gold`. If you want a metallic look, consider using a subtle gradient for `.btn-primary` instead of a flat color.
- Chart colors live in `static/js/chart.js` — change `backgroundColors` array to match your theme if you want category slices to align with gold/black palette.
- Currency presentation uses the `inr` Jinja filter (in `app.py`) and the chart tooltip uses `9` (rupee). If you change currency symbol or want to support multiple locales, consider adding `Flask-Babel`.

If you'd like, I can:
- Provide a light-theme variant file and a theme-toggle switch.
- Replace color literals in JS chart palette with CSS-driven values so colors come from CSS variables.
