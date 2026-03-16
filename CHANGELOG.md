# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [8.4.0] - 2026-03-02

### Added

- **Vortex Semantic Engine**: Replaced legacy keyword-based task classification with high-fidelity semantic routing using TF-IDF and NumPy.
- **Vortex Benchmark Suite**: New validation script (`system/scripts/vortex_benchmark.py`) to verify routing accuracy across diverse PM queries.
- **Strategic Enhancement Roadmap**: Formalized long-term vision in `implementation_plan.md` following the ULTRATHINK protocol.

---

## [8.3.0] - 2026-03-02

### Added

- **Better Antigravity Integration**: Official recommendation and auto-installation for the "Better Antigravity" extension (`kanezal.better-antigravity`).
- **FTUE Auto-Install**: Modified `core_setup.py` to automatically install `required` extensions during the Initial Setup Wizard.
- **Enhanced Documentation**: Updated `README.md` with Better Antigravity setup instructions.

### Fixed

- Improved extension installation reliability via `subprocess_helper.py`.

---

## [8.2.0] — Agent Fan-Out Engine + Critical Fixes - 2026-02-21

### Added

- **Agent Fan-Out Engine**: Code-executable parallelism allowing PM tasks to be dispatched to multiple expert agents (Staff PM, UX, Eng) simultaneously.
- **Result Synthesizer**: Intelligent merging of parallel agent outputs with conflict detection.
- **`/fan-out` Command**: New system command for high-concurrency PM workflows.
- **Phased RICE Scoring**: Integrated Phase 2.6 RICE/MoSCoW framework into PRD Authoring.

### Fixed

- **Root Directory Reconciliation**: Fixed ghost paths for `system/queue`.
- **Test Suite Optimization**: Restored test coverage to 80+ passing tests (0 failures).
- **Skill Integrity**: Fixed broken YAML frontmatter in 3 core skills.
- **Path Portability**: Replaced absolute paths with `Path.home()` for cross-platform stability.

---

## [4.8.0] - Historical Baseline

- Standardized 0-5 Folder Hierarchy.
- Initial Gemini CLI mesh integration.
- Context-driven development (Conductor) support.
