"""
06b_build_jagged_v2.py — higher-fidelity tunnel shell + ceiling

Goals vs v1 (scripts/06_build_jagged_inner_shell.py):
  * AMP 0.11 → 0.18 m (still inside 10% safety clip of 2 m local width)
  * Add mid-wavelength 40 cm octave → lifts roughness-scale integral
    and shifts dominant λ toward the real-scan 1.0–1.5 m band
  * Add large-scale amplitude modulation (30 m envelope) → spatial
    heterogeneity across the tunnel
  * Ceiling: 3-octave noise + stronger bulge variability (0.20 m)
  * Write v2 OBJs IN-PLACE over the standard filenames so XML stays valid
"""
import json, math, os
import numpy as np
from shapely.geometry import Polygon, Point, MultiPoint
from shapely.ops import triangulate

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_DIR    = os.path.dirname(SCRIPT_DIR)
GEOJSON    = os.path.join(ENV_DIR, "outputs", "tunnel.geojson")
OUT_WALLS  = os.path.join(ENV_DIR, "outputs", "meshes", "tunnel_inner_shell.obj")
OUT_CEIL   = os.path.join(ENV_DIR, "outputs", "meshes", "tunnel_ceiling_mesh.obj")

WALL_HEIGHT   = 3.5
EDGE_SEG      = 0.35          # finer densification than v1 (0.5 m → 0.35 m)
Z_LAYERS      = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.5]
AMP           = 0.28          # ±28 cm (needs loosened safety clip below)
LAMBDA_MAIN   = 0.15
LAMBDA_MID    = 0.40          # 40 cm octave
LAMBDA_DETAIL = 0.05
LAMBDA_LARGE  = 1.50          # 1.5 m octave → populates the 1 m band
CEIL_BULGE    = 0.45          # ceiling vault sags 45 cm at center
CEIL_AMP_MUL  = 3.00          # ceiling noise 3× wall amplitude (real cave ceilings are rougher)
WALL_TILT_DEG = 1.25
CEILING_GRID  = 1.5           # finer ceiling grid

# Strong spatial modulation — AMP scales by (0.3 … 1.7) across space
MOD_LAMBDA    = 25.0
MOD_STRENGTH  = 0.70

SAFETY_CLIP_FRAC = 0.15   # relaxed from 0.10 — still prevents junction pinch

rng = np.random.default_rng(42)


def mod_envelope(x, y):
    """0.6..1.4 multiplicative envelope — makes roughness spatially heterogeneous."""
    k = 2 * math.pi / MOD_LAMBDA
    e = (math.sin(k * (0.7 * x + 0.8 * y) + 0.5)
         + math.sin(k * (-0.5 * x + 0.9 * y) + 2.1)) / 2.0
    return 1.0 + MOD_STRENGTH * e


def fbm(x, y, z):
    """4-octave deterministic fBm, sum in roughly [-1, +1]."""
    k1 = 2 * math.pi / LAMBDA_LARGE   # w=0.45
    k2 = 2 * math.pi / LAMBDA_MID     # w=0.30
    k3 = 2 * math.pi / LAMBDA_MAIN    # w=0.35
    k4 = 2 * math.pi / LAMBDA_DETAIL  # w=0.18
    n = (
        0.45 * math.sin(k1 * (0.80 * x + 0.55 * y + 0.25 * z))
      + 0.45 * math.sin(k1 * (-0.45 * x + 0.88 * y + 0.30 * z) + 0.8)
      + 0.30 * math.sin(k2 * (0.91 * x + 0.42 * y + 0.30 * z))
      + 0.30 * math.sin(k2 * (-0.38 * x + 0.92 * y + 0.55 * z) + 1.3)
      + 0.35 * math.sin(k3 * (0.71 * x - 0.71 * y + 1.10 * z) + 2.1)
      + 0.35 * math.sin(k3 * (0.55 * x + 0.83 * y - 0.70 * z) + 0.7)
      + 0.18 * math.sin(k4 * (0.60 * x - 0.80 * y + 0.50 * z) + 3.1)
      + 0.18 * math.sin(k4 * (-0.71 * x + 0.71 * y + 0.40 * z) + 1.9)
    )
    # amplitude sum = 2.56; divide to keep peak roughly ≤ 1
    return n / 2.56


with open(GEOJSON) as f:
    data = json.load(f)
coords = data["features"][0]["geometry"]["coordinates"]
exterior_ring = coords[0]
hole_rings    = coords[1:]
shapely_poly  = Polygon(exterior_ring, holes=hole_rings)
print(f"Polygon: ext={len(exterior_ring)} verts, holes={len(hole_rings)}, area={shapely_poly.area:.0f} m²")


def densify_ring(ring, seg_len):
    out = []
    for i in range(len(ring) - 1):
        x0, y0 = ring[i]; x1, y1 = ring[i + 1]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        n = max(1, int(math.ceil(L / seg_len)))
        for k in range(n):
            t = k / n
            out.append((x0 + t * dx, y0 + t * dy))
    out.append(out[0])
    return out


def safety_clip(amp_req, local_w):
    mx = SAFETY_CLIP_FRAC * local_w
    return max(-mx, min(mx, amp_req))


wall_vertices, wall_normals, wall_faces = [], [], []
ceil_vertices, ceil_normals, ceil_faces = [], [], []
vertices, normals, faces = wall_vertices, wall_normals, wall_faces

tilt_rad = math.radians(WALL_TILT_DEG)
tilt_per_m = math.tan(tilt_rad)


def add_jagged_wall(ring_closed, invert_normal):
    ring = densify_ring(ring_closed, EDGE_SEG)
    n = len(ring) - 1
    edge_normals = []
    for i in range(n):
        x0, y0 = ring[i]; x1, y1 = ring[i + 1]
        dx, dy = x1 - x0, y1 - y0
        L = max(math.hypot(dx, dy), 1e-9)
        nx, ny = -dy / L, dx / L
        if invert_normal: nx, ny = -nx, -ny
        edge_normals.append((nx, ny))

    vert_normals = []
    for i in range(n):
        nA = edge_normals[(i - 1) % n]; nB = edge_normals[i]
        nx = nA[0] + nB[0]; ny = nA[1] + nB[1]
        L = max(math.hypot(nx, ny), 1e-9)
        vert_normals.append((nx / L, ny / L))

    def local_width(x, y): return 2.0

    grid = np.empty((n, len(Z_LAYERS), 3), dtype=np.float64)
    for i in range(n):
        x, y = ring[i]; nx, ny = vert_normals[i]
        env = mod_envelope(x, y)
        for zi, z in enumerate(Z_LAYERS):
            noise = fbm(x, y, z) * AMP * env
            tilt_off = -z * tilt_per_m
            disp = safety_clip(noise + tilt_off, local_width(x, y))
            grid[i, zi, 0] = x + nx * disp
            grid[i, zi, 1] = y + ny * disp
            grid[i, zi, 2] = z

    base = len(vertices) + 1
    flat = {}
    for i in range(n):
        for zi in range(len(Z_LAYERS)):
            v = grid[i, zi]
            vertices.append((v[0], v[1], v[2]))
            nx, ny = vert_normals[i]
            normals.append((nx, ny, 0.0))
            flat[(i, zi)] = len(vertices)

    for i in range(n):
        ii = (i + 1) % n
        for zi in range(len(Z_LAYERS) - 1):
            v00 = flat[(i, zi)]; v01 = flat[(i, zi + 1)]
            v10 = flat[(ii, zi)]; v11 = flat[(ii, zi + 1)]
            if not invert_normal:
                faces.append((v00, v01, v11))
                faces.append((v00, v11, v10))
            else:
                faces.append((v00, v10, v11))
                faces.append((v00, v11, v01))


add_jagged_wall(exterior_ring, invert_normal=False)
for hole in hole_rings:
    add_jagged_wall(hole, invert_normal=True)
print(f"Walls: {len(vertices)} verts, {len(faces)} tris")


# ── Ceiling ──
ext_dense = densify_ring(exterior_ring, EDGE_SEG * 2)
seed_pts = [(p[0], p[1]) for p in ext_dense[:-1]]
for hole in hole_rings:
    hd = densify_ring(hole, EDGE_SEG * 2)
    seed_pts.extend((p[0], p[1]) for p in hd[:-1])

minx, miny, maxx, maxy = shapely_poly.bounds
gx = np.arange(minx, maxx, CEILING_GRID)
gy = np.arange(miny, maxy, CEILING_GRID)
interior = []
for x in gx:
    for y in gy:
        if shapely_poly.contains(Point(x, y)):
            interior.append((x, y))
seed_pts.extend(interior)
print(f"Ceiling seeds: {len(seed_pts)} (boundary + {len(interior)} interior)")

mp = MultiPoint(seed_pts)
tris = triangulate(mp)
kept = [t for t in tris if shapely_poly.contains(t.centroid)]
print(f"Ceiling triangles kept: {len(kept)}")

boundary_geom = shapely_poly.boundary

def ceiling_z(x, y):
    d_edge = Point(x, y).distance(boundary_geom)
    # stronger bulge with per-site variability
    bulge_norm = math.tanh(d_edge / 3.0)
    bulge_var = 1.0 + 0.35 * math.sin(0.15 * x + 0.11 * y)
    bulge = CEIL_BULGE * bulge_norm * bulge_var
    env = mod_envelope(x, y)
    noise = fbm(x, y, WALL_HEIGHT) * AMP * CEIL_AMP_MUL * env
    return WALL_HEIGHT - bulge + noise


ceil_cache = {}
def get_ceiling_vert(x, y):
    key = (round(x, 5), round(y, 5))
    if key in ceil_cache: return ceil_cache[key]
    z = ceiling_z(x, y)
    ceil_vertices.append((x, y, z))
    ceil_normals.append((0.0, 0.0, -1.0))
    idx = len(ceil_vertices)
    ceil_cache[key] = idx
    return idx

for tri in kept:
    xs, ys = tri.exterior.coords.xy
    v0 = get_ceiling_vert(xs[0], ys[0])
    v1 = get_ceiling_vert(xs[1], ys[1])
    v2 = get_ceiling_vert(xs[2], ys[2])
    ax, ay, _ = ceil_vertices[v0 - 1]
    bx, by, _ = ceil_vertices[v1 - 1]
    cx, cy, _ = ceil_vertices[v2 - 1]
    signed = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    if signed > 0: v1, v2 = v2, v1
    ceil_faces.append((v0, v1, v2))

print(f"Ceiling: {len(ceil_vertices)} verts, {len(ceil_faces)} tris")


def write_obj(path, verts, norms, tris, header):
    with open(path, "w") as f:
        f.write(header + "\n")
        for v in verts: f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        f.write("\n")
        for nr in norms: f.write(f"vn {nr[0]:.6f} {nr[1]:.6f} {nr[2]:.6f}\n")
        f.write("\n")
        for tri in tris:
            a, b, c = tri
            f.write(f"f {a}//{a} {b}//{b} {c}//{c}\n")


params = (f"# v2  amp=±{AMP*100:.0f}cm  lambdas={LAMBDA_LARGE*100:.0f}+"
          f"{LAMBDA_MID*100:.0f}+{LAMBDA_MAIN*100:.0f}+{LAMBDA_DETAIL*100:.0f}cm  "
          f"ceil_bulge={CEIL_BULGE*100:.0f}cm  mod_env=[{1-MOD_STRENGTH:.2f},{1+MOD_STRENGTH:.2f}]")

write_obj(OUT_WALLS, wall_vertices, wall_normals, wall_faces,
          "# tunnel_inner_shell.obj — JAGGED v2 walls\n"
          "# Generated by 06b_build_jagged_v2.py\n" + params)
write_obj(OUT_CEIL, ceil_vertices, ceil_normals, ceil_faces,
          "# tunnel_ceiling_mesh.obj — JAGGED v2 ceiling\n"
          "# Generated by 06b_build_jagged_v2.py\n" + params)

print(f"\nWalls   → {OUT_WALLS}  ({os.path.getsize(OUT_WALLS)/1024:.0f} KB)")
print(f"Ceiling → {OUT_CEIL}  ({os.path.getsize(OUT_CEIL)/1024:.0f} KB)")
print("\nDone.")
