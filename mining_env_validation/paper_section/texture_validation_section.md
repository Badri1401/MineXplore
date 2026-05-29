## Surface-Texture Validation against Real Underground LiDAR

We validate the geometric fidelity of the simulated tunnel wall against the
Leung et al. 3-D LiDAR point cloud of an operational Chilean underground
mine. Validation is strictly **geometric**: only the surface-residual
statistics and wavelength spectrum of the walls are compared — visual
appearance, texture maps, and photometric properties are out of scope.

### Methodology

Both the real point cloud and a uniform resample of the simulated wall mesh
are restricted to the traversable height band z ∈ [0.5, 3.0] m.
Over a sweep of plane-fit window sizes w ∈ {0.10, 0.15, 0.20, 0.30, 0.50, 1.00, 2.00} m,
each w-sized voxel is fitted with a principal plane (SVD), and the
perpendicular residuals r_i are aggregated into ISO 4287-style metrics:
Ra (mean |r|), Rq (rms), Rz (p99−p1 peak-to-valley), p95. A 1-D along-wall
wavelength spectrum is obtained by extracting horizontal wall profiles in
5-cm-thick slabs, arc-length-resampling, and averaging FFT magnitudes.

### Results

At w = 0.50 m the real LiDAR reports Ra = 3.01 cm,
Rq = 5.15 cm, Rz = 33.56 cm,
p95 = 12.02 cm (over 1,342 valid patches,
554,034 residual samples). The simulated mesh at the same
window reports Ra = 1.22 cm, Rq = 1.78 cm,
Rz = 9.85 cm, p95 = 3.65 cm
(27,044 patches). Full scale sweep is in
Table \ref{tab:valid_matrix}.

The simulated surface therefore recovers 41 % of the real
roughness magnitude at the half-metre scale — an *under-shoot* rather than
over-shoot, which is intentional: simulation amplitudes are clipped at 10 %
of the local junction width so that narrow passages cannot pinch shut.
The wavelength spectrum (Fig. \ref{fig:freq}) shows coincident peaks in
the 5–20 cm band, confirming that simulated roughness populates the same
spatial-frequency band as the real walls.

The deviation heat-map at robot eye-height z = 1.75 m (Fig. \ref{fig:dev})
shows that simulated residuals are spatially stationary whereas real-mine
residuals are spatially heterogeneous — a known limitation to be addressed
by per-region amplitude modulation in future work.

### Honesty caveats

(i) The comparison is in mesh-sample space, not sensor-return space; the
LiDAR ray-path and range-noise distribution are not simulated here.
(ii) The real cloud is from a single mine site; the sim is not a
per-site digital twin, only a geometry matched at the aggregate-statistics
level. (iii) Absolute magnitudes under-shoot real by a factor of
2.46×; a controlled study of the displacement-amplitude vs.
navigability trade-off is left as future work.
