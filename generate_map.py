from app import build_map

# ====================================
# BUILD MAP
# ====================================

m = build_map()

# ====================================
# SAVE STATIC HTML
# ====================================

m.save("docs/index.html")

print("Static map berhasil dibuat!")