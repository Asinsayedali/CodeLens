# Design System Reference

## Color Philosophy
The color system should have ONE strong primary color that carries the brand.
Everything else should be neutral grays that let content breathe.
Use color sparingly — it should mean something when it appears.

## Good Color Palettes for Dev Tools (fits CodeLens)

### Option A: Indigo (professional, technical)
--color-primary-500: #6366f1
--color-primary-600: #4f46e5  ← main brand color
--color-primary-700: #4338ca

### Option B: Cyan (modern, data-forward)
--color-primary-500: #06b6d4
--color-primary-600: #0891b2
--color-primary-700: #0e7490

### Option C: Violet (creative, distinctive)
--color-primary-500: #8b5cf6
--color-primary-600: #7c3aed
--color-primary-700: #6d28d9

## Neutral Scale (use for all text and surfaces)
--color-gray-50:  #f8fafc
--color-gray-100: #f1f5f9
--color-gray-200: #e2e8f0
--color-gray-300: #cbd5e1
--color-gray-400: #94a3b8
--color-gray-500: #64748b
--color-gray-600: #475569
--color-gray-700: #334155
--color-gray-800: #1e293b
--color-gray-900: #0f172a

## Semantic Color Usage
- Primary: CTAs, active states, links, focus rings
- Success (#10b981): Completed states, positive metrics
- Warning (#f59e0b): Caution states, pending items
- Error (#ef4444): Destructive actions, failed states
- Info (#3b82f6): Informational callouts

## Typography Recommendations
Heading font: 'Inter' or 'Plus Jakarta Sans' (clean, technical)
Body font: 'Inter' (consistent) or 'DM Sans' (friendly)
Mono font: 'JetBrains Mono' or 'Fira Code' (for code display — essential for CodeLens)

Load via Google Fonts or use system font stack as fallback.

## Glassmorphism (use sparingly)
For modals, cards on hero sections, or overlays:
```css
background: rgba(255, 255, 255, 0.05);
backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.1);
```
Never use glassmorphism for primary content areas — only for floating elements.

## Graph/Visualization Colors
For the architecture graph nodes, use a categorical palette:
- Module type A: #6366f1
- Module type B: #06b6d4
- Module type C: #10b981
- Module type D: #f59e0b
- Module type E: #ef4444
- Module type F: #8b5cf6
Ensure all graph colors are distinguishable for color-blind users.