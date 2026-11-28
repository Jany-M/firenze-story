# 3D scans

Reduced meshes of 3D scans, made by `blender/scripts/prep_scan.py` and placed in the landmark models by
`blender/scripts/landmark_scan.py`. Each file keeps its source's licence; the parts of the GLBs built from it are shared
under the same terms. Register: `docs/DATA-SOURCES.md`.

| File | Work | Source | Licence | Changes |
|---|---|---|---|---|
| `david_stw.npz` | Michelangelo's David (marble, 1501–04, Galleria dell'Accademia) | Scan the World @ MyMiniFactory.com, "Michelangelo's David" – https://www.myminifactory.com/object/3d-print-michelangelo-s-david-in-florence-italy-2052 | CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/) | reduced from 1,199,884 to 24,000 triangles, moved to stand on its base at the origin, scaled to height 1 |

The original STL files stay out of the repository (`_dev/references/`).
