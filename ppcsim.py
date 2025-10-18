#!/usr/bin/env python3
"""
Ppcsim - A Simple PowerPC Simulator
A basic PowerPC instruction set simulator for educational purposes.
"""

import sys
import argparse
from typing import Dict, List, Optional


class PPCSimulator:
    """PowerPC CPU Simulator with basic instruction set support."""
    
    def __init__(self, memory_size: int = 65536):
        """
        Initialize the PPC simulator.
        
        Args:
            memory_size: Size of memory in bytes (default 64KB)
        """
        # General Purpose Registers (r0-r31)
        self.registers = [0] * 32
        
        # Special Purpose Registers
        self.pc = 0  # Program Counter
        self.lr = 0  # Link Register
        self.ctr = 0  # Count Register
        self.cr = 0  # Condition Register
        
        # Memory
        self.memory_size = memory_size
        self.memory = bytearray(memory_size)
        
        # Execution control
        self.running = False
        self.instruction_count = 0
        
    def load_program(self, program: List[int], start_address: int = 0):
        """
        Load a program into memory.
        
        Args:
            program: List of 32-bit instructions
            start_address: Memory address to load program at
        """
        for i, instruction in enumerate(program):
            addr = start_address + (i * 4)
            if addr + 3 < self.memory_size:
                self.memory[addr] = (instruction >> 24) & 0xFF
                self.memory[addr + 1] = (instruction >> 16) & 0xFF
                self.memory[addr + 2] = (instruction >> 8) & 0xFF
                self.memory[addr + 3] = instruction & 0xFF
        
        self.pc = start_address
        
    def fetch_instruction(self) -> int:
        """Fetch the next instruction from memory."""
        if self.pc + 3 >= self.memory_size:
            raise RuntimeError(f"Program counter out of bounds: {self.pc}")
        
        instruction = (self.memory[self.pc] << 24 | 
                      self.memory[self.pc + 1] << 16 |
                      self.memory[self.pc + 2] << 8 | 
                      self.memory[self.pc + 3])
        return instruction
    
    def decode_execute(self, instruction: int):
        """Decode and execute an instruction."""
        opcode = (instruction >> 26) & 0x3F
        
        # Handle different instruction formats
        if opcode == 14:  # addi - Add Immediate
            rt = (instruction >> 21) & 0x1F
            ra = (instruction >> 16) & 0x1F
            si = instruction & 0xFFFF
            # Sign extend immediate
            if si & 0x8000:
                si = si - 0x10000
            self.registers[rt] = (self.registers[ra] + si) & 0xFFFFFFFF
            self.pc += 4
            
        elif opcode == 15:  # addis - Add Immediate Shifted
            rt = (instruction >> 21) & 0x1F
            ra = (instruction >> 16) & 0x1F
            si = instruction & 0xFFFF
            # Sign extend and shift immediate
            if si & 0x8000:
                si = si - 0x10000
            self.registers[rt] = (self.registers[ra] + (si << 16)) & 0xFFFFFFFF
            self.pc += 4
            
        elif opcode == 24:  # ori - OR Immediate
            rs = (instruction >> 21) & 0x1F
            ra = (instruction >> 16) & 0x1F
            ui = instruction & 0xFFFF
            self.registers[ra] = (self.registers[rs] | ui) & 0xFFFFFFFF
            self.pc += 4
            
        elif opcode == 32:  # lwz - Load Word and Zero
            rt = (instruction >> 21) & 0x1F
            ra = (instruction >> 16) & 0x1F
            d = instruction & 0xFFFF
            if d & 0x8000:
                d = d - 0x10000
            addr = (self.registers[ra] + d) & 0xFFFFFFFF
            if addr + 3 < self.memory_size:
                word = (self.memory[addr] << 24 | 
                       self.memory[addr + 1] << 16 |
                       self.memory[addr + 2] << 8 | 
                       self.memory[addr + 3])
                self.registers[rt] = word
            self.pc += 4
            
        elif opcode == 36:  # stw - Store Word
            rs = (instruction >> 21) & 0x1F
            ra = (instruction >> 16) & 0x1F
            d = instruction & 0xFFFF
            if d & 0x8000:
                d = d - 0x10000
            addr = (self.registers[ra] + d) & 0xFFFFFFFF
            if addr + 3 < self.memory_size:
                word = self.registers[rs]
                self.memory[addr] = (word >> 24) & 0xFF
                self.memory[addr + 1] = (word >> 16) & 0xFF
                self.memory[addr + 2] = (word >> 8) & 0xFF
                self.memory[addr + 3] = word & 0xFF
            self.pc += 4
            
        elif opcode == 31:  # Extended opcodes
            xo = (instruction >> 1) & 0x3FF
            
            if xo == 266:  # add
                rt = (instruction >> 21) & 0x1F
                ra = (instruction >> 16) & 0x1F
                rb = (instruction >> 11) & 0x1F
                self.registers[rt] = (self.registers[ra] + self.registers[rb]) & 0xFFFFFFFF
                self.pc += 4
                
            elif xo == 40:  # subf - Subtract From
                rt = (instruction >> 21) & 0x1F
                ra = (instruction >> 16) & 0x1F
                rb = (instruction >> 11) & 0x1F
                self.registers[rt] = (self.registers[rb] - self.registers[ra]) & 0xFFFFFFFF
                self.pc += 4
                
            elif xo == 444:  # or
                rs = (instruction >> 21) & 0x1F
                ra = (instruction >> 16) & 0x1F
                rb = (instruction >> 11) & 0x1F
                self.registers[ra] = (self.registers[rs] | self.registers[rb]) & 0xFFFFFFFF
                self.pc += 4
                
            elif xo == 28:  # and
                rs = (instruction >> 21) & 0x1F
                ra = (instruction >> 16) & 0x1F
                rb = (instruction >> 11) & 0x1F
                self.registers[ra] = (self.registers[rs] & self.registers[rb]) & 0xFFFFFFFF
                self.pc += 4
                
            else:
                self.pc += 4  # Skip unknown extended instruction
                
        elif opcode == 18:  # b - Branch (simplified)
            li = instruction & 0x3FFFFFC
            if li & 0x2000000:
                li = li - 0x4000000
            self.pc = (self.pc + li) & 0xFFFFFFFF
            
        elif opcode == 0:  # Special case - halt/nop
            if instruction == 0:
                self.running = False
            else:
                self.pc += 4
        else:
            # Unknown instruction - skip
            self.pc += 4
    
    def run(self, max_instructions: int = 10000):
        """
        Run the simulator.
        
        Args:
            max_instructions: Maximum number of instructions to execute
        """
        self.running = True
        self.instruction_count = 0
        
        while self.running and self.instruction_count < max_instructions:
            try:
                instruction = self.fetch_instruction()
                self.decode_execute(instruction)
                self.instruction_count += 1
            except Exception as e:
                print(f"Error at PC={self.pc:08x}: {e}")
                break
    
    def print_state(self):
        """Print the current state of the simulator."""
        print("\n=== CPU State ===")
        print(f"PC: 0x{self.pc:08x}  Instructions: {self.instruction_count}")
        print("\nGeneral Purpose Registers:")
        for i in range(0, 32, 4):
            print(f"  r{i:2d}: 0x{self.registers[i]:08x}  "
                  f"r{i+1:2d}: 0x{self.registers[i+1]:08x}  "
                  f"r{i+2:2d}: 0x{self.registers[i+2]:08x}  "
                  f"r{i+3:2d}: 0x{self.registers[i+3]:08x}")
        print(f"\nSpecial Registers:")
        print(f"  LR: 0x{self.lr:08x}  CTR: 0x{self.ctr:08x}  CR: 0x{self.cr:08x}")
        print()


def run_example():
    """Run an example program."""
    print("Running example program...")
    print("\nProgram: Calculate sum of 5 + 10 + 15")
    
    # Create simulator
    sim = PPCSimulator()
    
    # Simple program:
    # addi r1, r0, 5    # r1 = 5
    # addi r2, r0, 10   # r2 = 10  
    # add  r3, r1, r2   # r3 = r1 + r2 = 15
    # addi r4, r0, 15   # r4 = 15
    # add  r5, r3, r4   # r5 = r3 + r4 = 30
    program = [
        0x38200005,  # addi r1, r0, 5
        0x3840000A,  # addi r2, r0, 10
        0x7C611214,  # add r3, r1, r2
        0x3880000F,  # addi r4, r0, 15
        0x7CA32214,  # add r5, r3, r4
        0x00000000,  # halt
    ]
    
    sim.load_program(program)
    sim.run()
    sim.print_state()
    
    print(f"Result: r5 = {sim.registers[5]} (expected: 30)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Ppcsim - A Simple PowerPC Simulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --example          Run example program
  %(prog)s --help             Show this help message
        """
    )
    
    parser.add_argument('--example', action='store_true',
                       help='Run an example program')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    args = parser.parse_args()
    
    if args.example:
        run_example()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
