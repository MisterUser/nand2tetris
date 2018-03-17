class Parser():
    def __init__(self, input_file):
        self.input_file = input_file
        self.comm_type = None
        self.arg1 = None
        self._arg2 = None
        self.l_arithmetic = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']

        self.vm_code = list()

        with open(input_file) as _if:
            for line in _if:
                code_line = line.split('//')[0]

                # nothing before comment (pure comment line)
                if not code_line.strip():
                    continue

                code_line = code_line.rstrip()
                self.vm_code.append(code_line)

        self.num_lines = len(self.vm_code)
        print('{} commands.'.format(self.num_lines))

        self.code_iter = 0

    def has_more_commands(self):
        return True if self.code_iter < self.num_lines else False 

    def parse_line(self, curr_line):
        parsed_command = curr_line.split()
        if not parsed_command:
            return

        if parsed_command[0] in self.l_arithmetic:
            self.comm_type = 'c_arithmetic'
            self.arg1 = parsed_command[0]
            return

        elif parsed_command[0] == 'push':
            self.comm_type = 'c_push'
            self.arg1 = parsed_command[1]
            self.arg2 = parsed_command[2]
        elif parsed_command[0] == 'pop':
            self.comm_type = 'c_pop'
            self.arg1 = parsed_command[1]
            self.arg2 = parsed_command[2]
        else:
            return


    def advance(self):
        # while True:
            # yield self.vm_code[self.code_iter]

        curr_line = self.vm_code[self.code_iter]

        self.parse_line(curr_line)

        self.code_iter += 1

        return self.comm_type, self.arg1, self.arg2


    @property
    def arg2(self):
        if self.comm_type in ['c_push', 'c_pop', 'c_function', 'c_call']:
            return self._arg2
        else:
            return None

    @arg2.setter
    def arg2(self, value):
        self._arg2 = value

class CodeWriter():
    def __init__(self, output_file):
        self.filename = output_file
        self.fh = open(output_file, 'w')
        self.num_eq = 0

    def set_file_name(self, fn):
        self.fh = fn

    def close(self):
        self.fh.close()

    def load_ptr_val(self, addr, dest):
        '''
        :param: addr : string
        :param: dest : 'A' or 'D'
        '''
        self.fh.write('@{}\r'.format(addr))
        self.fh.write('A=M\r')
        self.fh.write('{}=M\r'.format(dest))

    def set_ptr_val(self, addr, src):
        '''
        :param: addr : string
        :param: src : 'A' or 'D'
        '''
        self.fh.write('@{}\r'.format(addr))
        self.fh.write('A=M\r')
        self.fh.write('M={}\r'.format(src))

    def decr_ptr(self, addr):
        self.fh.write('@{}\r'.format(addr))
        self.fh.write('M=M-1\r')

    def incr_ptr(self, addr):
        self.fh.write('@{}\r'.format(addr))
        self.fh.write('M=M+1\r')

    def pop_stack_to_temp(self, index):
        self.pop_stack_to('D')

        # write D into temp
        self.fh.write('@R{}\r'.format(5 + int(index)))
        self.fh.write('M=D\r')

    def pop_stack_to_static(self, vm_filename, index):
        # self.decr_ptr('SP')
        # load stack val into D
        # self.fh.write('@SP\r')
        # self.fh.write('A=M\r')
        # self.fh.write('D=M\r')
        self.pop_stack_to('D')

        # write D into static
        self.fh.write('@{}.{}\r'.format(vm_filename, index))
        self.fh.write('M=D\r')

    def pop_stack_with_index(self, dest, index):
        self.decr_ptr('SP')
        # load address of segment + index into R15
        self.fh.write('@{}\r'.format(dest))
        self.fh.write('D=M\r')
        self.fh.write('@{}\r'.format(index))
        self.fh.write('D=D+A\r')
        # write into memory address
        self.fh.write('@R15\r'.format(index))
        self.fh.write('M=D\r')

        # load stack val into D
        # self.fh.write('@SP\r')
        # self.fh.write('A=M\r')
        # self.fh.write('D=M\r')
        self.load_ptr_val('SP', 'D')

        self.fh.write('@R15\r'.format(index))
        self.fh.write('A=M\r')
        self.fh.write('M=D\r')

    def pop_stack_to(self, dest):
        self.decr_ptr('SP')
        self.load_ptr_val('SP', '{}'.format(dest))

    def push_to_stack_from_temp(self, index):
        self.fh.write('@R{}\r'.format(5 + int(index)))
        self.fh.write('D=M\r')

        # psh value onto stack
        # self.fh.write('@SP\r')
        # self.fh.write('A=M\r')
        # self.fh.write('M=D\r')
        # self.incr_ptr('SP')
        self.push_to_stack_from('D')

    def push_to_stack_from_static(self, vm_filename, index):
        self.fh.write('@{}.{}\r'.format(vm_filename, index))
        self.fh.write('D=M\r')

        # psh value onto stack
        # self.fh.write('@SP\r')
        # self.fh.write('A=M\r')
        # self.fh.write('M=D\r')
        # self.incr_ptr('SP')
        self.push_to_stack_from('D')

    def push_to_stack_with_index(self, src, index):
        # load value of segment + index into D
        self.fh.write('@{}\r'.format(src))
        self.fh.write('D=M\r')
        self.fh.write('@{}\r'.format(index))
        self.fh.write('D=D+A\r')
        self.fh.write('A=D\r')
        self.fh.write('D=M\r')

        # psh value onto stack
        # self.fh.write('@SP\r')
        # self.fh.write('A=M\r')
        # self.fh.write('M=D\r')
        self.set_ptr_val('SP', 'D')
        self.incr_ptr('SP')

    def push_to_stack_from(self, src):
        self.set_ptr_val('SP', '{}'.format(src))
        self.incr_ptr('SP')

    def bool_ops(self, command):
        # true = -1, false = 0
        # subtract to get diff in D
        self.fh.write('D=M-D\r')

        self.fh.write('@EQ_COND{}\r'.format(self.num_eq))

        # jump to EQ_COND if D==0 (numbers are equal)
        if command == 'eq':
            self.fh.write('D;JEQ\r')
        # jump to EQ_COND if D>0 (x > y)
        if command == 'gt':
            self.fh.write('D;JGT\r')
        # jump to EQ_COND if D<0 (x < y)
        if command == 'lt':
            self.fh.write('D;JLT\r')

        # else (not equal), D=0 then jump to EQ_END
        self.fh.write('D=0\r')
        self.fh.write('@EQ_END{}\r'.format(self.num_eq))
        self.fh.write('0;JMP\r')

        # if numbers equal, set D=-1
        self.fh.write('(EQ_COND{})\r'.format(self.num_eq))
        self.fh.write('D=-1\r')

        # end (increment label number)
        self.fh.write('(EQ_END{})\r'.format(self.num_eq))
        self.num_eq += 1

    def write_arithmetic(self, command):
        # every command first pops a value into D
        self.pop_stack_to('D')

        if command == 'neg':
            self.fh.write('D=-D\r')
            self.push_to_stack_from('D')
            return

        if command == 'not':
            self.fh.write('D=!D\r')
            self.push_to_stack_from('D')
            return

        # binary operators
        self.decr_ptr('SP')
        self.fh.write('@SP\r')
        self.fh.write('A=M\r')
        if command == 'add':
            self.fh.write('D=D+M\r')
        if command == 'sub':
            self.fh.write('D=M-D\r')
        if command == 'and':
            self.fh.write('D=D&M\r')
        if command == 'or':
            self.fh.write('D=D|M\r')
        if command in ['eq', 'gt', 'lt']:
            self.bool_ops(command)

        self.push_to_stack_from('D')

    def write_push_pop(self, command, segment, index):
        if segment == 'constant':
            self.fh.write('@{}\r'.format(index))
            self.fh.write('D=A\r')
            self.push_to_stack_from('D')
            return
        elif segment == 'static':
            _fn = self.filename.split('.')[-2].split('/')[-1]
            if command == 'c_push':
                self.push_to_stack_from_static(_fn, index)
            elif command == 'c_pop':
                self.pop_stack_to_static(_fn, index)
            return
        elif segment == 'temp':
            if command == 'c_push':
                self.push_to_stack_from_temp(index)
            elif command == 'c_pop':
                self.pop_stack_to_temp(index)
            return
        elif segment == 'pointer':
            if index == '0':
                ptr = 'THIS'
            elif index == '1':
                ptr = 'THAT'
            else:
                print('Invalid pointer index')
                return

            if command == 'c_push':
                self.fh.write('@{}\r'.format(ptr))
                self.fh.write('D=M\r')
                self.push_to_stack_from('D')

            elif command == 'c_pop':
                self.pop_stack_to('D')
                self.fh.write('@{}\r'.format(ptr))
                self.fh.write('M=D\r')

            return

        elif segment == 'argument':
            seg = 'ARG'
        elif segment == 'local':
            seg = 'LCL'
        elif segment == 'this':
            seg = 'THIS'
        elif segment == 'that':
            seg = 'THAT'
        else:
            print('Segment not supported.')
            return

        if command == 'c_push':
            self.push_to_stack_with_index(seg, index)
        elif command == 'c_pop':
            self.pop_stack_with_index(seg, index)


if __name__ == '__main__':
    import sys
    vm_file_name = sys.argv[1]
    print(vm_file_name)
    parser = Parser(vm_file_name)
    asm_filename = vm_file_name.split('.')[-2] + '.asm'
    print(asm_filename)
    writer = CodeWriter(asm_filename)

    while parser.has_more_commands():
        comm, arg1, arg2 = parser.advance()
        print(comm, arg1, arg2)
        if comm == 'c_arithmetic':
            writer.write_arithmetic(arg1)
        elif comm in ['c_push', 'c_pop']:
            writer.write_push_pop(comm, arg1, arg2)

    writer.close()
