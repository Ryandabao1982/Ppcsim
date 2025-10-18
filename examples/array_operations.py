#!/usr/bin/env python3
"""
Example: Array sum calculator using Ppcsim
Demonstrates memory operations with arrays
"""

import sys
import os
# Add parent directory to path so we can import ppcsim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ppcsim import PPCSimulator


def array_sum_example():
    """Calculate the sum of an array stored in memory."""
    print("Array Sum Calculator")
    print("="*50)
    
    sim = PPCSimulator(memory_size=1024)
    
    # Array values to sum: [10, 20, 30, 40, 50]
    # We'll store them in memory starting at address 0x100
    array_values = [10, 20, 30, 40, 50]
    array_addr = 0x100
    
    # Store array in memory manually
    for i, val in enumerate(array_values):
        addr = array_addr + (i * 4)
        sim.memory[addr] = (val >> 24) & 0xFF
        sim.memory[addr + 1] = (val >> 16) & 0xFF
        sim.memory[addr + 2] = (val >> 8) & 0xFF
        sim.memory[addr + 3] = val & 0xFF
    
    print(f"\nArray stored at address 0x{array_addr:04x}: {array_values}")
    print(f"Expected sum: {sum(array_values)}")
    
    # Program to sum the array:
    # r1 = base address of array
    # r2 = sum accumulator
    # r3 = current element
    # r4 = offset
    program = [
        0x38200100,  # addi r1, r0, 0x100    # base address
        0x38400000,  # addi r2, r0, 0        # sum = 0
        0x38800000,  # addi r4, r0, 0        # offset = 0
        
        # Load and add first element
        0x7CA40214,  # add r5, r4, r1        # r5 = base + offset
        0x80A50000,  # lwz r3, 0(r5)         # load element
        0x7C431214,  # add r2, r3, r2        # sum += element
        0x38840004,  # addi r4, r4, 4        # offset += 4
        
        # Load and add second element
        0x7CA40214,  # add r5, r4, r1
        0x80A50000,  # lwz r3, 0(r5)
        0x7C431214,  # add r2, r3, r2
        0x38840004,  # addi r4, r4, 4
        
        # Load and add third element
        0x7CA40214,  # add r5, r4, r1
        0x80A50000,  # lwz r3, 0(r5)
        0x7C431214,  # add r2, r3, r2
        0x38840004,  # addi r4, r4, 4
        
        # Load and add fourth element
        0x7CA40214,  # add r5, r4, r1
        0x80A50000,  # lwz r3, 0(r5)
        0x7C431214,  # add r2, r3, r2
        0x38840004,  # addi r4, r4, 4
        
        # Load and add fifth element
        0x7CA40214,  # add r5, r4, r1
        0x80A50000,  # lwz r3, 0(r5)
        0x7C431214,  # add r2, r3, r2
        
        0x00000000,  # halt
    ]
    
    sim.load_program(program, start_address=0)
    sim.run(max_instructions=100)
    
    print(f"\nAfter execution:")
    print(f"  Sum (in r2): {sim.registers[2]}")
    print(f"  Last offset (r4): {sim.registers[4]}")
    
    if sim.registers[2] == sum(array_values):
        print("\n✓ Success! Sum calculated correctly.")
    else:
        print(f"\n✗ Error: Expected {sum(array_values)}, got {sim.registers[2]}")


def memory_copy_example():
    """Copy data from one memory location to another."""
    print("\n" + "="*50)
    print("Memory Copy Example")
    print("="*50)
    
    sim = PPCSimulator(memory_size=1024)
    
    # Source data at 0x100
    src_addr = 0x100
    dst_addr = 0x200
    value = 0xDEADBEEF
    
    # Store value at source
    sim.memory[src_addr] = (value >> 24) & 0xFF
    sim.memory[src_addr + 1] = (value >> 16) & 0xFF
    sim.memory[src_addr + 2] = (value >> 8) & 0xFF
    sim.memory[src_addr + 3] = value & 0xFF
    
    print(f"\nSource address: 0x{src_addr:04x}")
    print(f"Destination address: 0x{dst_addr:04x}")
    print(f"Value to copy: 0x{value:08x}")
    
    # Program to copy memory
    program = [
        0x38200100,  # addi r1, r0, 0x100   # src address
        0x38400200,  # addi r2, r0, 0x200   # dst address
        0x80610000,  # lwz r3, 0(r1)        # load from src
        0x90640000,  # stw r3, 0(r2)        # store to dst
        0x00000000,  # halt
    ]
    
    sim.load_program(program, start_address=0)
    sim.run()
    
    # Read back from destination
    result = (sim.memory[dst_addr] << 24 |
              sim.memory[dst_addr + 1] << 16 |
              sim.memory[dst_addr + 2] << 8 |
              sim.memory[dst_addr + 3])
    
    print(f"\nAfter execution:")
    print(f"  Value at destination: 0x{result:08x}")
    print(f"  Value in r3: 0x{sim.registers[3]:08x}")
    
    if result == value:
        print("\n✓ Success! Memory copied correctly.")
    else:
        print(f"\n✗ Error: Expected 0x{value:08x}, got 0x{result:08x}")


if __name__ == '__main__':
    array_sum_example()
    memory_copy_example()
