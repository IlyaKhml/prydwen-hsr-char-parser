<p align='center'>
    <b>EN</b> • <a href='README_RU.md'>RU</a>
</p>

# Prydwen (HSR) Character Data Parser

This script is designed to fetch and save character data from the website [Prydwen](https://www.prydwen.gg). It allows you to parse data for a specific character or process a complete list of characters. 

The script is focused on collecting information about characters from the game **Honkai: Star Rail (HSR)** and automatically generates URLs for characters based on character [list from Prydwen](https://www.prydwen.gg/star-rail/characters).

---

## Features
- Parse data for a single character.
- Parse data for all characters in the list.
- Save parsed data in `.pickle` files.
- Automatically generates URLs for character pages.
- Handles errors gracefully and lists skipped characters.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/IlyaKhml/prydwen-hsr-char-parser/
   cd prydwen-hsr-char-parser
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the script using Python with the following arguments:

### 1. Parse a Specific Character
To parse data for a specific character, use the `--character` (or `-c`) argument:
```bash
python main.py --character yunli
```

Replace `yunli` with the name of the desired character. The character must be in the predefined list.

### 2. Parse All Characters
To process the entire character list, use the `--all` (or `-a`) argument:
```bash
python main.py --all
```

---

## Command-Line Arguments
| Argument          | Alias | Description                                              |
|-------------------|-------|----------------------------------------------------------|
| `--character`     | `-c`  | Specify the name of a character to parse data for.       |
| `--all`           | `-a`  | Parse data for all characters in the list.              |

---

## How It Works

1. **Input:**
   - The script uses a predefined list of character names.
   - URLs for characters are automatically constructed in the format:
     ```
     https://www.prydwen.gg/star-rail/characters/<character-name>
     ```

2. **Output:**
   - Data is saved as `.pickle` files in the `data/` directory.
   - Each file is named after the character (e.g., `yunli.pickle`).
   - The `.pickle` file contains a dictionary with the following structure:
     ```
     {
         "light cones": DataFrame containing the data for the light cones,
         "relics": DataFrame containing the data for the relics,
         "planar sets": DataFrame containing the planar set data,
         "additional planar sets": Dictionary of additional planar sets data,
         "relic main stats": DataFrame containing relic main stats,
         "relic main stats dict": Dictionary of relic main stats with importance levels,
         "substats": String containing the substats,
         "substats dict": Dictionary of substats with importance levels,
         "substats details": String containing detailed substat information,
         "substats comments": String with comments about substats,
         "endgame stats": DataFrame with endgame stats data,
         "traces priority": Dictionary of traces priority,
         "synergy": List of synergy characters,
         "teams (MoC)": List of teams with rank, usage%, and rounds.
         "element": The element of the character.
     }
     ```

---

## Error Handling
- If a character cannot be processed due to a timeout or another issue, their name is added to a skipped list.
- All skipped characters are displayed after the script finishes processing.

---

## Example

### Processing All Characters
```bash
python main.py --all
```

### Processing a Single Character
```bash
python main.py --character kafka
```

---

## Notes
- Ensure you have write permissions for the `data/` directory to save the output files.
- The script includes a 5 second delay between processing each character to prevent possible blocking during parsing.
- Feel free to modify the character list in the `main.py` file if needed.


## License

Project HSR Character Data Parser is distrebuted under the MIT License.
