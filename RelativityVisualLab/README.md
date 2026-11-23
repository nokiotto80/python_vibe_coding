# RelativityVisualLab

**An interactive Python laboratory for exploring special and general relativity through numerical models and visual simulations.**

RelativityVisualLab is an educational software project designed to explore selected concepts of spacetime physics through interactive visualizations.

The project combines Python, mathematical models and graphical interfaces to make abstract concepts in relativity easier to investigate and understand.

It is developed as a modular application, with separate components for the graphical interface, physical models, configuration and individual simulations.

## Features

The project is under active development. Its current and planned components include:

- **Minkowski diagram** — visualization of spacetime events, worldlines and light cones.
- **Tesseract** — a three-dimensional representation of a four-dimensional hypercube.
- **Black hole simulations** — qualitative visualization of spacetime curvature around massive objects.
- **Wormhole simulations** — exploratory visual representations of hypothetical spacetime geometries.
- **Interactive graphical interface** — a central application window for accessing the available simulations.
- **Dynamic simulation loading** — simulation modules configured and managed through a JSON configuration file.

The simulations are intended primarily for educational and exploratory purposes. Their visual models may use simplified assumptions and should not be interpreted as precision scientific software.

## Technology Stack

The project is primarily developed using:

- Python 3
- Dash
- Plotly
- NumPy
- Flask
- Tkinter (Python standard library)

The application is designed around a modular Python architecture.

## Project Structure

```text
RelativityVisualLab/
│
├── assets/                 # Images and graphical resources
├── config/                 # Application and simulation configuration
├── docs/                   # Project documentation
├── examples/               # Example usage and experiments
├── gui/                    # Graphical user interface
├── physics/                # Physical and mathematical models
├── simulations/            # Individual simulation modules
│
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore              # Git exclusions
```

## Installation

### 1. Clone the repository

The project is currently hosted as a subdirectory of the `python_vibe_coding` repository.

```bash
git clone https://github.com/nokiotto80/python_vibe_coding.git
cd python_vibe_coding/RelativityVisualLab
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

## Development

RelativityVisualLab is an evolving project.

The development approach focuses on:

- Modular and maintainable Python code.
- Separation of graphical interface, simulation logic and physical models.
- Reusable components.
- Interactive scientific visualization.
- Version control through Git and GitHub.

New simulations and improvements will be added progressively.

## Scientific Scope and Limitations

This project is an educational visualization laboratory, not a numerical relativity solver.

Some models use simplified or qualitative representations of physical phenomena. The assumptions and mathematical approximations used by each simulation should be documented alongside the corresponding module.

## Project Status

**Work in progress.**

The architecture and initial simulations are being developed incrementally. Features, interfaces and physical models may change as the project evolves.

## Author

Developed by **nokiotto80**.

Contributions, suggestions and technical feedback are welcome.

## License

No open-source license has been specified yet. Until a license is added, all rights are reserved by the author.
