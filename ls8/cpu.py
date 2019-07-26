"""CPU functionality."""
import sys
class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        self.ram = [00000000] * 256 # 256 max memory
        self.reg = [0] * 8 # 8 gen purpose registers
        self.pc = 0
        self.fl = 0b00000000
        self.branchtable = {}
        self.branchtable[0b00000001] = self.op_hlt
        self.branchtable[0b10000010] = self.op_ldi
        self.branchtable[0b01000111] = self.op_prn
        self.branchtable[0b10100010] = self.op_mul
        self.branchtable[0b01000101] = self.op_push
        self.branchtable[0b01000110] = self.op_pop
        self.branchtable[0b01010000] = self.op_call
        self.branchtable[0b00010001] = self.op_ret
        self.branchtable[0b10100000] = self.op_add
        self.branchtable[0b10100111] = self.op_cmp
        self.branchtable[0b01010101] = self.op_jeq
        self.branchtable[0b01010110] = self.op_jne
        self.branchtable[0b01010100] = self.op_jmp
        self.running = True
        self.IR = 0
        self.reg[7] = 0xF4
        self.sp = self.reg[7]
    def ram_read(self, mar):
        return self.ram[mar]
    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr
    def load(self):
        """Load a program into memory."""
        address = 0
        file = sys.argv[1]
        # For now, we've just hardcoded a program:
        program = [
            # From print8.ls8
            # 0b10000010, # LDI R0,8
            # 0b00000000,
            # 0b00001000,
            # 0b01000111, # PRN R0
            # 0b00000000,
            # 0b00000001, # HLT
        ]
        with open(file, 'r') as data:
            for x in data:
                line = x.split('#', 1)[0]
                if line.strip() == '':
                    continue
                program.append(int(line, 2))
            for instruction in program:
                self.ram[address] = instruction
                address += 1
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            else:
                self.fl = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")
    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()
    def op_hlt(self):
        self.running = False
        sys.exit(1)
    def op_ldi(self):
        reg_add = self.ram[self.pc + 1]
        reg_val = self.ram[self.pc + 2]
        # self.ram_write(reg_add, reg_val)
        self.reg[reg_add] = reg_val
        self.pc += 3
    def op_prn(self):
        reg_add = self.ram[self.pc + 1]
        print(self.reg[reg_add])
        self.pc += 2
    def op_mul(self):
        reg_add_a = self.ram[self.pc + 1]
        reg_add_b = self.ram[self.pc + 2]
        self.alu("MUL", reg_add_a, reg_add_b)
        self.pc += 3
    def op_add(self):
        reg_add_a = self.ram[self.pc + 1]
        reg_add_b = self.ram[self.pc + 2]
        self.alu("ADD", reg_add_a, reg_add_b)
        self.pc += 3
    def op_cmp(self):
        reg_add_a = self.ram[self.pc + 1]
        reg_add_b = self.ram[self.pc + 2]
        self.alu("CMP", reg_add_a, reg_add_b)
        self.pc += 3
    def op_jeq(self):
        if self.fl == 0b00000001:
            self.op_jmp()
        else:
            self.pc += 2
    def op_jne(self):
        if self.fl != 0b00000001:
            self.op_jmp()
        else:
            self.pc += 2
    def op_jmp(self):
        operand_a = self.ram[self.pc + 1]
        self.pc = self.reg[operand_a]
    def op_push(self):
        self.sp -= 1
        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]
        self.ram[self.sp] = value
        self.pc += 2
    def op_pop(self):
        value = self.ram[self.sp]
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value
        self.sp += 1
        self.pc += 2
    def op_call(self):
        return_addr = self.pc + 2
        self.sp -= 1
        self.ram[self.sp] = return_addr
        reg_num = self.ram[self.pc + 1]
        subroutine_addr = self.reg[reg_num]
        self.pc = subroutine_addr
    def op_ret(self):
        return_addr = self.ram[self.sp]
        self.sp += 1
        self.pc = return_addr
    def run(self):
        """Run the CPU."""
        # self.trace()
        while self.running:
            command = self.ram[self.pc]
            if command in self.branchtable:
                self.branchtable[command]()
            else:
                print(f'unknown instruction {command}\n')
                sys.exit(1)