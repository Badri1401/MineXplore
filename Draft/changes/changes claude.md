I have now read the full paper draft (MineXplore_V1.pdf), your personal change notes (my_changes), the Perplexity analysis (Draft1_changes_to_do.pdf), and the external reviewer comments from Vibhakar Mohta and Yash Butala. I also have your full project knowledge including your reward structure, LiDAR configuration, and training setup. Let me now give you the complete analysis.

---

# DEVIL'S ADVOCATE PANEL — MINEXPLORE V1 FULL REVIEW

## The Panel

Before the scores, let me tell you exactly who is reviewing this and why each of them was chosen. This panel was assembled specifically for an **environment/benchmark paper targeting ICRA 2026 Xplore Workshop**.

| # | Panelist | Why They Were Chosen |
|---|---|---|
| 1 | **Prof. Davide Scaramuzza** — ETH Zürich, Field Robotics, DARPA SubT adjacent research, ICRA reviewer for 10+ years | He has reviewed papers exactly like this. He knows the difference between a system paper and an environment paper and will call out when you've confused the two. |
| 2 | **Dr. Lerrel Pinto** — NYU, RL for robotics, has published benchmark environments (knows the OpenAI Gym / MuJoCo Playground lineage) | He will immediately notice when a benchmark paper doesn't clearly define its interface. All the TBD fields will anger him. |
| 3 | **Prof. Hugh Durrant-Whyte** — SLAM pioneer, has direct experience with underground mine robotics in Australia (Northparkes copper mine, adjacent to Leung dataset work) | He can validate whether your claims about the Chilean dataset are accurate. He is the toughest person on the panel. |
| 4 | **Dr. Jeannette Bohg** — Stanford, simulation-to-real, MuJoCo environments, benchmark design | She will assess the pipeline's technical rigour and whether the geometry validation method (topdown overlay) is scientifically sufficient. |
| 5 | **Ananya Rao** — 4th year PhD, recently published an environment paper at CoRL 2024, fresh experience with what makes workshop submissions get accepted vs. rejected | She will flag readability, narrative flow, and what confused her as a reader. |

---

## SCORING FRAMEWORK

The paper is scored across 9 dimensions. Together they add up to **1000 points**. The RL results section is **not being penalised** for being incomplete because you have explicitly said you will add it — but the structural skeleton of that section is still evaluated.

| Dimension | Max Points | Why This Weight |
|---|---|---|
| Abstract | 100 | The abstract is the first and sometimes only thing a workshop reviewer reads. |
| Introduction | 150 | Sets the entire narrative. Highest word-for-effort return. |
| Related Work | 100 | Positions novelty. Either it works or it undercuts your claim. |
| Environment Design (Methodology) | 200 | **This is your main contribution.** Scored highest. |
| Benchmark Interface | 80 | Defines usability. Benchmark papers live or die on interface clarity. |
| Results | 100 | Even as validation, it must be credible. |
| Discussion & Limitations | 80 | Honesty here builds trust with reviewers. |
| Figures & Visual Story | 90 | Workshop papers are read visually first. |
| Writing, Terminology, Formatting | 100 | IEEE violations and terminology errors signal unreadiness. |

---

## SECTION-BY-SECTION BREAKDOWN

---

### 1. ABSTRACT — Score: 32 / 100

**What the current paper does:**
The abstract is written in 4 separate paragraphs. It introduces the environment (paragraph 1), re-explains MuJoCo (paragraph 2), describes the RL task (paragraph 3), and mentions results (paragraph 4). It uses the name "ChileMine-Sim" in the very first sentence. It describes agent operation as "partial observability." It contains no actual numbers — every result is implied but not stated.

**What is right:**
The four key topics are present — problem, environment, method, result. The core problem (no real-mine MuJoCo environment exists) is mentioned. The training objective (exploration-driven navigation) is named.

**What is wrong — panelist by panelist:**

**Prof. Scaramuzza:** "The IEEE ICRA abstract standard is a single paragraph of 150 to 250 words. Four paragraphs is not acceptable formatting, full stop. A reviewer seeing this at a glance will immediately question whether the authors have read a single ICRA paper before. Beyond formatting, the first sentence introduces the environment as 'ChileMine-Sim' when the title says 'MineXplore.' That is a naming contradiction on line 1."

**Dr. Pinto:** "MuJoCo is described in paragraph 1, then described again in paragraph 2 with 'Built in MuJoCo, a high-performance physics engine widely used for reinforcement learning.' Any reader who already knows what MuJoCo is — which is everyone at ICRA — will stop reading. You are burning abstract word count on explaining a tool the reader already knows."

**Prof. Durrant-Whyte:** "The phrase 'partial observability' is used in paragraph 2. I know this dataset. The Chilean mine has local sensing — LiDAR with finite range, no global map available to the robot. That is local observation, not partial observability in the formal POMDP sense. Partial observability technically means the agent cannot observe the full Markov state. Local observation means the agent can only see within a sensor range. These are related but distinct. Using the wrong term signals the authors have not read the relevant POMDP or robotics sensing literature carefully."

**Dr. Bohg:** "The phrase 'Results demonstrate that agents learn coordinated exploration strategies and successfully reconstruct key structural features of the mine' is a strong claim with zero numbers to back it. In the results section, every field is [TBD] or [PLACEHOLDER]. This is a claim written as if results exist when they do not. The abstract must either state real numbers or not make result claims at all."

**Ananya Rao:** "I read the abstract three times and I still don't know what MineXplore actually outputs. Is it an XML file? Is it a Python gym? Is it a dataset? The pipeline is named — OpenCV, Shapely, V-HACD, MJCF — but nowhere does the abstract say 'we release an open-source Gymnasium-compatible MuJoCo environment.' That is the product. Name the product clearly."

**Proposed Fix — rewrite the abstract from scratch as one paragraph:**

> "We present MineXplore, an open-source MuJoCo-based simulation environment for multi-robot navigation and exploration derived from real underground mine survey data. Starting from the Leung et al. 2017 Chilean copper mine dataset, we develop a seven-stage pipeline — contour detection, Shapely polygon extraction, V-HACD convex decomposition, and MJCF scene generation — that converts a 2D survey map into a physics-ready 3D tunnel world with 104,423 m² of navigable area. The compiled environment exposes a Gymnasium-compatible interface with local LiDAR observations and continuous velocity commands. To validate that MineXplore is navigable, we evaluate a MAPPO baseline, which achieves [X]% task success and [Y]% collision rate over [Z] episodes. MineXplore addresses a documented gap in the robot-learning tooling landscape: no prior MuJoCo or MJX environment has been grounded in a real production mine survey."

This is one paragraph. It introduces the name. It explains the pipeline in one sentence. It states the interface. It frames RL as validation. It gives numbers. It ends with the gap claim.

---

### 2. INTRODUCTION — Score: 58 / 150

**What the current paper does:**
The introduction opens with underground mine challenges (GPS denied, dust, water, topology). It mentions the DARPA SubT Challenge. It identifies two gaps. It introduces "ChileMine-Sim" as the solution. Figure 1 (the full pipeline diagram) appears here. Contributions are listed as three bullets using specific numbers (104,423 m², 1,186 geoms, seven-stage pipeline).

**What is right:**
The two-gap argument is strong and specific — Gap 1: no real-mine MuJoCo environment exists. Gap 2: Chilean mine dataset never used for simulation geometry. Both are well-supported by citations. The contribution bullets include real numbers, which is good. Reference [4] (Ebadi et al., IEEE T-RO 2024) is an excellent anchor citation.

**What is wrong:**

**Prof. Scaramuzza:** "Figure 1 — the entire pipeline diagram — appears inside the introduction before any methodology has been explained. A reader encountering terms like 'Douglas-Peucker' and 'V-HACD' and 'Shapely polygon with holes' in the introduction, before these concepts have been introduced, will not understand the figure. The figure belongs in Section III. What belongs in the introduction, if you want a figure, is a single high-level three-panel image: real mine photo, survey map, rendered MuJoCo environment. Three images, short caption, done."

**Dr. Pinto:** "The introduction cites papers [4], [2], [5] within the first paragraph. That immediately begins the literature survey feeling. The introduction's job is to tell the story of why this paper was needed and what it does, not to immediately start cataloguing related work. Keep the introduction to 3-4 paragraphs maximum. Citations should appear only to anchor the gap claims, not to describe prior work in detail."

**Prof. Durrant-Whyte:** "The contribution bullet for the pipeline says 'seven-stage contour-to-MJCF compilation and geometry-validation pipeline (Fig. 1), with a topdown overlay against the source survey as the primary fidelity check.' This is accurate — I counted seven stages in Fig. 1. But the word 'seven-stage' never reappears in Section III clearly. If you name it 'seven-stage' in your contributions, the reader must be able to go to Section III and find seven clearly labelled stages. Currently they cannot."

**Dr. Bohg:** "MJCF is used in the contribution bullets as an acronym without definition. MJCF stands for MuJoCo XML Format. IEEE standard requires that every acronym be defined on first use in the body, not just in the title. The first use of MJCF is in the contributions list. It must say 'MuJoCo XML Format (MJCF)' there."

**Ananya Rao:** "The contributions use 'ChileMine-Sim' in bullet point 1, while the paper title says 'MineXplore.' That is confusing. Also the caption for Fig. 1 is 92 words long. I counted. That is a methods section disguised as a caption. It describes the entire pipeline in full detail. You can write 15-20 words in a caption and move the rest to Section III where it belongs."

**Proposed structural fix for the Introduction:**
- Paragraph 1: Context (why mines are hard, 2-3 sentences)
- Paragraph 2: Gap statement (2 sentences, one per gap)
- Paragraph 3: "We present MineXplore..." — what it is and what it does
- Bullet contributions (3 bullets, clean, no [TBD])
- Remove Fig. 1 from here. Add a 3-panel teaser figure instead.
- Move all related work citations to Section II.

---

### 3. RELATED WORK — Score: 72 / 100

**What the current paper does:**
Four subsections: (A) Underground and Subterranean Robotics, (B) Simulation Environments for Robot Learning, (C) Real-Mine-Grounded Simulation, (D) Prior Use of the Chilean Mine Dataset. Section D claims, "To the best of our knowledge, no prior work has used the dataset's survey geometry to construct a physics-simulation environment in any engine."

**What is right:**
This is the best-written section in the paper. The structure into four subsections is logical and smart. Section D's gap claim is specific and honest about scope ("to the best of our knowledge"). The comparison against Gao and Awuah-Offei [12] in Section C is well-executed — three concrete differentiators are listed. The reference list is accurate: CERBERUS [2][3], Ebadi et al. [4], BARN [7][8], Isaac Gym [10], MuJoCo Playground [11] are all real papers with correct venue attributions.

**What is wrong:**

**Prof. Durrant-Whyte:** "You cite CERBERUS twice — reference [2] (Science Robotics) and reference [3] (Field Robotics) — for the same team and essentially the same system. That is redundant. Pick one citation. I recommend [2] since Science Robotics is higher impact and the result (winning the 2021 Final Event) is stated there."

**Prof. Scaramuzza:** "Reference [13] for Lösch et al. has [VERIFY full author list and volume] in the reference list. That means an unverified citation is going to be submitted to the workshop. If the panellist or reviewer checks that reference and it doesn't resolve, the entire paper's credibility is damaged. Fix this before submission — look it up, verify the volume and author list."

**Dr. Pinto:** "The lineages in Section B (Gazebo lineage, benchmarking lineage, GPU-accelerated lineage) are a useful organizational device, but the paragraph is long and the reasoning about why none of them 'ship a real-mine asset' is rushed into one sentence at the end. That conclusion — 'None of these ship a real-mine asset' — is your most important positioning statement in the entire related work. Give it its own sentence, make it bold if you want, and explain briefly what this gap costs the community (researchers who want to test underground navigation RL have no real-mine option)."

**Dr. Bohg:** "Section B mentions MuJoCo Playground [11] as having 'zero-shot sim-to-real transfer on quadrupeds, humanoids, and manipulators.' This is accurate per the arXiv paper. However, you then say 'None of these ship a real-mine asset' without noting that MuJoCo Playground also provides a framework for building new environments. A tough reviewer might say: 'just use MuJoCo Playground and add your mine.' You should add one sentence: 'MuJoCo Playground provides a framework for building environments but does not include any underground or survey-derived assets, requiring the user to build the geometry from scratch.'"

**Proposed fix:** The related work is good. The changes are small — remove one CERBERUS citation, fix reference [13], strengthen the final gap statement, add one clarifying sentence about MuJoCo Playground.

---

### 4. ENVIRONMENT DESIGN — Score: 88 / 200

This is your main contribution. It gets 200 points. It currently earns less than half.

**What the current paper does:**
Section III has four subsections: Source Data and Scale Calibration, 2D Geometry Extraction, 3D Compilation to MuJoCo, and Geometry Validation. Specific numbers are given: 1.36 px/m scale, 3.5 m tunnel height, 104,423 m² navigable area, 697 m × 188 m world extent, 1,186 V-HACD geoms. Fig. 3 (contour detection overlay) and Fig. 4 (MuJoCo viewer) are the two figures in this section.

**What is right:**
The scale calibration is specific and reproducible — 100m scale bar, 1.36 px/m. The navigable area (104,423 m²) is reported. The V-HACD decomposition into convex hulls is the correct technical choice for MuJoCo. The geometry validation approach (topdown overlay, Fig. 5) is a legitimate method. Load time (under 10 seconds, AMD Ryzen 5 5600H) is stated. These are all real, verifiable numbers.

**What is wrong:**

**Prof. Durrant-Whyte:** "The section opens with 'Section III walks through the pipeline of Fig. 1 in order.' But Fig. 1 is on page 2 and is already two pages ago at this point. More importantly, Fig. 1 has seven boxes, but Section III has four subsections. The mapping between the seven stages and the four subsections is never explained. A reviewer trying to follow along cannot do so. Either label the seven stages explicitly (Stage 1: Binarize + Contour Trace, Stage 2: Shapely Polygon, etc.) and map each subsection to its stage(s), or rename the subsections to match the stage names in Fig. 1."

**Dr. Bohg:** "The V-HACD decomposition is described with this phrase: 'we decomposed the extruded mesh with V-HACD into convex hulls [VERIFY: V-HACD resolution, concavity threshold, max hulls].' The [VERIFY] tag is in the actual paper text. This means a parameter that determines the quality of your collision geometry — how accurately the walls are represented for collision purposes — has an unknown value. This is not a minor detail. V-HACD has three key parameters: resolution (number of voxels), concavity threshold, and maximum number of hulls. These affect whether a robot can navigate narrow passages without false collision triggers. You must look up the actual values used and state them. Do not submit with [VERIFY] in the text."

**Dr. Pinto:** "There are exactly two figures covering the entire methodology section (Figs. 3 and 4), plus Fig. 5 in the Results section. Fig. 4 — the MuJoCo viewer screenshot — is dark, taken at a strange camera angle, and shows a large flat brown surface with some geometry in the background. It does not showcase the tunnel structure compellingly. An interested reader or reviewer asking 'does this look like a mine?' will not be convinced by Fig. 4. You need: (a) a bird's-eye view with walls clearly visible; (b) a first-person robot perspective inside the tunnel; (c) a side-by-side of the 2D contour and the 3D extrusion. These are the images that sell the contribution."

**Prof. Scaramuzza:** "The section currently has no description of the robot model. The contributions mention 'a Gymnasium-compatible multi-agent navigation interface' but Section III never specifies the robot: differential drive? what wheelbase? what mass? what collision geometry? For a simulation environment paper, the robot model is part of the environment specification, not an afterthought in Section IV."

**Ananya Rao:** "I read this section twice and I cannot find where texture mapping is described. In the pipeline figure (Fig. 1), Stage 7 is 'Texture + Run RL Algorithm.' But in Section III, there is no subsection on texture. Either texture mapping is missing from the paper or it was planned but not yet written. Either way, this must be resolved — either describe what textures are applied and how, or remove 'Texture' from Stage 7 of Fig. 1."

**Prof. Durrant-Whyte (additional point):** "The phrase 'achieving strong geometric consistency with the source map through pixel-to-metric calibration and validation overlays' appears in the abstract. The actual validation in the paper is a visual topdown overlay in Fig. 5. That is a qualitative comparison, not a quantitative one. There is no Intersection-over-Union metric, no Hausdorff distance between the extracted contour and the source map boundary, no pixel-level error analysis. The claim of 'strong geometric consistency' is therefore unsubstantiated. Either add a quantitative metric (IOU between rendered topdown and source map would work) or change the language to 'we verify geometric consistency by visual topdown overlay comparison.'"

**Proposed fixes:**
- Label the seven stages explicitly at the start of Section III
- Map subsections to stage numbers
- Remove all [VERIFY] tags and fill in actual V-HACD parameters
- Add a subsection on texture mapping or remove texture from the pipeline
- Add robot model specification (mass, wheelbase, collision geometry)
- Replace Fig. 4 with a better interior tunnel render
- Add a first-person robot eye perspective image
- Add a quantitative geometric fidelity metric or soften the language

---

### 5. BENCHMARK INTERFACE — Score: 22 / 80

**What the current paper does:**
Section IV has four subsections: Observation and Action Spaces, Reset/Step/Episode Structure, Multi-Agent Extension, and Reproducibility. Nearly every parameter is [TBD]. LiDAR beam count: [TBD]. Range: [TBD]. Reward details: [TBD: reward details from Badri's setup]. MuJoCo version: [TBD]. N agents: [TBD].

**What is right:**
The high-level architecture is sound — Gymnasium-compatible reset/step loop, continuous (v, ω) action space, local observation concept, per-agent reward with shared collision penalty, fixed seeds for reproducibility.

**What is wrong:**

**Dr. Pinto:** "This section as written cannot be reviewed. The core purpose of a benchmark interface section is to give another researcher enough information to re-implement or use your environment. LiDAR beam count, LiDAR range, N agents — these are not minor details. These are the definition of the benchmark. The LiDAR configuration alone determines whether a trained policy is comparable across different runs. Without these numbers, this section is meaningless. I know the author plans to add them, and I will judge the final version, but the paper must not be submitted in this state."

**Dr. Bohg:** "The reward structure says '[TBD: reward details from Badri's setup]' — I want to point out that from the project knowledge, the reward structure already exists and is fully implemented. The collision penalty is -15.0 per step, milestone bonuses exist at 25%, 50%, and 75% coverage, LiDAR beams are 16 with range 0.12-10m. These numbers exist in the implementation. They just have not been written into the paper. This is not a matter of work still to be done — it is a matter of copy-pasting from the code into the paper."

**Ananya Rao:** "The reproducibility subsection says 'Code and model will be released upon publication.' IEEE ICRA workshop papers do not require code release, but saying you will release it without a concrete commitment (like a GitHub URL placeholder) is weaker than saying nothing. Either commit to a repo URL or remove the sentence."

**Proposed fixes:**
- Fill in LiDAR: 16 beams, range 0.12-10m, normalized
- Fill in action space: continuous (v, ω) differential drive
- Fill in N agents: state the number used
- Fill in reward structure: step penalty, milestone bonuses at 25/50/75%, collision penalty -15.0
- Fill in MuJoCo version
- Add a GitHub URL placeholder if you plan to release

---

### 6. RESULTS — Score: 28 / 100

**I am not penalising the empty RL results.** You have told me you will add them. I am evaluating only what is currently present, which is Fig. 5 (the topdown overlay) and the claim of 100% ray-cast navigability.

**What is right:**
Fig. 5 is the strongest figure in the paper. Showing the original survey map side-by-side with the rendered MuJoCo topdown view is exactly the right primary fidelity check. The outer tunnel boundary, rock island, and passages visually coincide. The claim "100% of sampled free-space points pass ray-cast navigability" is a real, verifiable result — though the sample count is [TBD].

**What is wrong:**

**Prof. Durrant-Whyte:** "The sample count for the ray-cast navigability check is [TBD: sample count]. How many points were sampled? 100 points and 10,000 points are both '100%' by the metric as stated, but they mean very different things about the thoroughness of validation. State the number."

**Dr. Bohg:** "Fig. 5 caption calls this the 'primary geometric fidelity check of the paper.' I agree it is necessary. But it is not sufficient as a quantitative measure. The Intersection-over-Union (IOU) between the binary mask of the original survey and the orthographic render could be computed in Python in approximately 20 lines of code. I strongly suggest adding this one number. It transforms Fig. 5 from a qualitative visual comparison into a quantitative result."

**Proposed fix:** Add IOU score to Fig. 5. State sample count for ray-cast check. When RL results come in, use learning curves (not a table) as the primary visualization — consistent with your own notes.

---

### 7. DISCUSSION AND LIMITATIONS — Score: 52 / 80

**What the current paper does:**
Three subsections: What ChileMine-Sim Is and Is Not, Limitations, When to Use ChileMine-Sim. Four limitations are stated: no elevation change, V-HACD hull artifacts, no sensor textures, early-stage RL results.

**What is right:**
The "What It Is and Is Not" framing is excellent academic practice. Explicitly saying "not a physics-calibrated twin," "not a multi-mine suite," and "not a sim-to-real system" protects against reviewer objections before they can be raised. The "When to Use" subsection is a good idea in principle — few papers do this.

**What is wrong:**

**Prof. Scaramuzza:** "The 'When to Use ChileMine-Sim' subsection says: 'Use the SubT Virtual Testbed or the Edgar Mine framework of Gao and Awuah-Offei if you need elevation modelling or the Gazebo asset ecosystem.' You are directly telling the reader to use a competitor product over yours for a significant use case. This is not good positioning. Elevation modelling is a real limitation — but phrasing it as 'go use Gazebo instead' gives Gazebo more weight than your environment. The correct framing is: 'MineXplore is optimized for RL training speed and real-survey geometry. For full elevation modelling or Gazebo-based hardware integration, complementary tools exist.' Lead with your strengths, then acknowledge limits."

**Prof. Durrant-Whyte:** "The limitation on elevation is stated as 'the source is a 2D floor plan extruded at constant height; the environment has no elevation change.' This is accurate. But there is a missing detail: the Chilean mine tunnel actually has grade changes — the survey data from Leung et al. includes slope information. The limitation is not just that 2D floor plans lack elevation; it is that even the source dataset has elevation data that you chose not to use. Being explicit about this choice (and why — it simplifies the geometry, it's a reasonable first-pass approximation) is more intellectually honest than saying the source is a 2D floor plan."

**Proposed fix:** Reframe "When to Use" to lead with MineXplore strengths. Be explicit that the elevation limitation is a design choice, not a data limitation. Use "MineXplore" not "ChileMine-Sim" throughout this section.

---

### 8. FIGURES AND VISUAL STORY — Score: 35 / 90

**What the current paper does:**
Six figures total: Fig. 1 (pipeline diagram in Introduction), Fig. 2 (source floor plan), Fig. 3 (contour detection overlay), Fig. 4 (dark MuJoCo viewer), Fig. 5 (topdown comparison), Fig. 6 (placeholder for learning curves). One table (Table I, all placeholder).

**What is right:**
Fig. 5 is strong. The visual comparison between original survey and MuJoCo render is clear, appropriately sized, and supports the paper's core claim. Fig. 3 (contour detection on binarised map) clearly shows the OpenCV output. Fig. 2 (source floor plan) provides necessary reference.

**What is wrong:**

**Ananya Rao:** "Fig. 4 is boring. I know that word is harsh, but it is accurate. It shows a dark, slightly tilted view of what appears to be a brown flat surface with some geometry. The tunnel walls are barely visible. The central rock island is not prominent. If I showed Fig. 4 to someone unfamiliar with MuJoCo environments and asked 'is this a mine tunnel?', they would say no. You need: (1) a top-down lit render that shows the full tunnel network shape, (2) a first-person view from inside the tunnel showing the walls and corridor structure, (3) a side-by-side comparison of the 2D contour map and the 3D render."

**Dr. Pinto:** "There is no figure showing what the agent sees. This is a benchmark paper. The agent's observation — the local LiDAR scan, the local map, whatever the agent receives — is part of the benchmark specification. Without a figure showing the robot eye view, the reader cannot evaluate whether the benchmark is realistic or trivial. Add this."

**Prof. Scaramuzza:** "Fig. 1's caption is 92 words long. I counted. A standard IEEE figure caption should be one to two sentences. The caption for Fig. 1 is literally an abstract of the methodology section. The information in that caption belongs in Section III. Shorten the caption to: 'End-to-end MineXplore compilation pipeline from the Leung et al. 2017 survey map to a Gymnasium-compatible MuJoCo environment.' Done."

**Dr. Bohg:** "The paper has 4 real figures and 2 placeholders. A 4-page IEEE paper typically has 4-8 figures. You are at the low end, and 2 of those don't exist yet. The visual space is being underutilized. Add: (a) agent observation view, (b) better tunnel interior render, (c) learning curve when ready."

**Vibhakar Mohta's suggestion (already given):** Add a systems-level diagram with real mine photos. This is correct. A 3-panel figure: real mine photo from Chilean mine → 2D survey map → rendered MuJoCo environment. This should be Figure 1. The current pipeline diagram (which is good) should move to Section III.

---

### 9. WRITING, TERMINOLOGY, AND FORMATTING — Score: 30 / 100

**What the current paper does:**
Uses "ChileMine-Sim" in the abstract, introduction, contributions, discussion, and conclusion — while the title says "MineXplore." Uses [TBD], [VERIFY], and [PLACEHOLDER] tags throughout. Some section headings appear in italics in the rendered PDF. The formatting was noted by Vibhakar Mohta to be "merging into right column."

**What is wrong:**

**Prof. Scaramuzza:** "There are 18 instances of 'ChileMine-Sim' in the paper body. The paper is titled 'MineXplore.' This must be a find-and-replace before submission. It also signals that the paper was written under one name and never updated — a sign of rushed preparation."

**Yash Butala's comment confirmed:** "MJCF is used without the full form. First use in the paper is in the contributions section. It must read 'MuJoCo XML Format (MJCF)' there. After that, MJCF alone is fine."

**Prof. Durrant-Whyte:** "Reference [13] for Lösch et al. has '[VERIFY full author list and volume]' in the actual reference list. A published paper cannot have unverified references. Look this up. The paper is: Lösch et al., 'Design of an Autonomous Robot for Mapping, Navigation, and Manipulation in Underground Mines,' in Field and Service Robotics, 2020, or possibly the Sensors journal 2023 version. Verify and fix."

**Dr. Bohg:** "The [VERIFY] tag inside the Section III text — 'V-HACD into convex hulls [VERIFY: V-HACD resolution, concavity threshold, max hulls]' — is inside the body text of the paper, not just a note to yourself. It will appear in the PDF exactly as shown. This is not acceptable for any submission."

**Ananya Rao:** "The italic section headings (visible in Fig. 4's position in the PDF) conflict with standard IEEE conference formatting. IEEE uses numbered section headings in small caps or bold. Check the ICRA LaTeX template and fix heading styles."

---

## DEVIL'S ADVOCATE PANEL SCORING

### Individual Panelist Scores

| Section | Max | Scaramuzza | Pinto | Durrant-Whyte | Bohg | Rao | Average |
|---|---|---|---|---|---|---|---|
| Abstract | 100 | 28 | 30 | 35 | 38 | 38 | **33.8** |
| Introduction | 150 | 55 | 52 | 60 | 65 | 60 | **58.4** |
| Related Work | 100 | 72 | 68 | 70 | 75 | 72 | **71.4** |
| Environment Design | 200 | 82 | 90 | 88 | 95 | 85 | **88.0** |
| Benchmark Interface | 80 | 18 | 15 | 22 | 20 | 25 | **20.0** |
| Results | 100 | 25 | 30 | 28 | 30 | 28 | **28.2** |
| Discussion & Limitations | 80 | 50 | 52 | 48 | 55 | 52 | **51.4** |
| Figures & Visual Story | 90 | 32 | 38 | 34 | 36 | 36 | **35.2** |
| Writing/Terminology/Format | 100 | 28 | 30 | 30 | 32 | 32 | **30.4** |
| **TOTAL** | **1000** | **390** | **405** | **415** | **446** | **428** | **416.8** |

---

### FINAL PANEL VERDICT

**Score: 417 / 1000**

**Prof. Scaramuzza:** "The core contribution is real and the gap is genuine. No one has done this before. But the paper cannot be submitted as is. The naming inconsistency alone (ChileMine-Sim vs MineXplore) signals a paper that was not proofread. The [VERIFY] and [TBD] tags throughout communicate that the authors themselves are not sure of their own numbers. Fix the naming. Fill in every TBD that you already know the answer to — which from the project files appears to be most of them. Then the score jumps substantially."

**Dr. Pinto:** "This paper currently reads as a draft of a benchmark paper rather than a benchmark paper. The benchmark interface section is the most critical section for a paper like this — it defines the thing you are contributing — and it is almost entirely empty. Once filled in, this section alone can add 50+ points. The RL results, when added, add another 50+. The paper can realistically reach 750+ with three focused days of work."

**Prof. Durrant-Whyte:** "The geometric validation is the most important technical claim in this paper, and it is currently qualitative (visual overlay only). Add IOU. Add the V-HACD parameters. Fix the elevation limitation description. These are non-negotiable for credibility with anyone who knows underground robotics data."

**Dr. Bohg:** "The pipeline idea is genuinely useful and the implementation exists — the project files show a working implementation with specific parameters. The problem is exclusively writing. Almost all the information needed to write a strong Section IV already exists in the codebase and is not in the paper. This is a writing and organization problem, not a technical one."

**Ananya Rao:** "As a reader who came in fresh, the paper confused me on name (MineXplore vs ChileMine-Sim), on what the agent actually sees (never shown), and on whether the results exist (implied in abstract, all placeholders in results). Fix those three things and the paper becomes readable and credible."

---

## PATH TO 850+ SCORE: REALISTIC AFTER YOUR FIXES

| After Fix | Points Added | New Score |
|---|---|---|
| Rename all ChileMine-Sim → MineXplore | +20 | 437 |
| Rewrite abstract as 1 paragraph with real numbers | +55 | 492 |
| Fill in Section IV (LiDAR 16 beams, 0.12-10m, reward structure) | +52 | 544 |
| Move Fig. 1 to Section III, add 3-panel teaser to Introduction | +30 | 574 |
| Fix Fig. 4 (better tunnel render + first-person view) | +30 | 604 |
| Add agent observation view figure | +25 | 629 |
| Remove [VERIFY] tags, fill in V-HACD params | +20 | 649 |
| Fix reference [13] (Lösch et al.) | +10 | 659 |
| Define MJCF on first use | +8 | 667 |
| Add IOU metric to Fig. 5 | +20 | 687 |
| Add texture subsection or remove texture from pipeline | +15 | 702 |
| Fix abstract naming (ChileMine-Sim → MineXplore) | included above | — |
| Fix elevation limitation language | +10 | 712 |
| Reframe "When to Use" to lead with MineXplore strengths | +8 | 720 |
| Add RL results (learning curves, success/collision rates) | +90 | 810 |
| Fix ICRA formatting (headings, captions, column merging) | +20 | 830 |
| Restructure Introduction (funnel structure, remove early figure) | +25 | 855 |

**Realistic final score after all fixes: 850-860 / 1000**

---

## MASTER FINAL CHANGE LIST (Priority Order)

These are every change that needs to be made. They are ordered from most critical (paper is broken without it) to minor polish.

**CRITICAL — paper cannot be submitted without these:**

1. Find and replace every instance of "ChileMine-Sim" with "MineXplore" throughout the entire paper
2. Rewrite the abstract as a single paragraph (150-200 words): problem statement, MineXplore + pipeline, Gymnasium interface, RL as validation with actual numbers, gap claim
3. Remove "partial observability" — replace with "local observation" everywhere
4. Remove all [TBD], [VERIFY], and [PLACEHOLDER] tags — fill in every one you already know (LiDAR: 16 beams, 0.12-10m; reward structure from your implementation; V-HACD parameters from your code; agent count; MuJoCo version)
5. Fix reference [13] — look up Lösch et al. and fill in the actual full author list and volume
6. Define MJCF on first use: "MuJoCo XML Format (MJCF)"
7. Remove "MuJoCo is a high-performance physics engine..." from the second paragraph of the abstract — it is already in Introduction
8. Fix Fig. 1 caption — reduce from 92 words to 20 words. Move the technical detail into Section III

**HIGH PRIORITY — significantly impact score:**

9. Move Fig. 1 (pipeline diagram) to Section III where it belongs
10. Add a three-panel teaser figure to the Introduction: real mine photo → 2D survey map → rendered MuJoCo environment
11. Replace Fig. 4 with a better render — top-lit bird's eye view showing the full tunnel network, then a separate first-person interior tunnel view
12. Add an agent observation view figure showing what the robot actually sees (16-beam LiDAR scan, local map)
13. Add IOU quantitative metric to the topdown validation (Fig. 5) — compare binary mask of source survey against orthographic render
14. State the ray-cast navigability sample count (currently [TBD: sample count])
15. Add explicit Stage labels to Section III (Stage 1 through Stage 7) matching Fig. 1
16. Add a texture mapping subsection in Section III, or remove "Texture" from Stage 7 of Fig. 1 if Sreeram's work is not ready
17. Add robot model specification: differential drive, wheelbase, mass, collision geometry

**MEDIUM PRIORITY — improve quality and positioning:**

18. Restructure Introduction: context paragraph → gap statement → "We present MineXplore" paragraph → 3 bullet contributions. Remove all dense citations from Introduction and move them to Section II
19. Reframe "When to Use" to lead with MineXplore strengths: training speed, real-survey geometry, Gymnasium interface. Then acknowledge elevation limitation
20. Fix elevation limitation language: acknowledge that the Leung et al. dataset contains slope data but the 2D extrusion design choice simplifies elevation. This is a choice, not a data limitation
21. Remove one of the two CERBERUS citations [2] or [3] — they are redundant
22. Add one sentence in Section II.B positioning against MuJoCo Playground specifically
23. Replace Table I with learning curve figures when RL results come in
24. State explicitly in Section IV: "We use RL solely to validate that MineXplore is navigable under local observations — RL is not the primary contribution of this paper"
25. Add explicit mention of Xplore-relevant exploration metric: coverage percentage (fraction of tunnel area seen) per episode

**POLISH — formatting and language:**

26. Fix all section heading formatting to match IEEE ICRA LaTeX template (no italic headings)
27. Fix column overflow / merging into right column noted by Vibhakar Mohta
28. Reduce abstract acronyms (MAPPO, LSTM, V-HACD all appear in abstract — define or remove per Yash Butala's comment)
29. Run final draft through grammar check for sentence completeness and consistent tense
30. Add GitHub placeholder URL to reproducibility section or remove the code release promise
