"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [00000000] * 255  # 256 max memory
        self.register = [0] * 8  # 8 gen purpose registers
        self.pc = 0

    def ram_read(self, mar):

        print(self.ram[mar])

    def ram_write(self, mar, mdr):

        self.ram[mar] = mdr

    def load(self):
        """Load a program into memory."""

        address = 0
        file = sys.argv[1]
        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            # 0b10000010,  # LDI R0,8
            # 0b00000000,
            # 0b00001000,
            # 0b01000111,  # PRN R0
            # 0b00000000,
            # 0b00000001,  # HLT
        ]

        f = open(file, 'r')
        f1 = f.readlines()
        for x in f1:
            if x[0] != '#':
                if x != '\n':
                    program.append(int(x[0:8], 2))

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.ram[reg_a] += self.ram[reg_b]
        elif op == "SUB":
            self.ram[reg_a] -= self.ram[reg_b]
        elif op == "MUL":
            self.ram[reg_a] = self.ram[reg_a] * self.ram[reg_b]
        elif op == "DIV":
            self.ram[reg_a] /= self.ram[reg_b]
        elif op == "MOD":
            self.ram[reg_a] %= self.ram[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        IR = 0
        running = True

        while running:
            command = self.ram[IR]

            if command == 0b10000010:
                reg_add = self.ram[IR + 1]
                reg_val = self.ram[IR + 2]
                self.ram_write(reg_add, reg_val)
                IR += 3

            elif command == 0b01000111:
                reg_add = self.ram[IR + 1]
                self.ram_read(reg_add)
                IR += 2

            elif command == 0b00000001:
                running = False
                sys.exit(1)

            elif command == 0b10100010:
                reg_add_a = self.ram[IR + 1]
                reg_add_b = self.ram[IR + 2]
                self.alu("MUL", reg_add_a, reg_add_b)
                IR += 3

            else:
                print(f'unknown instruction {command}')
                sys.exit(1)
