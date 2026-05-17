# Energy Production Optimization

## Overview

An optimization system for planning electricity production and power plant maintenance scheduling. Determines optimal maintenance schedules for power plants while minimizing total production costs and meeting demand constraints.

The goal of this project is therefore to model the electricity production system and compute:

- a **maintenance schedule** for power plants,
- a **corresponding production plan**,

such that the **total cost of electricity production is minimized** over the planning horizon.

This work is conducted as part of a **TER (Travail d’Étude et de Recherche)** under supervision of [Dr. Mariam SANGARE](linkedin.com/in/mariam-sangare01) and is inspired by the **ROADEF/EURO Challenge 2010**, a well-known industrial optimization challenge proposed by EDF.

## Quick Start

### Requirements

- Python 3.1+

### Installation

```bash
# Clone the repository
git clone https://github.com/lafilledepondy/energyProductionOptimization.git
cd energyProductionOptimization

# Create virtual environment
python3 -m venv venv
source venv/bin/activate # on Linux
# venv\Scripts\activate # on Windows

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
python3 main.py
```

## Documentation

- **[Presentation](assets/Presentation_TER.pdf)** – TER presentation slides
- **[Report](assets/rapport_TER.pdf)** – TER final report (note: report is in French ; it doesn't include the relaxation lineare & relaxation lagrangienne of the project, which is still in progress)
- **[Project Specifications](assets/sujet_MaintenanceCentrales.pdf)** – Adapted project specifications
- **[Original Specifications](assets/sujet_Original.pdf)** – Original project specifications

## License

MIT License - see [LICENSE](LICENSE) for details
