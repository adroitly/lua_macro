# coding:utf-8
import sys
import os
import time
import re

START_IF = "--#if"
ELSE_IF = "--#elseif"
ELSE = "--#else"
END_IF = "--#endif"
TAG_START = "--[[ AUTO_COMPLIME_START --"
TAG_END = "-- AUTO_COMPLIME_END ]] --"
REMOVE_TEXT = False

helpStr = """
use cmd line this
python lua_macro.py --path=path --tags="tag1|tag2" --remove=false

cmds =
    --path=path
    --tags="tag1|tag2"
    --remove=false/true
    --exclude="path|path"
    --endswith=".lua|.py"
    --help show detail
"""

def log(*args):
    logStr = ""
    for n in args:
        logStr += str(n) + " "
    if len(logStr) != 0:
        print(logStr)

def get_line_if(line):
    line = line.strip()
    line = line.replace(" ", "")
    line = line.replace(START_IF, "")
    line = line.replace(ELSE_IF, "")
    line = line.replace(ELSE, "")
    line = line.replace(END_IF, "")
    ifs = line.split("|")
    return ifs

def line_isin_tags(line, tags):
    ifs = get_line_if(line)
    for tag in ifs:
        if tag in tags:
            return True
    return False

def if_is_error(lines):
    tag = 0
    for line in lines:
        if START_IF in line:
            tag = 1
        elif ELSE_IF in line:
            if tag == -1:
                return True
        elif ELSE in line:
            tag = -1
    return False

def remove_texts(lines):
    targetLines = []
    tag = 0
    for line in lines:
        if TAG_START in line:
            tag = 1
        elif TAG_END in line:
            tag = 0
        elif tag == 0:
            targetLines.append(line)
    return targetLines

def replace_temp_lines(lines, tags):
    if if_is_error(lines):
        log("tag Error ")
        return lines
    tempLines = []
    # remove tag lines
    for line in lines:
        if TAG_END in line or TAG_START in line:
            continue
        else:
            tempLines.append(line)

    targetLines = []
    state = 0
    hasTag = False
    isTagStart = False
    for line in tempLines:
        if START_IF in line or ELSE_IF in line:
            if state == 1:
                targetLines.append(TAG_END + "\n")
                isTagStart = False
            targetLines.append(line)
            if not line_isin_tags(line, tags):
                targetLines.append(TAG_START + "\n")
                isTagStart = True
                state = 1
            else:
                hasTag = True
                state = 0
        elif ELSE in line:
            if isTagStart :
                targetLines.append(TAG_END + "\n")
                isTagStart = False
            targetLines.append(line)
            if hasTag:
                targetLines.append(TAG_START + "\n")
                isTagStart = True
        elif END_IF in line:
            if isTagStart:
                targetLines.append(TAG_END + "\n")
            targetLines.append(line)
        else:
            targetLines.append(line)
    if REMOVE_TEXT:
        return remove_texts(targetLines)
    return targetLines

def replace_file(filePath, tags):
    if not os.path.isfile(filePath):
        return False
    # log("replaceing ", filePath)
    lines = []
    tempLines = []
    tag = 0
    hasReplace = False
    with open(filePath, "r") as file:
        allLines = file.readlines()
        # 可以使用pattern = re.compile(ur'^' + START_IF + '[\d\D]*?' + END_IF)
        for line in allLines:
            if tag == 0:
                if line.lstrip().startswith(START_IF):
                    tag = 1
                    tempLines = []
                    tempLines.append(line)
                else:
                    lines.append(line)
            elif tag == 1:
                tempLines.append(line)
                if line.lstrip().startswith(END_IF):
                    if (not hasReplace):
                        log("replaceing ", filePath)
                    hasReplace = True
                    tempLines = replace_temp_lines(tempLines, tags)
                    for line in tempLines:
                        lines.append(line)
                    tag = 0

    writeStr = ""
    for line in lines:
        writeStr += line
    with open(filePath, "w") as file:
        file.write(writeStr)
    return hasReplace

def file_endswith(file, endswith):
    if len(endswith) == 0:
        return True
    for data in endswith:
        if file.endswith(data):
            return True
    return False

def file_exclude(file, exclude):
    if len(exclude) == 0:
        return False
    file = file.replace("\\", "/").replace("//", "/")
    for data in exclude:
        if file.startswith(data) or data in file:
            return True
    return False

def file_is_include(file, endswith, exclude):
    return not file_exclude(file, exclude) and file_endswith(file, endswith)

def replace_dir_files(path, tags, endswith, exclude):
    fileCount = 0
    maxTime = 0
    maxFile = ""
    for root, dirs, files in os.walk(path):
        for file in files:
            fullPath = os.path.join(root, file)
            if not file_is_include(fullPath, endswith, exclude):
                continue
            fileCount += 1
            t = time.time()
            if replace_file(fullPath, tags):
                t = time.time() - t
            else:
                t = 0
            if t > maxTime:
                maxTime = t
                maxFile = fullPath
    log("max time use", str(maxTime) + "s", "file =", maxFile)
    log("replace count ", fileCount)

def read_cmds():
    cmds = {}
    try:
        inData = ""
        for arg in sys.argv[1:]:
            inData += arg
        datas = inData.split("--")
        for i in range(len(datas)):
            data = datas[i]
            temps = data.split("=")
            if len(temps) == 2:
                cmds[temps[0]] = temps[1]
            elif temps[0] == "help":
                cmds[temps[0]] = True
    except Exception as e:
        pass
    return cmds

if __name__ == '__main__':
    cmds = read_cmds()
    log("cmds == ", cmds)
    endswith = []
    exclude = []
    if cmds.has_key("help"):
        log(helpStr)
        exit(0)
    if not cmds.has_key("path"):
        log("please use --path = path")
        exit(0)
    if not cmds.has_key("tags"):
        log("please use --tags = \"tag1|tag2|tag3\"")
        exit(0)
    if cmds.has_key("endswith"):
        endswith = cmds["endswith"].split("|")
    if cmds.has_key("exclude"):
        exclude = cmds["exclude"].replace("\\", "/").replace("//", "/").split("|")

    log("endswith", endswith)
    log("exclude", exclude)

    path = cmds["path"]
    tagsStr = cmds["tags"]
    tags = tagsStr.split("|")
    REMOVE_TEXT = False
    if cmds.has_key("remove"):
        data = cmds["remove"]
        if data.lower() == "true":
            REMOVE_TEXT = True

    log("is remove", REMOVE_TEXT)
    log("start replace ", path)
    t = time.time()
    replace_dir_files(path, tags, endswith, exclude)
    log("use time", str(time.time() - t) + "s")
    log("replace end----")
