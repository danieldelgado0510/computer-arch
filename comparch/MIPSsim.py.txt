#!/usr/bin/env python
# coding: utf-8

# In[229]:


#!/usr/bin/env python
# coding: utf-8

#Daniel Delgado
#On my honor, I have neither given nor received unauthorized aid on this assignment


# In[230]:


import sys


# In[231]:


#category 1
cat_1 = '000'
J='000'
BEQ='001'
BNE='010'
BGTZ='011'
SW='100'
LW='101'
BREAK='110'
cat1 = [cat_1,J,BEQ,BNE,BGTZ,SW,LW,BREAK]


# In[232]:


#category 2
cat_2 = '001'
ADD='000'
SUB='001'
AND='010'
OR='011'
SRL='100'
SRA='101'
MUL='110'
cat2 = [cat_2,ADD,SUB,AND,OR,SRL,SRA,MUL]


# In[233]:


#category 3
cat_3 = '010'
ADDI='000'
ANDI='001'
ORI='010'
cat3 = [cat_3,ADDI,ANDI,ORI]


# In[234]:


#register arrays, initialized to zero
registers = [0] * 32 #only write
data = [0] * 16 #only read
lock_data = [0] * 16
data_break = 260
break_index = 0


# In[235]:


#initialize all registers to 0
def init():
    global registers
    global data
    global lock_data
    registers = [0] * 32 
    for i in range(len(lock_data)):
        data[i] = lock_data[i]


# In[236]:


#convert negative two's complement to int
def convert(val):
        tmp = val.strip()
        tmp = ''.join('1' if x == '0' else '0' for x in tmp)
        tmp = int(tmp,2) + 1
        return tmp*-1


# In[237]:


#convert two's complement binary to int
def twos_complement(sample):
        if(sample[0]=='1'): #negative bit
            return convert(sample)

        elif(sample[0]=='0'): #positive bit
            return int(sample,2)


# In[238]:


def shift_l(value,shift):
    if value >= 0:
        return value>>shift
    else: 
        return (value+0x100000000)>>shift


# In[239]:


#read in instructions from file, return instruction array
def read_instr(file):
    input_instr = []
    f_dis = open(file,"r")
    for x in f_dis:
        input_instr.append(x)
    return input_instr


# In[240]:


#read data from instr
def read_data(input_instr):
    global lock_data
    global data_break
    global break_index
    address = 260
    #data registers, initialized to zero
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
    return data


# In[241]:


def which_cat(sample):
    input_cat = sample[:3]    
    if(input_cat == cat_1): # branch functions possible
        return 1
    if(input_cat == cat_2):
        return 2
    if(input_cat == cat_3):
        return 3
    else: return -1


# In[242]:


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
        #data[data_index] = registers[rt]

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
        #registers[rt] = data[data_index]


    if(opcode == BREAK):
        output = "BREAK"
        break_exc = True

    #w_dis.write(output + '\n')
    return (output,break_exc,branch)


# In[243]:


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
        #registers[rd] = registers[rs] + registers[rt]

    if(opcode == SUB):
        output = "SUB "
        rd_string = "R" + str(rd) + ", "
        rs_string = "R" + str(rs) + ", "
        rt_string = "R" + str(rt)
        output = output + rd_string + rs_string + rt_string
        #registers[rd] = registers[rs] - registers[rt]

    if(opcode == AND):
        output = "AND "
        rd_string = "R" + str(rd) + ", "
        rs_string = "R" + str(rs) + ", "
        rt_string = "R" + str(rt)
        output = output + rd_string + rs_string + rt_string
        #registers[rd] = registers[rs] and registers[rt]

    if(opcode == OR):
        output = "OR "
        rd_string = "R" + str(rd) + ", "
        rs_string = "R" + str(rs) + ", "
        rt_string = "R" + str(rt)
        output = output + rd_string + rs_string + rt_string
        #registers[rd] = registers[rs] or registers[rt]

    if(opcode == SRL):
        output = "SRL "
        rd_string = "R" + str(rd) + ", "
        rs_string = "R" + str(rs) + ", "
        rt_string = "#" + str(rt)
        output = output + rd_string + rs_string + rt_string
        #registers[rd] = shift_l(registers[rs], registers[rt])
        #registers[rd] = registers[rs] >> registers[rt]

        #( rd <-- rs >> rt )

    if(opcode == SRA):
        output = "SRA "
        rd_string = "R" + str(rd) + ", "
        rs_string = "R" + str(rs) + ", "
        rt_string = "#" + str(rt)
        output = output + rd_string + rs_string + rt_string
        #registers[rd] = registers[rs] >> registers[rt]
        #registers[rd] = registers[rs] >> registers[rt]

        #( rd <-- rs >> rt)

    if(opcode == MUL):
        output = "MUL "
        rd_string = "R" + str(rd) + ", "
        rs_string = "R" + str(rs) + ", "
        rt_string = "R" + str(rt)
        output = output + rd_string + rs_string + rt_string
        #registers[rd] = registers[rs] * registers[rt]
        #()
    return output    


# In[244]:


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
       #registers[rd] = registers[rs] + imm


   if(opcode == ANDI):
       output = "ANDI "
       rd_string = "R" + str(rd) + ", "
       rs_string = "R" + str(rs) + ", "
       imm_string = "#" + str(imm)
       output = output + rd_string + rs_string + imm_string
       #registers[rd] = registers[rs] and imm

   if(opcode == ORI):
       output = "ORI "
       rd_string = "R" + str(rd) + ", "
       rs_string = "R" + str(rs) + ", "
       imm_string = "#" + str(imm)
       output = output + rd_string + rs_string + imm_string
       #registers[rd] = registers[rs] or imm

   return output   


# In[245]:


def cat1_raw(sample):

    input_cat = sample[0:3]
    opcode = sample[3:6]

    rs = int(sample[6:11],2)
    rt = int(sample[11:16],2)

    offset = sample[16:32]
    branch_offset = offset
    offset = offset.strip() + '00'

    branch = 0
    output = 0

    if(opcode == J):
        instr_index = sample[8:]
        instr_index = instr_index.strip() + '00'
        instr_index_int = int(instr_index, 2)
        branch = instr_index_int

    if(opcode == BEQ):
        if( registers[rs] == registers[rt] ):
            branch = int(offset,2)

    if(opcode == BNE):
        if( registers[rs] != registers[rt] ):
            branch = int(offset,2)

    if(opcode == BGTZ):
        if( registers[rs] > 0 ):
            branch = int(offset,2)

    if(opcode == SW): #stores into data SW should never get used, only LW. Same for all other instructions
        #dest = rs
        #source = rt
        data_index = int(((int(branch_offset,2)-data_break) + registers[rs])/4)
        output = registers[rt]

    if(opcode == LW): #loads into registers
        #dest = rt
        #source = rs
        #registers <-- from data
        data_index = int(((int(branch_offset,2)-data_break) + registers[rs])/4)
        output = data[data_index]

    return output, rt#value, register

def cat2_raw(sample):
    opcode = sample[3:6]
    rd = int(sample[6:11],2)
    rs = int(sample[11:16],2)
    rt = int(sample[16:21],2)
    output = 0

    if(opcode == ADD):
        output = registers[rs] + registers[rt]

    if(opcode == SUB):
        output = registers[rs] - registers[rt]

    if(opcode == AND):
        output = registers[rs] and registers[rt]

    if(opcode == OR):
        output = registers[rs] or registers[rt]

    if(opcode == SRL):
        output = shift_l(registers[rs], registers[rt])

    if(opcode == SRA):
        output = registers[rs] >> registers[rt]

    if(opcode == MUL):
        output = registers[rs] * registers[rt]   
    return output, rd
    
def cat3_raw(sample):
    opcode = sample[3:6]
    rd = int(sample[6:11],2)
    rs = int(sample[11:16],2)
    imm = twos_complement(sample[16:])
    output = 0
    if(opcode == ADDI):
        output = registers[rs] + imm

    if(opcode == ANDI):
        output = registers[rs] and imm

    if(opcode == ORI):
        output = registers[rs] or imm
    return output, rd
    
def cat_raw(sample):
    cat = which_cat(sample)
    if(cat == 1):
        return cat1_raw(sample)
    if(cat == 2):
        return cat2_raw(sample)
    if(cat == 3):
        return cat3_raw(sample)


# In[246]:


def cat1_exec(sample):

    input_cat = sample[0:3]
    opcode = sample[3:6]

    rs = int(sample[6:11],2)
    rt = int(sample[11:16],2)

    offset = sample[16:32]
    branch_offset = offset
    offset = offset.strip() + '00'

    branch = 0

    if(opcode == J):
        instr_index = sample[8:]
        instr_index = instr_index.strip() + '00'
        instr_index_int = int(instr_index, 2)
        branch = instr_index_int

    if(opcode == BEQ):
        if( registers[rs] == registers[rt] ):
            branch = int(offset,2)

    if(opcode == BNE):
        if( registers[rs] != registers[rt] ):
            branch = int(offset,2)

    if(opcode == BGTZ):
        if( registers[rs] > 0 ):
            branch = int(offset,2)

    if(opcode == SW): #stores into data
        #dest = rs
        #source = rt
        data_index = int(((int(branch_offset,2)-data_break) + registers[rs])/4)
        data[data_index] = registers[rt]

    if(opcode == LW): #loads into registers
        #dest = rt
        #source = rs
        #registers <-- from data
        data_index = int(((int(branch_offset,2)-data_break) + registers[rs])/4)
        registers[rt] = data[data_index]

    return branch


# In[247]:


def cat2_exec(sample):
    opcode = sample[3:6]
    rd = int(sample[6:11],2)
    rs = int(sample[11:16],2)
    rt = int(sample[16:21],2)

    if(opcode == ADD):
        registers[rd] = registers[rs] + registers[rt]

    if(opcode == SUB):
        registers[rd] = registers[rs] - registers[rt]

    if(opcode == AND):
        registers[rd] = registers[rs] and registers[rt]

    if(opcode == OR):
        registers[rd] = registers[rs] or registers[rt]

    if(opcode == SRL):
        registers[rd] = shift_l(registers[rs], registers[rt])

    if(opcode == SRA):
        registers[rd] = registers[rs] >> registers[rt]

    if(opcode == MUL):
        registers[rd] = registers[rs] * registers[rt]   


# In[248]:


#category 3 function
def cat3_exec(sample):
   opcode = sample[3:6]
   rd = int(sample[6:11],2)
   rs = int(sample[11:16],2)
   imm = twos_complement(sample[16:])

   if(opcode == ADDI):
       registers[rd] = registers[rs] + imm


   if(opcode == ANDI):
       registers[rd] = registers[rs] and imm

   if(opcode == ORI):
       registers[rd] = registers[rs] or imm


# In[249]:


def rd_rs_rt_1(sample):
    input_cat = sample[0:3]
    opcode = sample[3:6]
    rs = int(sample[6:11],2)
    rd = int(sample[11:16],2)
    
    if(opcode == LW):
        return rd, rs, -1 #write, read, read format
    else: return -1, rd, rs
    
def rd_rs_rt_2(sample):
    rd = int(sample[6:11],2)
    rs = int(sample[11:16],2)
    rt = int(sample[16:21],2)
    return rd, rs, rt #write, read, read format

def rd_rs_rt_3(sample):
    rd = int(sample[6:11],2)
    rs = int(sample[11:16],2)
    return rd, rs, -1 #write, read, read format

def rd_rs_rt(sample):
    cat = which_cat(sample)
    if(cat == 1):
        return rd_rs_rt_1(sample)
    if(cat == 2):
        return rd_rs_rt_2(sample)
    if(cat == 3):
        return rd_rs_rt_3(sample)


# In[250]:


def cat(sample): #for printing ease of instructions
    #decode input
    input_cat = sample[:3]
    output = ""
    _ = __ = False
    
    if(input_cat == cat_1): # branch functions possible
        output, _, __ = cat_1_func(sample,_)

    if(input_cat == cat_2):
        output = cat_2_func(sample)
        

    if(input_cat == cat_3):
        output = cat_3_func(sample)
        
    return output


# In[251]:


def data_print():
    output = "Data\n"
    d_316 = str(data_break) + ":"
    d_348 = str(data_break+32) + ":"

    for i in range(8):
        d_316 = d_316 + "\t" + str(data[i])
        d_348 = d_348 + "\t" + str(data[i+8])

    output = output + d_316 + "\n" + d_348 + "\n"
    return output


# In[252]:


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
    output = output + r_00 + "\n" + r_08 + "\n" + r_16 + "\n" + r_24 + "\n"    
    return output


# In[253]:


class Pipeline:
    def __init__(self, instruction):
        #initialize cycles
        self.CYCLE = 0
        
        #assign instruction set
        self.INSTRUCTION = [i for i in instruction]
        
        #location on instruction set
        self.INSTR_PTR = 0
        
        #IF branches
        self.WAITING = [] #max 1
        self.EXECUTED = [] #max 1
        
        #buffers 1-10
        self.BUF_1 = [] #max 8
        self.BUF_2 = [] #max 2
        self.BUF_3 = [] #max 2
        self.BUF_4 = [] #max 2
        self.BUF_5 = [] #max 1
        self.BUF_6 = [] #max 1
        self.BUF_7 = [] #max 1
        self.BUF_8 = [] #max 1
        self.BUF_9 = [] #max 1
        self.BUF_10 = [] #max 1
        
        #stalled pipeline
        self.STALL = False
        
        #break found
        self.COMPLETE = False
        
        
    #Control functions
    def complete(self):
        return self.COMPLETE
    
    def stall(self):
        self.STALL = True
        
    def unstall(self):
        self.STALL = False
        
    def get_instr(self):
        instr = [i for i in self.INSTRUCTION]
        return instr
    
    def branch(self, branch):
        br = int(branch/4)
        if( br == 0 ):
            return -1
        if( br > 65 ):
            br = br - 65 
        return br
    
    #sorry
    def empty_buf(self):
        return (not self.BUF_1 and not self.BUF_2 and not self.BUF_3 and not self.BUF_4 and not self.BUF_5 and not self.BUF_6 and not self.BUF_7 and not self.BUF_8 and not self.BUF_9 and not self.BUF_10)
       
    def sum_buf(self):
        all_buf = self.BUF_2 + self.BUF_3 + self.BUF_4 + self.BUF_5 + self.BUF_6 + self.BUF_7 + self.BUF_8 + self.BUF_9 + self.BUF_10
        return all_buf
    
    def RAW(self,instr1,instr2):#assuming instr1 came before instr2
        rd_1, rs_1, rt_1 = rd_rs_rt(instr1)
        rd_2, rs_2, rt_2 = rd_rs_rt(instr2)
        
        if(rd_1 == -1):
            rd_1 = -2
        if(rs_2 == -1):
            rs_2 = -3
        if(rt_2 == -1):
            rt_2 = -4
            
        if(rd_1 == rs_2 or rd_1 == rt_2):
            return True
        return False
    
    def WAW(self,instr1,instr2):
        rd_1, rs_1, rt_1 = rd_rs_rt(instr1)
        rd_2, rs_2, rt_2 = rd_rs_rt(instr2)
        
        if(rd_1 == -1):
            rd_1 = -2
        if(rd_2 == -1):
            rd_2 = -3
        
        if(rd_1 == rd_2):
            return True
        return False
    
    def WAR(self,instr1,instr2):
        rd_1, rs_1, rt_1 = rd_rs_rt(instr1)
        rd_2, rs_2, rt_2 = rd_rs_rt(instr2)
        
        if(rd_2 == -1):
            rd_2 = -2
        if(rs_1 == -1):
            rs_1 = -3
        if(rt_1 == -1):
            rt_1 = -4
        
        if(rd_2 == rs_1 or rd_2 == rt_1):
            return True
        return False
    
    #used in issue stage
    def depend(self,instr):#master dependency function. Compares with existing in pipeline, returns if dependent or not
        tmp_all = self.sum_buf()
        index = self.BUF_1.index(instr)

        size = len(self.BUF_1)

        for x in range(index, -1, -1):
            i = self.BUF_1[x]
            if(i == instr):
                continue
            sum_dep = self.RAW(i,instr) or self.WAW(i,instr) or self.WAR(i,instr)
            if(sum_dep):
                return True
        
        rare_war = False
        for i in self.BUF_2:
            input_cat = i[0:3]
            opcode = i[3:6]
            if(opcode == SW and self.WAR(i,instr)): #if store word instruction and some dependency, can by pass WAR if SW in buf2 already
                rare_war = True
        
        war = False
        for i in tmp_all:
            if(i == instr):
                continue
            if(rare_war):
                war = False
            else: war = self.WAR(i,instr)
                
            sum_dep = self.RAW(i,instr) or self.WAW(i,instr) or war
            if(sum_dep):
                return True

        return False
    
    def depend_branch(self,instr,tmp_buf1):#master dependency function. Compares with existing in pipeline, returns if dependent or not
        tmp_all = tmp_buf1 + self.BUF_1 + self.sum_buf()

        for i in tmp_all:
            if(i == instr):
                continue
            sum_dep = self.RAW(i,instr) or self.WAW(i,instr) or self.WAR(i,instr)
            if(sum_dep):
                return True
        return False
    
    #main pipeline
    def direction(self, sample): #helps IS decide which buffer each instruction goes
        input_cat = sample[0:3]
        opcode = sample[3:6]
        if(input_cat == cat_1):
            if(opcode == J or opcode == BEQ or opcode == BNE or opcode == BGTZ or opcode == BREAK):
                return 0
            
            if(opcode == LW or opcode == SW):
                return 1
            
        if(input_cat == cat_2):
            if(opcode == ADD or opcode == SUB or opcode == AND or opcode == OR or opcode == SRL or opcode == SRA):
                return 2
            
            if(opcode == MUL):
                return 3
            
        if(input_cat == cat_3):
            if(opcode == ADDI or opcode == ANDI or opcode == ORI):
                return 4
            
        return 1
    

    def IF(self):

        tmp_buf1 = []
        tmp_wait = []
        tmp_exec = []
        
        if( not self.STALL ): #check if stalled # scratch this, only stalls on dependencies # this is deprecated
            _ = False
            space = 8 - len(self.BUF_1) 
            if(space > 4):
                space = 4
            for i in range(space):
                instr = self.INSTRUCTION[self.INSTR_PTR]
                self.INSTR_PTR = self.INSTR_PTR + 1
                input_cat = instr[:3]
                opcode = instr[3:6]
                
                if( self.direction(instr) == 0 ):#branch instruction fetched
                    if(opcode == BREAK):
                        _, broke, _ = cat_1_func(instr, _)
                        if(broke):
                            self.COMPLETE = True
                            self.stall()
                            tmp_exec.append(instr)
                            break
                    if(opcode == J):
                        self.INSTR_PTR = self.branch(cat1_exec(instr))
                        tmp_exec.append(instr)
                        break
                    else:
                        check = self.depend_branch(instr,tmp_buf1) #check dependencies on branch instr
                        if(check):#dependencies found, stall until clear
                            self.stall()
                            tmp_wait.append(instr)#if dependencies goes here
                        else:
                            tmp_exec.append(instr)
                            value = self.branch(cat1_exec(instr))
                            if(value != -1):
                                self.INSTR_PTR = value + self.INSTR_PTR 
                        break
 
                tmp_buf1.append(instr)
                        
        if(self.WAITING): 
            check = self.depend_branch(self.WAITING[0],[])
            if( not check ):
                tmp = self.WAITING[0]
                tmp_exec.append(tmp)
                self.WAITING.remove(tmp)
                self.unstall()
                value = self.branch(cat1_exec(tmp))
                if(value != -1):
                    self.INSTR_PTR = value + self.INSTR_PTR
            
        if(self.EXECUTED):
            self.EXECUTED.pop()

        return tmp_buf1, tmp_wait, tmp_exec
    
    
    def IS(self):
        tmp_buf2 = []
        tmp_buf3 = []
        tmp_buf4 = []
        
        space_2 = 2 - len(self.BUF_2)    
        counter = 0
        for i in self.BUF_1:#if dependency skip
            if(self.depend(i)):
                continue
            if(counter == space_2): #next buff full
                break
            if(self.direction(i) == 1):#LW and SW with no dependencies or other
                tmp_buf2.append(i)#issue
                counter = counter + 1
        
        space_3 = 2 - len(self.BUF_3)    
        counter = 0
        for i in self.BUF_1:
            if(self.depend(i)):
                continue
            if(counter == space_3):
                break
            if(self.direction(i) == 2 or self.direction(i) == 4):#ADD, ADDI, etc.
                tmp_buf3.append(i)
                counter = counter + 1
                
        space_4 = 2 - len(self.BUF_4)    
        counter = 0
        for i in self.BUF_1:
            if(self.depend(i)):
                continue
            if(counter == space_4):
                break
            if(self.direction(i) == 3):#MUL
                tmp_buf4.append(i)
                counter = counter + 1  

        for i in tmp_buf2:
            self.BUF_1.remove(i) #remove extracted elements AFTER copying onto new buffer

        for i in tmp_buf3:
            self.BUF_1.remove(i)        

        for i in tmp_buf4:
            self.BUF_1.remove(i)
        
        
        return (tmp_buf2, tmp_buf3, tmp_buf4)
    
    
    def ALU1(self):
        tmp_buf5 = []
        if(self.BUF_2):
            tmp = self.BUF_2[0]
            tmp_buf5.append(tmp)
            self.BUF_2.remove(tmp)
        return tmp_buf5
    
    def ALU2(self):
        tmp_buf6 = []
        if(self.BUF_3):
            tmp = self.BUF_3[0]
            tmp_buf6.append(tmp)
            self.BUF_3.remove(tmp)
        return tmp_buf6
    
    def MUL1(self):
        tmp_buf7 = []
        if(self.BUF_4):
            tmp = self.BUF_4[0]
            tmp_buf7.append(tmp)
            self.BUF_4.remove(tmp)
        return tmp_buf7
    
    def MEM(self):
        tmp_buf8 = []
        #detect sw and execute
        if(self.BUF_5):
            tmp = self.BUF_5[0]
            input_cat = tmp[:3]
            opcode = tmp[3:6]
            if(opcode == SW):
                cat1_exec(tmp)
                self.BUF_5.remove(tmp)
                return tmp_buf8
            tmp_buf8.append(tmp)
            self.BUF_5.remove(tmp)
        return tmp_buf8
    
    def MUL2(self):
        tmp_buf9 = []
        if(self.BUF_7):
            tmp = self.BUF_7[0]
            tmp_buf9.append(tmp)
            self.BUF_7.remove(tmp)
        return tmp_buf9
    
    def MUL3(self):
        tmp_buf10 = []
        if(self.BUF_9):
            tmp = self.BUF_9[0]
            tmp_buf10.append(tmp)
            self.BUF_9.remove(tmp)
        return tmp_buf10
    
    def WB(self): #writes into registers, dont worry about sequencing, final step
        write = []
        if(self.BUF_6):
            instr = self.BUF_6[0]
            direc = self.direction(instr)
            if(direc == 2):
                cat2_exec(instr)
                self.BUF_6.pop(0)
            if(direc == 4):
                cat3_exec(instr)
                self.BUF_6.pop(0)
        if(self.BUF_8):
            instr = self.BUF_8[0]
            direc = self.direction(instr)
            if(direc == 1):
                cat1_exec(instr)
                self.BUF_8.pop(0)
        if(self.BUF_10):
            instr = self.BUF_10[0]
            direc = self.direction(instr)
            if(direc == 3):
                cat2_exec(instr)
                self.BUF_10.pop(0)
        return True
        
    
    def update_buffers(self): #where all the pipeline magic happens
        tmp_buf1, tmp_wait, tmp_exec = self.IF()
        tmp_buf2, tmp_buf3, tmp_buf4 = self.IS()
        tmp_buf5 = self.ALU1()
        tmp_buf6 = self.ALU2()
        tmp_buf7 = self.MUL1()
        tmp_buf8 = self.MEM()
        tmp_buf9 = self.MUL2()
        tmp_buf10 = self.MUL3()
        self.WB()
        
        #im so sorry
        self.BUF_1 = self.BUF_1 + tmp_buf1
        self.WAITING = self.WAITING + tmp_wait
        self.EXECUTED = self.EXECUTED + tmp_exec
        self.BUF_2 = self.BUF_2 + tmp_buf2
        self.BUF_3 = self.BUF_3 + tmp_buf3
        self.BUF_4 = self.BUF_4 + tmp_buf4
        self.BUF_5 = self.BUF_5 + tmp_buf5
        self.BUF_6 = self.BUF_6 + tmp_buf6
        self.BUF_7 = self.BUF_7 + tmp_buf7
        self.BUF_8 = self.BUF_8 + tmp_buf8
        self.BUF_9 = self.BUF_9 + tmp_buf9
        self.BUF_10 = self.BUF_10 + tmp_buf10
    
    def cycle(self):
        self.CYCLE = self.CYCLE + 1
        self.update_buffers()
    
    #Print Functions
    def if_print(self):
        output = "IF:\n"
        
        output = output + "\tWaiting: "
        if(self.WAITING): #not empty
            output = output + "[" + cat(self.WAITING[0]) + "]\n"
        else:
            output = output + "\n"
        
        output = output + "\tExecuted: "
        if(self.EXECUTED): #not empty
            output = output + "[" + cat(self.EXECUTED[0]) + "]\n"
        else:
            output = output + "\n"
            
        return output
    
    
    def buf1_print(self):
        output = "Buf1:\n"
        for i in range(len(self.BUF_1)):
            output = output + "\tEntry " + str(i) + ": [" + cat(self.BUF_1[i]) + "]\n" 
        remaining = len(self.BUF_1)
        for i in range(remaining, 8):
            output = output + "\tEntry " + str(i) + ":\n"
        return output
    
    
    def buf2_print(self):
        output = "Buf2:\n"
        for i in range(len(self.BUF_2)):
            output = output + "\tEntry " + str(i) + ": [" + cat(self.BUF_2[i]) + "]\n" 
        remaining = len(self.BUF_2)
        for i in range(remaining, 2):
            output = output + "\tEntry " + str(i) + ":\n"
        return output
        
        
    def buf3_print(self):
        output = "Buf3:\n"
        for i in range(len(self.BUF_3)):
            output = output + "\tEntry " + str(i) + ": [" + cat(self.BUF_3[i]) + "]\n" 
        remaining = len(self.BUF_3)
        for i in range(remaining, 2):
            output = output + "\tEntry " + str(i) + ":\n"
        return output
        
        
    def buf4_print(self):
        output = "Buf4:\n"
        for i in range(len(self.BUF_4)):
            output = output + "\tEntry " + str(i) + ": [" + cat(self.BUF_4[i]) + "]\n"
        remaining = len(self.BUF_4)
        for i in range(remaining, 2):
            output = output + "\tEntry " + str(i) + ":\n"
        return output
                
        
    def buf5_10_print(self):
        output = "Buf5: "
        if(self.BUF_5): #not empty
            output = output + "[" + cat(self.BUF_5[0]) + "]\n"
        else: #empty
            output = output + "\n"
        
        output = output + "Buf6: "
        if(self.BUF_6): #not empty
            output = output + "[" + str(cat_raw(self.BUF_6[0])[0]) + ", R" + str(cat_raw(self.BUF_6[0])[1]) + "]\n"
        else: #empty
            output = output + "\n"
        
        output = output + "Buf7: "
        if(self.BUF_7): #not empty
            output = output + "[" + cat(self.BUF_7[0]) + "]\n"
        else: #empty
            output = output + "\n"
        
        output = output + "Buf8: "
        if(self.BUF_8): #not empty
            output = output + "[" + str(cat_raw(self.BUF_8[0])[0]) + ", R" + str(cat_raw(self.BUF_8[0])[1]) + "]\n"
        else: #empty
            output = output + "\n"
        
        output = output + "Buf9: "
        if(self.BUF_9): #not empty
            output = output + "[" + cat(self.BUF_9[0]) + "]\n"
        else: #empty
            output = output + "\n"
        
        output = output + "Buf10: "
        if(self.BUF_10): #not empty
            output = output + "[" + str(cat_raw(self.BUF_10[0])[0]) + ", R" + str(cat_raw(self.BUF_10[0])[1]) + "]\n"
        else: #empty
            output = output + "\n"
        
        return output
        
    
    def pipeline_print(self):
        output = ""
        output = output + self.if_print()
        output = output + self.buf1_print()
        output = output + self.buf2_print()
        output = output + self.buf3_print()
        output = output + self.buf4_print()
        output = output + self.buf5_10_print() + "\n"
            
        return output
        
            
            


# In[254]:


#Disassembler function
def disassembler(input_instr):
    address = 260
    break_exc = False
    w_dis = open("disassembly.txt", "w")

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
    return True


# In[255]:


def simulation(instruction):
    kill = 0
    #output text divider
    divider = "--------------------\n"
    
    #open new simulation.txt file to write
    file = 'simulation.txt'
    w_sim = open(file, "w")
    
    #create pipeline with instruction 
    p = Pipeline(instruction)
    
    while( not p.complete() ):
        kill = kill + 1
        if(kill > 100):
            break
        #print("cycle: ", str(kill))
        
        #cycle pipeline
        p.cycle()
            
        #print pipeline contents
        w_sim.write(divider)
        w_sim.write("Cycle " + str(p.CYCLE) + ":\n\n")
        w_sim.write(p.pipeline_print())
        w_sim.write(register_print() + "\n")
        w_sim.write(data_print())
    
    w_sim.close()
    
   
    
    
    #call pipeline


# In[256]:


def main(argv):
    text = argv
    #Read in instructions
    instr = read_instr(text) #eventually will be argv
    
    #Read in data from instructions
    data = read_data(instr)
    
    #Write to disassembler file
    disassembler(instr)
    
    #Initialize data and registers
    init()
    
    #Simulation
    simulation(instr)
    
    #done
    


# In[257]:


if __name__ == "__main__":
    main(sys.argv[1])


# In[ ]:




