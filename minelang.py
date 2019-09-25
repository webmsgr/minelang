import random
import string
import os
import json
from zipfile import ZipFile

#not good code
os.nmkdir = os.mkdir
def mk(o):
    try:
        os.nmkdir(o)
    except:
        pass
os.mkdir = mk
#whymustidothis


# Base
def commandify(command):
    return "execute as @s run "+command
def tempreg():
    return ''.join([random.choice(string.ascii_letters) for n in xrange(16)])
def init(progname,domessage=False):
    c = []
    if domessage:
        c = [commandify("say running program {}".format(progname))]
    return c+[commandify("scoreboard objectives add {} dummy".format(progname))]
def setdisplay(progname):
    return [commandify("scoreboard objectives setdisplay sidebar {}".format(progname).strip())]

# T1 Low Level
def setreg(progname,regto,regfrom):
    return [commandify("scoreboard players operation {1} {0} = {2} {0}".format(progname,regto,regfrom))]
def setregconst(progname,reg,value):
    return [commandify("scoreboard players set {} {} {}".format(reg,progname,value))]
def deletereg(progname,reg):
    return [commandify("scoreboard players reset {} {}".format(reg,progname))]
def addreg(progname,reg1,reg2,outreg):
    commands = []
    commands += setreg(progname,outreg,reg1)
    commands.append(commandify("scoreboard players operation {1} {0} += {2} {0}".format(progname,outreg,reg2)))
    return commands
def subreg(progname,reg1,reg2,outreg):
    commands = []
    commands += setreg(progname,outreg,reg1)
    commands.append(commandify("scoreboard players operation {1} {0} -= {2} {0}".format(progname,outreg,reg2)))
    return commands                    
def multreg(progname,reg1,reg2,outreg):
    commands = []
    commands += setreg(progname,outreg,reg1)
    commands.append(commandify("scoreboard players operation {1} {0} *= {2} {0}".format(progname,outreg,reg2)))
    return commands
def divreg(progname,reg1,reg2,outreg):
    commands = []
    commands += setreg(progname,outreg,reg1)
    commands.append(commandify("scoreboard players operation {1} {0} /= {2} {0}".format(progname,outreg,reg2)))
    return commands
def command(comm):
    return commandify(comm)
def onetick(commands):
    return commands

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
        myzip.write("pack.mcmeta".format(progname))
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
# finished