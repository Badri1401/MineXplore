# Metric Definitions

All residuals `r_i` are perpendicular distances from points to a locally
fitted plane. The plane is found by **singular value decomposition** of the
mean-centred point cloud inside a voxel; the last right-singular vector is
the plane normal. A voxel is retained only if (i) it contains ≥30 points,
(ii) the residual σ is within [0.1 mm, 50 cm] (rejects degenerate fits and
non-wall clutter).

| Symbol | Definition                                                | Units |
|--------|-----------------------------------------------------------|-------|
| Ra     | mean of \|r\|                                            | m     |
| Rq     | root-mean-square of r  (= σ, since r is mean-centred)     | m     |
| Rz     | 99th − 1st percentile of r  (robust peak-to-valley)       | m     |
| p95    | 95th percentile of \|r\|                                 | m     |
| λ      | spatial wavelength, from 1-D along-wall arc-length FFT    | m     |

**Voxel-scale sweep.** The `voxel_m` column is the edge length of the
cubical neighbourhood used for the plane fit. Sweeping it reveals at which
spatial scale the residuals live — this is the correct generalisation of a
"surface" metric to raw 3-D LiDAR where there is no a-priori reference face.

**Spectral wavelength analysis.** Within 5-cm-thick horizontal slabs we find
the local tangent (SVD) and cross-wall normal directions, resample the
wall-profile at uniform arc-length, FFT it, and average the magnitude
spectrum across slabs. Peaks in the resulting λ ↔ amplitude curve identify
the dominant surface-wavelength bands.

**Why these.** They match ISO 4287:1997 surface-profile conventions so
reviewers familiar with machining metrology can map our numbers onto the
literature, while remaining computable from unorganised LiDAR or a sampled
mesh without registration.
