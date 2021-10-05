#!/usr/bin/env python
# coding: utf-8

# In[265]:


#load a specified mips text file
#generate the assembly code equivalent to the input file (disassembler)

#Generate instruction by instruction simulation of the MIPS code (simulator)
#produce/print the contents of registers and data memories after each execution of each instruction
#TODO: find out why lock_data keeps changing despite being a locked saved format of input data.




#category-1
import sys

def main(argv):
    
    file = argv

    cat_1 = '000'
    J='000'
    BEQ='001'
    BNE='010'
    BGTZ='011'
    SW='100'
    LW='101'
    BREAK='110'
    cat1 = [cat_1,J,BEQ,BNE,BGTZ,SW,LW,BREAK]


    # In[267]:


    #category-2
    cat_2 = '001'
    ADD='000'
    SUB='001'
    AND='010'
    OR='011'
    SRL='100'
    SRA='101'
    MUL='110'
    cat2 = [cat_2,ADD,SUB,AND,OR,SRL,SRA,MUL]


    # In[268]:


    #category-3
    cat_3 = '010'
    ADDI='000'
    ANDI='001'
    ORI='010'
    cat3 = [cat_3,ADDI,ANDI,ORI]


    # In[269]:


    #Global variables

    input_instr = []

    cat = [cat1,cat2,cat3]

    registers = [0] * 32 #only write
    data = [0] * 16 #only read


    # In[270]:


    def convert(val):
        tmp = val.strip()
        tmp = ''.join('1' if x == '0' else '0' for x in tmp)
        tmp = int(tmp,2) + 1
        return tmp*-1


    # In[271]:


    def twos_complement(sample):
        if(sample[0]=='1'): #negative bit
            return convert(sample)

        elif(sample[0]=='0'): #positive bit
            return int(sample,2)


    # In[272]:


    #read from file and print contents
    address = 260
    data_break = address
    f_dis = open(file, "r")
    w_dis = open("disassembly.txt", "w")

    for x in f_dis:
        input_instr.append(x)

    break_index = 0
    broken = False
    for index in range(len(input_instr)):
        instr = input_instr[index]
        input_cat = instr[:6]
        if( input_cat == cat_1 + BREAK and not broken):
            break_index = index + 1 # +! because current instruction is break, not a read in value
            broken = True
            data_break = address + 4 #with sample this should result in 316, but change otherwise
        address = address + 4


    for index in range(len(input_instr) - break_index-1):
        data[index] = twos_complement(input_instr[index+break_index])

    lock_data = [i for i in data]


    # In[273]:


    #category 1 function
    def cat_1_func(sample,break_exc):

        input_cat = sample[0:3]
        opcode = sample[3:6]

        rs = int(sample[6:11],2)
        rt = int(sample[11:16],2)

        offset = sample[16:32]
        branch_offset = offset
        offset = offset.strip() + '00'

        output = ""
        branch = 0

        if(opcode == J):
            instr_index = sample[8:]
            instr_index = instr_index.strip() + '00'
            instr_index_int = int(instr_index, 2)
            output = "J #" + str(instr_index_int)
            branch = instr_index_int

        if(opcode == BEQ):
            output = "BEQ "
            rs_string = "R" + str(rs) + ", "
            rt_string = "R" + str(rt) + ", "
            offset_string = "#" + str(int(offset,2))
            output = output + rs_string + rt_string + offset_string
            if( registers[rs] == registers[rt] ):
                branch = int(offset,2)

        if(opcode == BNE):
            output = "BNE "
            rs_string = "R" + str(rs) + ", "
            rt_string = "R" + str(rt) + ", "
            offset_string = "#" + str(int(offset,2))
            output = output + rs_string + rt_string + offset_string
            if( registers[rs] != registers[rt] ):
                branch = int(offset,2)


        if(opcode == BGTZ):
            output = "BGTZ "
            rs_string = "R" + str(rs) + ", "
            rt_string = "R" + str(rt) + ", "
            offset_string = "#" + str(int(offset,2))
            output = output + rs_string + offset_string
            if( registers[rs] > 0 ):
                branch = int(offset,2)


        if(opcode == SW): #stores into data
            #dest = rs
            #source = rt
            output = "SW "
            mem = int(sample[16:32],2)
            rs_string = "R" + str(rs)
            rt_string = "R" + str(rt) + ", "
            output = output + rt_string + str(mem) + "(" + rs_string + ")"
            data_index = int(((int(branch_offset,2)-data_break) + registers[rs])/4)
            data[data_index] = registers[rt]

        if(opcode == LW): #loads into registers
            #dest = rt
            #source = rs
            output = "LW "
            mem = int(sample[16:32],2)
            rs_string = "R" + str(rs)
            rt_string = "R" + str(rt) + ", "
            output = output + rt_string + str(mem) + "(" + rs_string + ")"
            #registers <-- from data
            data_index = int(((int(branch_offset,2)-data_break) + registers[rs])/4)
            registers[rt] = data[data_index]


        if(opcode == BREAK):
            output = "BREAK"
            break_exc = True

        #w_dis.write(output + '\n')
        return (output,break_exc,branch)


    # In[274]:


    #category 2 function
    def cat_2_func(sample):
        opcode = sample[3:6]
        rd = int(sample[6:11],2)
        rs = int(sample[11:16],2)
        rt = int(sample[16:21],2)
        output = ""


        if(opcode == ADD):
            output = "ADD "
            rd_string = "R" + str(rd) + ", "
            rs_string = "R" + str(rs) + ", "
            rt_string = "R" + str(rt)
            output = output + rd_string + rs_string + rt_string
            registers[rd] = registers[rs] + registers[rt]

        if(opcode == SUB):
            output = "SUB "
            rd_string = "R" + str(rd) + ", "
            rs_string = "R" + str(rs) + ", "
            rt_string = "R" + str(rt)
            output = output + rd_string + rs_string + rt_string
            registers[rd] = registers[rs] - registers[rt]

        if(opcode == AND):
            output = "AND "
            rd_string = "R" + str(rd) + ", "
            rs_string = "R" + str(rs) + ", "
            rt_string = "R" + str(rt)
            output = output + rd_string + rs_string + rt_string
            registers[rd] = registers[rs] and registers[rt]

        if(opcode == OR):
            output = "OR "
            rd_string = "R" + str(rd) + ", "
            rs_string = "R" + str(rs) + ", "
            rt_string = "R" + str(rt)
            output = output + rd_string + rs_string + rt_string
            registers[rd] = registers[rs] or registers[rt]

        if(opcode == SRL):
            output = "SRL "
            rd_string = "R" + str(rd) + ", "
            rs_string = "R" + str(rs) + ", "
            rt_string = "R" + str(rt)
            output = output + rd_string + rs_string + rt_string
            #registers[rd] = registers[rs] << registers[rt]

            #( rd <-- rs << rt )

        if(opcode == SRA):
            output = "SRA "
            rd_string = "R" + str(rd) + ", "
            rs_string = "R" + str(rs) + ", "
            rt_string = "R" + str(rt)
            output = output + rd_string + rs_string + rt_string
            #( rd <-- rs >> )

        if(opcode == MUL):
            output = "MUL "
            rd_string = "R" + str(rd) + ", "
            rs_string = "R" + str(rs) + ", "
            rt_string = "R" + str(rt)
            output = output + rd_string + rs_string + rt_string
            registers[rd] = registers[rs] * registers[rt]
            #()
        return output    


    # In[275]:


    #category 3 function
    def cat_3_func(sample):
        opcode = sample[3:6]
        rd = int(sample[6:11],2)
        rs = int(sample[11:16],2)
        imm = twos_complement(sample[16:])
        output = ""

        if(opcode == ADDI):
            output = "ADDI "
            rd_string = "R" + str(rd) + ", "
            rs_string = "R" + str(rs) + ", "
            imm_string = "#" + str(imm)
            output = output + rd_string + rs_string + imm_string
            registers[rd] = registers[rs] + imm


        if(opcode == ANDI):
            output = "ANDI "
            rd_string = "R" + str(rd) + ", "
            rs_string = "R" + str(rs) + ", "
            imm_string = "#" + str(imm)
            output = output + rd_string + rs_string + imm_string
            registers[rd] = registers[rs] and imm

        if(opcode == ORI):
            output = "ORI "
            rd_string = "R" + str(rd) + ", "
            rs_string = "R" + str(rs) + ", "
            imm_string = "#" + str(twos_complement(imm))
            output = output + rd_string + rs_string + imm_string
            registers[rd] = registers[rs] or imm

        return output    


    # In[276]:


    #write on disassembly file
    address = 260
    break_exc = False
    w_dis = open("disassembly.txt", "a")

    for instruction in input_instr:
        instr = instruction
        w_dis.write(instruction.strip() + '\t' + str(address).strip() + '\t')

        #decode input
        input_cat = instr[:3]

        if(break_exc):
            output = str(twos_complement(instruction))
            w_dis.write(output + '\n')

        if(input_cat == cat_1 and not break_exc): # branch functions possible
            output, break_exc, _ = cat_1_func(instruction,break_exc)
            w_dis.write(output + '\n')

        if(input_cat == cat_2 and not break_exc):
            output = cat_2_func(instruction)
            w_dis.write(output + '\n')

        if(input_cat == cat_3 and not break_exc):
            output = cat_3_func(instruction)
            w_dis.write(output + '\n')



        address = address + 4

    w_dis.close()


    # In[277]:


    #register print
    def register_print():
        output = "Registers\n"
        r_00 = "R00:"
        r_08 = "R08:"
        r_16 = "R16:"
        r_24 = "R24:"

        for i in range(8):
            r_00 = r_00 + "\t" + str(registers[i])
            r_08 = r_08 + "\t" + str(registers[i+8])
            r_16 = r_16 + "\t" + str(registers[i+16])
            r_24 = r_24 + "\t" + str(registers[i+24])
        output = output + r_00 + "\n" + r_08 + "\n" + r_16 + "\n" + r_24 + "\n\n"    
        return output



    # In[278]:


    #data print
    def data_print():
        output = "Data\n"
        d_316 = "316:"
        d_348 = "348:"

        for i in range(8):
            d_316 = d_316 + "\t" + str(data[i])
            d_348 = d_348 + "\t" + str(data[i+8])

        output = output + d_316 + "\n" + d_348 + "\n\n"
        return output


    # In[279]:


    #simulator
    data = lock_data # restore original data values inputted from file


    address = 260
    w_sim = open("simulation.txt","w")
    simulation_header = "--------------------\n"
    break_exc = False

    registers = [0] * 32 #only write

    cycle = 1
    i = 0

    while(i<len(input_instr)):
        branch = 0
        instr = input_instr[i]
        instruction = instr
        input_cat = instr[:3]

        if(not break_exc):
            w_sim.write(simulation_header)
            w_sim.write('Cycle ' + str(cycle) + ':\t' + str(address) + "\t")

        if(input_cat == cat_1 and not break_exc): #branch functions possible
            output, break_exc, branch = cat_1_func(instruction,break_exc)
            w_sim.write(output + '\n\n')

        if(input_cat == cat_2 and not break_exc):
            output = cat_2_func(instruction)
            w_sim.write(output + '\n\n')

        if(input_cat == cat_3 and not break_exc):
            output = cat_3_func(instruction)
            w_sim.write(output + '\n\n')

        #perform all instructions before showing results ^^^
        if(not break_exc):
            w_sim.write(register_print())
            w_sim.write(data_print())

        address = address + 4
        cycle = cycle+1
        i = i+1

        if( branch > 0 ):
            if( branch < 272 ):
                branch = branch+address
            i = int(i + (branch-address)/4)
            address = branch

    #One last register and data dump
    w_sim.write(register_print())
    w_sim.write(data_print())
    w_sim.close()

if __name__ == "__main__":
    main(sys.argv[1])
