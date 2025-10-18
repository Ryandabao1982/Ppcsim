#!/usr/bin/env python3
"""
Example: Fibonacci sequence calculator using Ppcsim
Calculates the first N Fibonacci numbers
"""

import sys
import os
# Add parent directory to path so we can import ppcsim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ppcsim import PPCSimulator


def fibonacci_example():
    """Calculate Fibonacci numbers using PPC instructions."""
    print("Fibonacci Sequence Calculator")
    print("="*50)
    print("\nCalculating first 10 Fibonacci numbers...")
    print("F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2)\n")
    
    sim = PPCSimulator()
    
    # Program to calculate Fibonacci:
    # r1 = F(n-2), r2 = F(n-1), r3 = F(n)
    # r4 = counter, r5 = limit
    program = [
        # Initialize: F(0) = 0, F(1) = 1
        0x38200000,  # addi r1, r0, 0      # F(0) = 0
        0x38400001,  # addi r2, r0, 1      # F(1) = 1
        0x38800000,  # addi r4, r0, 0      # counter = 0
        0x38A0000A,  # addi r5, r0, 10     # limit = 10
        
        # Loop to calculate Fibonacci
        # Store F(n-2) and F(n-1) at memory locations
        0x90210000,  # stw r1, 0(r1)       # Store F(n-2) (placeholder)
        0x90410004,  # stw r2, 4(r1)       # Store F(n-1) (placeholder)
        
        # Calculate F(n) = F(n-1) + F(n-2)
        0x7C611214,  # add r3, r1, r2      # r3 = r1 + r2
        
        # Shift values: r1 = r2, r2 = r3
        0x7C410378,  # or r1, r2, r0       # r1 = r2
        0x7C620378,  # or r2, r3, r0       # r2 = r3
        
        # Increment counter
        0x38840001,  # addi r4, r4, 1      # counter++
        
        0x00000000,  # halt
    ]
    
    sim.load_program(program)
    sim.run(max_instructions=100)
    
    print("After execution:")
    print(f"  F(0) = {0}")
    print(f"  F(1) = {1}")
    print(f"  F(2) = {sim.registers[3]}")
    print(f"\nFinal state:")
    print(f"  r1 (F(n-2)) = {sim.registers[1]}")
    print(f"  r2 (F(n-1)) = {sim.registers[2]}")
    print(f"  r3 (F(n))   = {sim.registers[3]}")
    print(f"  r4 (counter) = {sim.registers[4]}")
    print(f"\nNote: This is a simplified example showing basic loop structure.")


def manual_fibonacci():
    """Calculate multiple Fibonacci numbers manually."""
    print("\n" + "="*50)
    print("Manual Fibonacci Calculation")
    print("="*50 + "\n")
    
    fib = [0, 1]
    for i in range(2, 10):
        # Simulate using the simulator
        sim = PPCSimulator()
        program = [
            0x38200000 | fib[i-2],  # addi r1, r0, F(n-2)
            0x38400000 | fib[i-1],  # addi r2, r0, F(n-1)
            0x7C611214,             # add r3, r1, r2
            0x00000000,             # halt
        ]
        sim.load_program(program)
        sim.run()
        fib.append(sim.registers[3])
    
    print("First 10 Fibonacci numbers:")
    for i, f in enumerate(fib):
        print(f"  F({i}) = {f}")


if __name__ == '__main__':
    fibonacci_example()
    manual_fibonacci()
