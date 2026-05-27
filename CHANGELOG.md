# CHANGELOG

All notable changes to this GIS Dashboard project will be documented here.

---

# Version 1.0.0
Initial Modern GIS Dashboard Release

## Added

### GIS Core
- Kabupaten GeoJSON visualization
- Polygon hover highlight
- Polygon click interaction
- Tooltip kabupaten
- Marker lokasi client
- MiniMap support
- Fullscreen mode

### Dashboard Features
- KPI Dashboard
- Client Filter
- Commodity Filter
- Search Kabupaten
- Related Analytics
- Top 5 Commodity Analytics
- Reset Filter

### UI / UX
- Sidebar dashboard
- Floating legend
- Loading spinner
- Smooth animation
- Glassmorphism KPI card
- Dark mode support
- Responsive layout
- Sidebar toggle

### Basemap
- OpenStreetMap
- Terrain
- Light Mode
- Dark Mode

### Popup
- Modern popup UI
- Glassmorphism popup
- Commodity chip/tag
- Client chip/tag
- Dark mode popup

---

# Version 1.0.1
Dashboard Logic Improvement

## Fixed
- KPI counting issue
- Duplicate commodity issue
- Duplicate client issue
- Kabupaten active counting logic
- Sidebar overlapping legend
- Infinite loading issue
- Filter synchronization issue

## Improved
- Filter accuracy
- Polygon active state
- Sidebar animation
- Dark mode consistency

---

# Version 1.0.2
Project Structure Refactor

## Added
- External CSS structure
- External JavaScript structure
- PROJECT_CONTEXT.md
- CHANGELOG.md

## Improved
- Maintainability
- Cleaner project structure
- Easier future migration

# Version 1.0.3

## Fixed
- Popup transparency issue during PNG export
- html2canvas glassmorphism rendering issue

## Improved
- Export PNG rendering quality
- Export mode popup styling

---

# Version 1.0.4

## Fixed
- Export PNG capturing overlay issue
- "Preparing Export" popup appearing inside exported image
- Export transparency / blur issue
- Leaflet tile rendering issue during export
- Sidebar not rendering correctly in PNG export
- Floating legend not appearing consistently in export
- html2canvas capturing loading layer
- Export rendering race condition
- Leaflet canvas repaint issue before capture
- Export background transparency issue

## Improved
- PNG export rendering stability
- Leaflet redraw synchronization
- Export image sharpness
- Export loading flow
- html2canvas rendering compatibility
- Export UI state handling
- Map rendering consistency before capture
- Export performance optimization

## Added
- Leaflet invalidateSize export refresh
- Export ignoreElements configuration
- Automatic export modal hiding before capture
- Delayed tile rendering synchronization
- Export-safe CSS rendering rules
- Dedicated export rendering fixes for Leaflet layers

# Version 1.0.5

Export System Stabilization & UI Enhancement

## Fixed
- Export PNG blank / white output issue
- Export PDF rendering issue
- Infinite "Preparing Export" loading issue
- Sidebar not appearing in export result
- Floating legend not appearing in export
- Export watermark/logo missing issue
- Watermark overlapping minimap
- Export DOM rendering conflict
- html2canvas export capture inconsistency
- Watermark positioning issue
- Export loading cleanup lifecycle issue
- Duplicate export watermark CSS conflict
- Invalid nested CSS rules
- Export rendering overflow issue
- Export target mismatch issue
- Export rendering scaling inconsistency
- Export layout stretching issue
- Export sidebar positioning issue
- Export legend rendering race condition

## Improved
- Export PNG rendering stability
- Export PDF rendering stability
- Export watermark positioning
- Export UI synchronization
- Export loading flow
- html2canvas compatibility
- Export rendering performance
- Sidebar toggle animation
- Sidebar toggle positioning logic
- CSS maintainability
- Export rendering consistency
- Minimap compatibility during export
- Watermark responsiveness
- Export DOM structure stability

## Added
- Export watermark logo support
- Dynamic sidebar toggle positioning
- Automatic search reset on Clear Filter
- Export-safe watermark rendering
- Export-safe Leaflet rendering flow
- Export DOM synchronization handling
- Improved export layout structure
- Responsive export watermark positioning

## Refactor
- Cleaned duplicate #exportWatermark CSS rules
- Removed legacy export-mode styles
- Removed obsolete export button styles
- Removed duplicate popup export styles
- Simplified export rendering architecture
- Simplified watermark rendering logic
- Improved CSS organization
- Reduced redundant export rendering rules