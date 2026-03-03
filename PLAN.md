# Implementation Plan

## Task 1: Equal-Height Containers
**Problem**: Side-by-side columns (feature cards, metric cards, result cards) have mismatched heights because child elements don't stretch to fill their column.

**Solution**: Strengthen the CSS in `theme.py` to force all children inside horizontal blocks to fill height. Add `height: 100%` to all card CSS classes (`.feature-card`, `.glass-card`, `.tactical-panel`, `.metric-card`, `.result-card`). Also add a targeted rule for Streamlit's inner column wrapper divs.

**Files**: `dashboard/theme.py`, `dashboard/components.py`

---

## Task 2: Custom Sidebar Restyle
**Problem**: Sidebar uses Streamlit's default navigation (plain list with emoji icons). Needs a proper SOC-style sidebar with styled nav items, amber active states, better spacing, brand section at bottom.

**Solution**: Heavy CSS overrides targeting Streamlit's sidebar `data-testid` selectors:
- Style `[data-testid="stSidebarNav"]` nav links — amber left border on active, hover highlight, uppercase labels, Space Grotesk font
- Move branding to bottom of sidebar
- Add amber accent borders and tactical styling to sidebar sections
- Style sidebar headings, dividers, selectboxes, sliders, buttons
- Ensure collapse toggle is styled

**Files**: `dashboard/theme.py` (CSS), `dashboard/theme.py:inject_sidebar_brand()` (HTML structure)

---

## Task 3: Localization (en.json)
**Problem**: All ~450+ UI strings are hardcoded in Python. Need i18n infrastructure so user can add `tk.json` for Turkmen.

**Solution**:
1. Create `dashboard/locales/en.json` with all user-facing strings organized by page
2. Create `dashboard/i18n.py` helper module: `load_locale(lang)` and `t(key)` function that reads from session state
3. Add language selector to Settings page (EN / TK)
4. Replace all hardcoded strings in all 8 Python files with `t("key")` calls

**Structure of en.json**:
```json
{
  "common": { "footer", "brand_title", "brand_subtitle", ... },
  "home": { "hero_title", "hero_subtitle", "system_capabilities", ... },
  "live_monitor": { "page_title", "start_monitoring", ... },
  "pcap": { ... },
  "attack_details": { ... },
  "history": { ... },
  "settings": { ... },
  "how_it_works": { ... }
}
```

**Files**:
- NEW: `dashboard/locales/en.json`
- NEW: `dashboard/i18n.py`
- EDIT: All 8 existing dashboard Python files to use `t()` calls
