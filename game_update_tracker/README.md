# Game Update Tracker

## Features

- 🔍 Tracks file changes and version info between updates
- ⚙️ Supports multiple installed game instances
- 🗂️ Saves state snapshots for each game instance
- ⚡ Uses multi-core hashing for fast scanning with `xxhash`
- 🧾 Generates HTML reports with version and file changes

## Directory Structure

| Directory          | Purpose                                                 |
| ------------------ | ------------------------------------------------------- |
| `instance_states/` | Stores previous scan results (JSON snapshots)           |
| `reports/`         | Stores generated HTML change reports                    |
| `instances.json`   | Configuration file mapping instance names to game paths |

## Setup

Make sure you have **Python 3.8+** installed.
Install dependencies:

```
pip install xxhash
```

Adjust the `instances.json` configuration for your game installation(s).
The instance name will be used for the report file name.
The path needs to point to the directory that contains `GF2_Exilium.exe`.

## Usage

```
python game_update_scanner.py
```

Running this for the first time will take a while to calculate the initial state of the game.
Afterwards just run it after any update to get a report on the changes.

```
python copy_new_files.py <report>.html [data_dir] [output]
```

Copy all the new and modified files from a given report from the games `Data` directory to the output directory.
