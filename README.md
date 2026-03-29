# Energy Production and Power Plant Maintenance Planning

## Description

This project studies the **planning of electricity production and power plant maintenance**. The objective is to determine an optimal schedule for shutting down power plants for maintenance while ensuring that electricity demand is satisfied at minimal production cost.

Power plants, particularly nuclear plants, must periodically stop operating to refuel and perform maintenance operations. Planning these outages is a complex optimization problem because many operational, safety, and logistical constraints must be satisfied simultaneously while maintaining sufficient electricity generation capacity.

The goal of this project is therefore to model the electricity production system and compute:

- a **maintenance schedule** for power plants,
- a **corresponding production plan**,

such that the **total cost of electricity production is minimized** over the planning horizon.

This work is conducted as part of a **TER (Travail d’Étude et de Recherche)** and is inspired by the **ROADEF/EURO Challenge 2010**, a well-known industrial optimization challenge proposed by EDF.

## Visuals

## Installation

### Requirements

- Python 3.1+

### Setup

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

## Usage

```bash
./main.py
```

## Roadmap

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
