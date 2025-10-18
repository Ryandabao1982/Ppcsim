# Ppcsim - PowerPC Simulator

A simple educational PowerPC instruction set simulator written in Python.

## Features

- **Basic PowerPC Instructions**: Supports common instructions including:
  - Arithmetic: `add`, `addi`, `addis`, `subf`
  - Logical: `and`, `or`, `ori`
  - Memory: `lwz` (load word), `stw` (store word)
  - Control flow: `b` (branch)
- **32 General Purpose Registers**: Full support for r0-r31
- **Special Purpose Registers**: PC, LR, CTR, CR
- **Configurable Memory**: Default 64KB, customizable
- **Debug Output**: View CPU state and register values

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Ryandabao1982/Ppcsim.git
cd Ppcsim

# Install the package
pip install -e .
```

### Direct Usage

```bash
# Make the script executable
chmod +x ppcsim.py

# Run directly
./ppcsim.py --example
```

## Usage

### Run Example Program

```bash
ppcsim --example
```

This runs a simple program that calculates: 5 + 10 + 15 = 30

### Python API

```python
from ppcsim import PPCSimulator

# Create a simulator instance
sim = PPCSimulator(memory_size=65536)

# Define a simple program (machine code)
program = [
    0x38200005,  # addi r1, r0, 5    (r1 = 5)
    0x3840000A,  # addi r2, r0, 10   (r2 = 10)
    0x7C611214,  # add r3, r1, r2    (r3 = r1 + r2)
    0x00000000,  # halt
]

# Load and run the program
sim.load_program(program, start_address=0)
sim.run(max_instructions=1000)

# Display the results
sim.print_state()

# Access register values
result = sim.registers[3]  # r3 contains the result
print(f"Result in r3: {result}")
```

## Supported Instructions

| Instruction | Opcode | Description |
|-------------|--------|-------------|
| `add` | 31/266 | Add two registers |
| `addi` | 14 | Add immediate |
| `addis` | 15 | Add immediate shifted |
| `subf` | 31/40 | Subtract from |
| `and` | 31/28 | Logical AND |
| `or` | 31/444 | Logical OR |
| `ori` | 24 | OR immediate |
| `lwz` | 32 | Load word and zero |
| `stw` | 36 | Store word |
| `b` | 18 | Branch |

## Architecture

- **Memory**: Byte-addressable with configurable size
- **Word Size**: 32-bit instructions and data
- **Endianness**: Big-endian
- **Registers**: 32 general-purpose registers (32-bit each)

## Examples

### Example 1: Simple Addition

```python
from ppcsim import PPCSimulator

sim = PPCSimulator()
program = [
    0x38200064,  # addi r1, r0, 100  (r1 = 100)
    0x38400032,  # addi r2, r0, 50   (r2 = 50)
    0x7C611214,  # add r3, r1, r2    (r3 = 150)
    0x00000000,  # halt
]
sim.load_program(program)
sim.run()
print(f"100 + 50 = {sim.registers[3]}")
```

### Example 2: Memory Operations

```python
from ppcsim import PPCSimulator

sim = PPCSimulator()
program = [
    0x3C601234,  # addis r3, r0, 0x1234  (r3 = 0x12340000)
    0x60635678,  # ori r3, r3, 0x5678    (r3 = 0x12345678)
    0x90610100,  # stw r3, 0x100(r1)     (store to memory)
    0x80810100,  # lwz r4, 0x100(r1)     (load from memory)
    0x00000000,  # halt
]
sim.load_program(program)
sim.run()
sim.print_state()
```

## Development

### Running Tests

```bash
# Run the example program
python ppcsim.py --example

# Or using the installed command
ppcsim --example
```

### Project Structure

```
Ppcsim/
├── ppcsim.py       # Main simulator implementation
├── setup.py        # Package setup script
├── Readme.md       # This file
└── LICENSE         # License file (if applicable)
```

## License

This project is provided as-is for educational purposes.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Roadmap

Future enhancements may include:
- More PowerPC instructions
- Floating-point support
- Interactive debugger
- Assembly language parser
- Performance counters
- Cache simulation
