import random
import string
import os
import json
from zipfile import ZipFile
import shlex


#not very good code
os.nmkdir = os.mkdir
def mk(o):
    try:
        os.nmkdir(o)
    except:
        pass
os.mkdir = mk
#whymustidothis

def uncommandify(command):
    return command.replace(commandify(""), "", 1)
# Base
def commandify(command):
    return "execute as @s run "+command
def tempreg():
    return ''.join([random.choice(string.ascii_letters) for _ in range(12)])
def init(progname, domessage=False):
    c = []
    if domessage:
        c = [commandify("say running program {}".format(progname))]
    return c+[commandify("scoreboard objectives add {} dummy".format(progname))]
def setdisplay(progname):
    return [commandify("scoreboard objectives setdisplay sidebar {}".format(progname).strip())]

# T1 Low Level
def setreg(progname, regto, regfrom):
    return [commandify("scoreboard players operation {1} {0} = {2} {0}".format(progname, regto, regfrom))]
def setregconst(progname, reg, value):
    return [commandify("scoreboard players set {} {} {}".format(reg, progname, value))]
def deletereg(progname, reg):
    return [commandify("scoreboard players reset {} {}".format(reg, progname))]
def addreg(progname,reg1,reg2,outreg):
    commands = []
    if not outreg == reg1:
        commands += setreg(progname,outreg,reg1)
    commands.append(commandify("scoreboard players operation {1} {0} += {2} {0}".format(progname,outreg,reg2)))
    return commands
def subreg(progname,reg1,reg2,outreg):
    commands = []
    if not outreg == reg1:
        commands += setreg(progname,outreg,reg1)
    commands.append(commandify("scoreboard players operation {1} {0} -= {2} {0}".format(progname,outreg,reg2)))
    return commands
def multreg(progname,reg1,reg2,outreg):
    commands = []
    if not outreg == reg1:
        commands += setreg(progname,outreg,reg1)
    commands.append(commandify("scoreboard players operation {1} {0} *= {2} {0}".format(progname,outreg,reg2)))
    return commands
def divreg(progname,reg1,reg2,outreg):
    commands = []
    if not outreg == reg1:
        commands += setreg(progname,outreg,reg1)
    commands.append(commandify("scoreboard players operation {1} {0} /= {2} {0}".format(progname,outreg,reg2)))
    return commands
def command(comm):
    return [commandify(comm)]
def onetick(commands):
    return commands
def modreg(progname,reg1,reg2,outreg):
    commands = []
    if not outreg == reg1:
        commands += setreg(progname,outreg,reg1)
    commands.append(commandify("scoreboard players operation {1} {0} %= {2} {0}".format(progname,outreg,reg2)))
    return commands

def ifreg(progname,reg1,reg2,cond,command):
    command = command[0]
    if commandify("") in command:
        command = uncommandify(command)
    return ["execute as @s if score {1} {0} {2} {3} {0} run {4}".format(progname,reg1,cond,reg2,command)]
def ifnotreg(progname,reg1,reg2,cond,command):
    command = command[0]
    if commandify("") in command:
        command = uncommandify(command)
    return ["execute as @s unless score {1} {0} {2} {3} {0} run {4}".format(progname,reg1,cond,reg2,command)]


#T2 Bitwise
# @todo more logic gates
# @body you cant have enough logic gates
def numtobitarray(progname,num,arr,bits=8):
    comm = []
    comm += setregconst(progname,"base",2)
    for bit in range(1,bits+1):
        comm += setregconst(progname,"{}-{}".format(arr,bit),0)
    comm += setreg(progname,"in",num)
    for bit in range(1,bits+1):
        arrindex = "{}-{}".format(arr,bit)
        comm += modreg(progname,"in","base",arrindex)
        comm += divreg(progname,"in","base","in")

    comm += deletereg(progname,"in")
    comm += deletereg(progname,"base")
    return comm
def bitarraytonum(progname,out,arr,bits=8):
    comm = []
    comm += setregconst(progname,out,0)
    for bit in range(1,bits+1):
        comm += setregconst(progname,"mult",2**(bit-1))
        comm += multreg(progname,"{}-{}".format(arr,bit),"mult","{}-{}-d".format(arr,bit))
    for bit in range(1,bits+1):
        comm += addreg(progname,out,"{}-{}-d".format(arr,bit),out)
    for bit  in range(1,bits+1):
        comm += deletereg(progname,"{}-{}-d".format(arr,bit))
    comm += deletereg(progname,"mult")
    return comm
def andregbit(progname,array1,array2,out,bits=8):
    comm = []
    for bit in range(1,bits+1):
        comm += multreg(progname,"{}-{}".format(array1,bit),"{}-{}".format(array2,bit),"{}-{}".format(out,bit))
    return comm
# @todo make and take in 2 bitarrays and return a bitarray
# @body chaining with less commands!
def andreg(progname,reg1,reg2,out,bits=8):
    comm = []
    array1 = tempreg()
    array2 = tempreg()
    outarray = tempreg()
    comm += numtobitarray(progname,reg1,array1,bits)
    comm += numtobitarray(progname,reg2,array2,bits)
    comm += andregbit(progname,array1,array2,outarray,bits)
    comm += bitarraytonum(progname,out,outarray,bits)
    for bit in range(1,bits+1):
        comm += deletereg(progname,"{}-{}".format(array1,bit))
        comm += deletereg(progname,"{}-{}".format(array2,bit))
        comm += deletereg(progname,"{}-{}".format(outarray,bit))
    return comm

def notregbit():
    pass
def notreg(progname,reg,out,bits=8):
    sub = 2**bits-1
    regs = tempreg()
    comm = setregconst(progname,regs,sub)
    comm += subreg(progname,regs,reg,out)
    comm += deletereg(progname,regs)
    return comm


def nand(progname,reg1,reg2,out,bits=8):
    comm = []
    temp = tempreg()
    comm += andreg(progname,reg1,reg2,temp,bits)
    comm += notreg(progname,temp,out,bits)
    comm += deletereg(progname,temp)
    return comm
def progtofile(prog,out):
    with open(os.path.join(out,"run.mcfunction"),"w") as file:
        file.write('\n'.join(prog))
def makedatapack(author,progname,prog):
    author, progname = author.lower(),progname.lower()
    print("Creating build directories")
    try:
        os.mkdir("build")
    except:
        pass
    builddir = ".\\build\\"+progname
    os.mkdir(builddir)
    os.chdir(builddir)
    os.mkdir("data")
    os.mkdir(os.path.join("data",author))
    os.mkdir(os.path.join("data",author,"functions"))
    os.mkdir(os.path.join("data",author,"functions",progname))
    print("writing files")
    with open("pack.mcmeta","w") as file:
        data = {"pack": {"pack_format": 1,"description": "{} by {}".format(progname,author)}}
        file.write(json.dumps(data))
    progtofile(prog,os.path.join("data",author,"functions",progname))
    print("zipping up")

    with ZipFile('{}-{}.zip'.format(author,progname), 'w') as myzip:
        myzip.write("pack.mcmeta")
        myzip.write("data/")
        myzip.write("data/"+author)
        myzip.write("data/"+author+"/functions/")
        myzip.write("data/"+author+"/functions/"+progname)
        myzip.write("data/"+author+"/functions/"+progname+"/run.mcfunction")

    os.chdir("../..")
# two plus two example program
twoplustwo = init("twoplustwo",False)
twoplustwo += setdisplay("twoplustwo")
twoplustwo += setregconst("twoplustwo","numone",2)
twoplustwo += setregconst("twoplustwo","numtwo",2)
twoplustwo += addreg("twoplustwo","numone","numtwo","out")
maketwoplustwo = lambda: makedatapack("webmsgr","twoplustwo",twoplustwo)
# finished
#arraytest
arraytest = init("arraytest",False)
arraytest += setregconst("arraytest","inp",5)
arraytest += numtobitarray("arraytest","inp","input")
arraytest += bitarraytonum("arraytest","out","input")
makearraytest = lambda: makedatapack("webmsgr","arraytest",arraytest)
#end
# and test
andtest = init("andtest",False)
andtest += setregconst("andtest","in1",5)
andtest += setregconst("andtest","in2",6)
andtest += andreg("andtest","in1","in2","out") # out should be 4
# not test
nottest = init("nottest",False)
nottest += setregconst("nottest","in1",5)
nottest += notreg("nottest","in1","out") # should be 250
