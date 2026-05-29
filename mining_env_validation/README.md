# Mining-Environment Texture Validation

Geometric-only validation of our MuJoCo tunnel mesh against a real
underground-mine LiDAR point cloud.

## Contents

| Path                                          | Purpose                                           |
|-----------------------------------------------|---------------------------------------------------|
| metrics/validation_matrix.csv                 | Ra / Rq / Rz / p95 sweep, both sources            |
| metrics/metric_definitions.md                 | Exact definitions + pipeline                       |
| plots/roughness_comparison.png                | Scale curve + 0.5 m ISO-4287 bars                 |
| plots/frequency_analysis.png                  | Wall-profile wavelength spectrum                  |
| plots/deviation_heatmap.png                   | Spatial σ map at robot eye height (1.75 m)        |
| paper_section/texture_validation_section.md   | LaTeX-ready ICRA subsection, cites the figures    |

## Data provenance

Real point cloud: Leung et al. Chilean-Mine LiDAR, file
`raw_bags/12M/12M/12M_lidar.dat`, first 2,000,000 points.
Simulated mesh:   `Mining Env/outputs/meshes/tunnel_inner_shell.obj`,
sampled to 3,000,000 uniform surface points.

## Reproducing

```
cd "Mining Env"
.venv/bin/python scripts/10_icra_validation.py
```

No hand-tuned numbers appear in the report — all values in
`texture_validation_section.md` are formatted from the CSV at build time.
