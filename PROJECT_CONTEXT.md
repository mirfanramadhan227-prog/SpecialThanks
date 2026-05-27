# GIS Dashboard Project

## Project Name
Indonesia Client Distribution Map

---

# Main Purpose

Dashboard GIS interaktif untuk menampilkan:

- Persebaran client per kabupaten
- Persebaran commodity per kabupaten
- Analisis client & commodity
- Monitoring nasional berbasis peta

---

# Main Technology Stack

## Backend / Data Processing
- Python
- Pandas
- GeoPandas
- Folium

## Frontend
- HTML
- CSS
- JavaScript
- Leaflet.js

---

# Current Project Structure

GIS Project/
│
├── app.py
├── data.xlsx
├── PROJECT_CONTEXT.md
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── main.js
│
└── GeoJson-Indonesia-38-Provinsi/

---

# Existing Features

## GIS Features
- Kabupaten GeoJSON
- Marker lokasi client
- Polygon highlight
- Tooltip kabupaten
- Modern popup
- MiniMap
- Fullscreen mode

## Dashboard Features
- KPI Dashboard
- Related Analytics
- Top 5 Commodity
- Search Kabupaten
- Filter Client
- Filter Commodity
- Reset Filter

## UI Features
- Glassmorphism KPI
- Dark Mode
- Sidebar Toggle
- Loading Spinner
- Modern Popup UI
- Responsive Layout

---

# Current Basemap

- OpenStreetMap
- Terrain
- Light Mode
- Dark Mode

---

# Main Data Columns

## Excel Data
- kabupaten
- Client
- Commodity

## GeoJSON Data
- WADMKK

---

# Current Logic

## KPI Logic
- KPI mengikuti filter aktif
- KPI mengikuti kabupaten yang diklik

## Filter Logic
- Filter client → tampil commodity terkait
- Filter commodity → tampil client terkait

## Top Commodity Logic
- Nasional jika tidak klik kabupaten
- Per kabupaten jika polygon diklik

---

# Styling Convention

## Main Colors
- Merah muda:
  Kabupaten dengan data
- Abu:
  Kabupaten tanpa data
- Hijau:
  Marker client
- Biru:
  Polygon aktif

---

# Important Notes

- GeoJSON layer selalu aktif
- Layer checkbox polygon disembunyikan
- Basemap tetap selectable
- Sidebar dan legend independent
- CSS dipisah ke style.css
- JS dipisah ke main.js

---

# Current Development Stage

Stage:
Modern Enterprise GIS Dashboard

Next Planned Features:
- Export PDF
- Export PNG
- Flask Migration
- PostgreSQL/PostGIS
- Advanced Analytics