# UI Completion Checklist

Run through every item before marking the UI as done.

## Design Consistency
- [ ] One font family for headings, one for body
- [ ] No hardcoded hex/rgb colors in component files
- [ ] All spacing uses the defined scale (multiples of 4px)
- [ ] Icons are all from the same library, same size conventions
- [ ] Border radius is consistent per element type (cards always lg, buttons always md, etc.)
- [ ] Shadows are consistent — no mixing of sharp and soft shadows

## States Coverage
- [ ] Every button has hover, active, focus-visible, disabled states
- [ ] Every input has focus, error, disabled states
- [ ] Every page has a loading state (skeleton preferred)
- [ ] Every list/table has an empty state with helpful message + CTA
- [ ] Every async action has an error state with retry option

## Responsiveness
- [ ] Tested at 375px (mobile)
- [ ] Tested at 768px (tablet)
- [ ] Tested at 1280px (desktop)
- [ ] No horizontal scroll at any breakpoint
- [ ] Navigation collapses properly on mobile
- [ ] Tables are scrollable horizontally on mobile
- [ ] Touch targets are minimum 44x44px on mobile

## Accessibility
- [ ] All images have alt attributes
- [ ] All form inputs have visible labels (not just placeholders)
- [ ] Focus order is logical (tab through the page)
- [ ] Focus rings are visible on all interactive elements
- [ ] Color is not the only way to convey information
- [ ] Contrast ratio is 4.5:1 minimum for body text

## Dark Mode
- [ ] All components tested in dark mode
- [ ] No white backgrounds hardcoded (use var(--color-surface))
- [ ] Code blocks readable in dark mode
- [ ] Graph/chart colors work in dark mode
- [ ] Toggle persists across page refresh

## Performance
- [ ] No unnecessary re-renders (check with React DevTools)
- [ ] Images are lazy loaded
- [ ] Heavy components (graph visualization) are lazy imported
- [ ] Animations use transform/opacity only (not width/height)

## CodeLens Specific
- [ ] Repo architecture graph is interactive (click nodes, zoom, pan)
- [ ] Code snippets use monospace font with syntax highlighting
- [ ] Tech debt severity uses consistent color coding (red/yellow/green)
- [ ] Q&A interface shows clear loading indicator while fetching
- [ ] Onboarding docs rendered as proper markdown (not raw text)
- [ ] File paths displayed in monospace with truncation on overflow