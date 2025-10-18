#!/usr/bin/env python3
"""
Test suite for Ppcsim - PowerPC Simulator
"""

from ppcsim import PPCSimulator


def test_addition():
    """Test basic addition."""
    print("Test 1: Addition")
    sim = PPCSimulator()
    program = [
        0x38200005,  # addi r1, r0, 5
        0x3840000A,  # addi r2, r0, 10
        0x7C611214,  # add r3, r1, r2
        0x00000000,  # halt
    ]
    sim.load_program(program)
    sim.run()
    assert sim.registers[1] == 5, f"Expected r1=5, got {sim.registers[1]}"
    assert sim.registers[2] == 10, f"Expected r2=10, got {sim.registers[2]}"
    assert sim.registers[3] == 15, f"Expected r3=15, got {sim.registers[3]}"
    print("  ✓ Passed: 5 + 10 = 15")


def test_subtraction():
    """Test subtraction."""
    print("Test 2: Subtraction")
    sim = PPCSimulator()
    program = [
        0x38200064,  # addi r1, r0, 100
        0x38400032,  # addi r2, r0, 50
        0x7C620850,  # subf r3, r2, r1
        0x00000000,  # halt
    ]
    sim.load_program(program)
    sim.run()
    assert sim.registers[3] == 50, f"Expected r3=50, got {sim.registers[3]}"
    print("  ✓ Passed: 100 - 50 = 50")


def test_logical_or():
    """Test logical OR."""
    print("Test 3: Logical OR")
    sim = PPCSimulator()
    program = [
        0x382000F0,  # addi r1, r0, 0xF0
        0x3840000F,  # addi r2, r0, 0x0F
        0x7C231378,  # or r3, r1, r2
        0x00000000,  # halt
    ]
    sim.load_program(program)
    sim.run()
    assert sim.registers[3] == 0xFF, f"Expected r3=0xFF, got {sim.registers[3]:02x}"
    print("  ✓ Passed: 0xF0 | 0x0F = 0xFF")


def test_memory_operations():
    """Test memory store and load."""
    print("Test 4: Memory Operations")
    sim = PPCSimulator()
    program = [
        0x38600042,  # addi r3, r0, 0x42
        0x90610010,  # stw r3, 0x10(r1)
        0x80810010,  # lwz r4, 0x10(r1)
        0x00000000,  # halt
    ]
    sim.load_program(program)
    sim.run()
    assert sim.registers[4] == 0x42, f"Expected r4=0x42, got {sim.registers[4]:02x}"
    print("  ✓ Passed: Store and load 0x42")


def test_immediate_shifted():
    """Test addis (add immediate shifted)."""
    print("Test 5: Add Immediate Shifted")
    sim = PPCSimulator()
    program = [
        0x3C601234,  # addis r3, r0, 0x1234
        0x00000000,  # halt
    ]
    sim.load_program(program)
    sim.run()
    assert sim.registers[3] == 0x12340000, f"Expected r3=0x12340000, got {sim.registers[3]:08x}"
    print("  ✓ Passed: addis creates 0x12340000")


def test_complex_calculation():
    """Test complex calculation."""
    print("Test 6: Complex Calculation")
    sim = PPCSimulator()
    program = [
        0x38200005,  # addi r1, r0, 5
        0x3840000A,  # addi r2, r0, 10
        0x7C611214,  # add r3, r1, r2    # r3 = 15
        0x3880000F,  # addi r4, r0, 15
        0x7CA32214,  # add r5, r3, r4    # r5 = 30
        0x00000000,  # halt
    ]
    sim.load_program(program)
    sim.run()
    assert sim.registers[5] == 30, f"Expected r5=30, got {sim.registers[5]}"
    print("  ✓ Passed: (5 + 10) + 15 = 30")


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("  Ppcsim Test Suite")
    print("="*50 + "\n")
    
    tests = [
        test_addition,
        test_subtraction,
        test_logical_or,
        test_memory_operations,
        test_immediate_shifted,
        test_complex_calculation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ Failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1
        print()
    
    print("="*50)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*50 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    exit(main())
