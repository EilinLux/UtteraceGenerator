#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import codecs
import os.path
import sys
import random
from _collections import deque


class Element():
    def __init__(self, _word, _weight):
        self.weight = _weight
        self.word = _word


class Grammar():
    def __init__(self, terminalTagDict, terminalListDict, globalGramFileNameList, localGramFilename):
        self.importGramList = list()
        self.sentList = list()
        self.ruleDict = dict()
        self.terminalTagDict = terminalTagDict
        self.terminalListDict = terminalListDict
        self.nonTerminalGramDict = dict()
        self.publicGramDict = list()
        self.parenthesisDict = []
        self.parenthesisIndex = 0
        for globalGramFileName in globalGramFileNameList:
            self.readGram(globalGramFileName)  # 1 globalGram / 1 domain
            self.importGramList.append(
                globalGramFileName[globalGramFileName.rfind('/') + 1:])
        self.gramname = os.path.basename(localGramFilename).split('.')[0]
        self.readGram(localGramFilename)  # an intent
        # self.importGramList.append(localGramFilename)

    def printDict(self):
        for key, value in self.terminalTagDict.iteritems():
            print(key + "\t" + value)

    def get_path_name(self, inp, branch_name=None):
        """ Resolve path with environment variable such as $RESOURCES
        inp : path with environment variable
        out : absolute path
            pasted by sang-ho lee, 20160620, to resolve $RESOURCES in json file
        """
        inp = inp.strip('/')
        out = ''
        ph = inp.split('/')
        for i in range(len(ph)):
            if ph[i][0] == '$':
                out += os.environ[ph[i][1:]]
            else:
                out += ph[i]
            if i < len(ph) - 1:
                out += '/'

        if branch_name != None and "{BRANCH}" in out:
            out = out.replace('{BRANCH}', branch_name)

        return out

    def readConfig(self, configName):
        if os.path.isfile(configName) == True:
            freadConfig = codecs.open(configName, 'r', encoding='utf8')

            with codecs.open(configName, 'r', encoding='utf8') as jsonFile:
                config = json.load(jsonFile)

            try:
                jsonFile.close()

                list0 = config["DATA"]["$list"]
                list = self.get_path_name(list0)

                terminalSetDict = dict()

                for element in config["NONTERMINAL"]:
                    if "__comment__" in element:
                        continue

                    if element not in self.terminalTagDict:
                        if "TAG" not in config["NONTERMINAL"][element]:
                            print(
                                "=========================================================")
                            print("ERROR 1: TAG of " + element +
                                  " is not in the config file")
                            print(
                                "=========================================================")
                            sys.exit(1)
                        self.terminalTagDict[element] = config["NONTERMINAL"][element]["TAG"]

                        if "LIST" not in config["NONTERMINAL"][element]:
                            print(
                                "=========================================================")
                            print("ERROR 2: List of " + element +
                                  " is not in the config file")
                            print(
                                "=========================================================")
                            sys.exit(1)
                        fread = codecs.open(config["NONTERMINAL"][element]["LIST"].replace("$list", list), 'r',
                                            encoding='utf8')

                        for line in fread:
                            word = line.lower().replace(u'\ufeff', '')
                            word = word.strip()
                            if word == "":
                                continue

                            # and word in self.terminalListDict[element]: continue;
                            if element not in self.terminalListDict:
                                self.terminalListDict[element] = []
                                terminalSetDict[element] = set()

                            if word not in terminalSetDict[element]:
                                self.terminalListDict[element].append(word)
                                terminalSetDict[element].add(word)

                freadConfig.close()
            except ValueError:
                print("=========================================================")
                print('ERROR3: Deconding JSON has failed')
                print("=========================================================")
                sys.exit(1)
        else:
            print('WARNING: config (' + configName + ') file is missed (no error)')

    def readConfig_each(self, configName, branch, node, common_dir=None, domain_dir=None):

        # TODO : allow all variable?
        default_plist_path = None

        if os.path.isfile(configName) == True:
            freadConfig = codecs.open(configName, 'r', encoding='utf8')

            with codecs.open(configName, 'r', encoding='utf8') as jsonFile:
                config = json.load(jsonFile)
            try:
                jsonFile.close()

                # override
                if "DATA" in config:
                    dataDict = config["DATA"]
                    if '$list' in dataDict:  # deprecated?
                        default_plist_path = self.get_path_name(
                            dataDict["$list"], branch)
                    if '$common_dir' in dataDict:
                        common_dir = self.get_path_name(
                            dataDict["$common_dir"], branch)
                    if '$domain_dir' in dataDict:
                        domain_dir = self.get_path_name(
                            dataDict["$domain_dir"], branch)

                # list0 = config["DATA"]["$list"]
                # list = self.get_path_name(list0)

                terminalSetDict = dict()

                # if "{BRANCH}" in list :
                #    list = list.replace('{BRANCH}', branch)

                for element in config["NONTERMINAL"]:
                    # print ('>> Loading ' + element
                    if "__comment__" in element:
                        continue
                    if element == node:
                        if element not in self.terminalTagDict:
                            print('>> Loading ' + element)
                            if "TAG" not in config["NONTERMINAL"][element]:
                                print(
                                    "=========================================================")
                                print("ERROR 1: TAG of " + element +
                                      " is not in the config file")
                                print(
                                    "=========================================================")
                                sys.exit(1)
                            self.terminalTagDict[element] = config["NONTERMINAL"][element]["TAG"]

                            if "LIST" not in config["NONTERMINAL"][element]:
                                print(
                                    "=========================================================")
                                print("ERROR 2: List of " + element +
                                      " is not in the config file")
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            list_path = config["NONTERMINAL"][element]["LIST"]
                            if default_plist_path != None:
                                list_path = list_path.replace(
                                    "$list", default_plist_path)
                            if common_dir != None:
                                list_path = list_path.replace(
                                    "$common_dir", common_dir)
                            if domain_dir != None:
                                list_path = list_path.replace(
                                    "$domain_dir", domain_dir)

                            fread = codecs.open(
                                list_path, 'r', encoding='utf8')

                            for line in fread:
                                word = line.replace(u'\ufeff', '')
                                word = word.lower().replace('  ', ' ').strip()
                                if word == "":
                                    continue

                                if word.count('|') >= 2:
                                    print('Error: "' + word +
                                          '" is in the phrase list (Double bar)')
                                    continue

                                if word.count('[') >= 2:
                                    print(
                                        'Error: "' + word + '" is in the phrase list (Double left bracket)')
                                    continue

                                if word.count(']') >= 2:
                                    print(
                                        'Error: "' + word + '" is in the phrase list (Double Right bracket)')
                                    continue

                                if '|' in word:
                                    word = word[:word.rfind('|')].strip()

                                # and word in self.terminalListDict[element]: continue;
                                if element not in self.terminalListDict:
                                    self.terminalListDict[element] = []
                                    terminalSetDict[element] = set()

                                if word not in terminalSetDict[element]:
                                    self.terminalListDict[element].append(word)
                                    terminalSetDict[element].add(word)

                                if '[' in word and ']' in word:
                                    word2 = word.replace('[', ' [')
                                    word2 = word2.replace(']', '] ')
                                    word2 = word2.replace('  ', ' ').strip()

                                    if word2 not in terminalSetDict[element]:
                                        self.terminalListDict[element].append(
                                            word2)
                                        terminalSetDict[element].add(word2)

                                    wordList = word.split()
                                    word3 = ''
                                    for wordSegment in wordList:
                                        if '[' in wordSegment and ']' in wordSegment:
                                            if wordSegment[0] != '[' or wordSegment[len(wordSegment) - 1] != ']':
                                                newWordSegment = '[' + wordSegment.replace('[', '').replace(']',
                                                                                                            '') + ']'
                                                word3 += newWordSegment + ' '
                                            else:
                                                word3 += wordSegment + ' '
                                        else:
                                            word3 += wordSegment + ' '

                                    word3 = word3.strip()
                                    if word3 not in terminalSetDict[element]:
                                        self.terminalListDict[element].append(
                                            word3)
                                        terminalSetDict[element].add(word3)
                            break

                freadConfig.close()
            except ValueError:
                print("=========================================================")
                print('ERROR3: Deconding JSON has failed')
                print("=========================================================")
                sys.exit(1)
        else:
            print('WARNING: config (' + configName + ') file is missed (no error)')

    def try_parse(self, string, fail=None):
        try:
            return int(string)
        except Exception:
            return fail

    def readGram(self, gramFileName):
        line_no = 0

        if os.path.isfile(gramFileName) == True:
            freadGram = codecs.open(gramFileName, 'r', encoding='utf8')

            # origGramFileName =  gramFileName
            print(
                'Load a grammar: [' + gramFileName[gramFileName.rfind('/') + 1:] + ']')
            if gramFileName[gramFileName.rfind('/') + 1:-5] not in self.importGramList:
                self.importGramList.append(
                    gramFileName[gramFileName.rfind('/') + 1:-5])

            weight = None
            state = ""
            for line in freadGram:
                line_no += 1
                if '#' in line:
                    line = line[:line.find('#')]

                newLine = line.replace("\n", "").replace(
                    "\r", "").replace("\t", "")

                if len(newLine.strip()) == 0:
                    continue

                if newLine.find(";") < 0:
                    state += newLine + " "
                    continue

                else:
                    state += newLine.replace(";", "")
                    state = state.replace("(", " ( ").replace("[", " [ ").replace(")", " ) ").replace("]",
                                                                                                      " ] ").replace(
                        "|", " | ").replace("/", " / ").replace("  ", " ").replace(">", "> ").replace("<", " <")
                    if state[:8] == "grammar ":
                        state = ""
                        continue

                    if state[:7] == 'import ':
                        importGramFileName = state[7:].strip()

                        print('Import a grammar: [' + importGramFileName + '.gram] from [' + gramFileName[
                            gramFileName.rfind(
                                '/') + 1:] + ']')
                        if importGramFileName in self.importGramList:
                            print(
                                "=========================================================")
                            print('ERROR: The grammar file ' + importGramFileName + ' is imported multiple times (Line No.:' + str(
                                line_no) + ')')
                            print(
                                "=========================================================")
                            sys.exit(1)

                        self.importGramList.append(importGramFileName)

                        importGramFileName = gramFileName[:gramFileName.rfind(
                            '/')] + '/' + importGramFileName + '.gram'
                        # print importGramFileName
                        self.readImportGram(importGramFileName)
                        state = ""
                        continue

                    if state.find('=') < 0:
                        print(
                            "=========================================================")
                        print('ERROR: The statement has no \'=\' in ' +
                              state + ' (Line No.:' + str(line_no) + ')')
                        print(
                            "=========================================================")
                        sys.exit(1)

                    parStack = list()
                    parIndexStack = list()

                    index = 0
                    splits = state.split('=')

                    if len(splits) != 2:
                        print(
                            "=========================================================")
                        print('ERROR: The statement has multiple \'=\' or semicolon \';\' is missed in ' + state + ' (Line No.:' + str(
                            line_no) + ')')
                        print(
                            "=========================================================")
                        sys.exit(1)

                    isPublic = False

                    nonTerminal = splits[0].strip()
                    # grammar error checking
                    tmpList = nonTerminal.split('__')
                    if len(tmpList) == 3:
                        print("subgoal is not well-defined: " + nonTerminal)

                    if 'public ' in nonTerminal:
                        isPublic = True
                        startindex = nonTerminal.index("<")
                        nonTerminal = nonTerminal[startindex:]

                    if nonTerminal[0] != "<" or nonTerminal[len(nonTerminal) - 1] != ">":
                        print(
                            "=========================================================")
                        print('ERROR: The nonterminal should be \'<XXX >\' in ' + state + ' (Line No.:' + str(
                            line_no) + ')')
                        print(
                            "=========================================================")
                        sys.exit(1)

                    if nonTerminal in self.nonTerminalGramDict:
                        print(
                            "=========================================================")
                        print('ERROR: Non-terminal ' + nonTerminal + ' is defined multiple times in ' + state + ' (Line No.:' + str(
                            line_no) + ')')
                        print(
                            "=========================================================")
                        sys.exit(1)

                    utter = splits[1].strip()  # rightHand side
                    newUtter = utter

                    i = 0
                    while True:
                        if i >= len(newUtter):
                            if len(parStack) > 0:
                                print(
                                    "=========================================================")
                                print('ERROR: parenthesis is not matched in ' + state + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)
                            break

                        ch = newUtter[i]
                        if ch == ' ':
                            i += 1
                            continue

                        if ch == '(':
                            parStack.append('(')
                            parIndexStack.append(i)

                        elif ch == "[":
                            parStack.append('[')
                            parIndexStack.append(i)

                        elif ch == ")":
                            if len(parStack) <= 0:
                                print(
                                    "=========================================================")
                                print('ERROR -5: parenthesis is not matched in ' + state + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)
                            par = parStack[len(parStack) - 1]
                            startIndex = parIndexStack[len(parIndexStack) - 1]
                            endIndex = i

                            if par == "[" or par == "{":
                                print(
                                    "=========================================================")
                                print('ERROR -4: parenthesis is not matched in ' + state + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            parStack.pop()
                            parIndexStack.pop()

                            id = "#" + str(self.parenthesisIndex)
                            nid = self.parenthesisIndex
                            self.parenthesisIndex += 1
                            content = newUtter[startIndex + 1:endIndex]
                            if '(' in content or '[' in content or ')' in content or ']' in content:
                                print(
                                    "=========================================================")
                                print('ERROR -1: parenthesis error in ' +
                                      state + ' (Line No.:' + str(line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            splits2 = content.split('|')

                            self.parenthesisDict.append([])
                            for strTemp in splits2:
                                newStr = strTemp.strip()
                                weight = 1

                                leftIndex = newStr.find('/')
                                if leftIndex >= 0:
                                    rightIndex = newStr.rfind('/')

                                    if leftIndex == rightIndex:
                                        print(
                                            "=========================================================")
                                        print('ERROR -101: / is used for weight as (/70/ what| /30/where)' + strTemp + ' (Line No.:' + str(
                                            line_no) + ')')
                                        print(
                                            "=========================================================")
                                        sys.exit(1)

                                    weight = self.try_parse(
                                        newStr[leftIndex + 1:rightIndex].strip())

                                    if weight == None:
                                        print(
                                            "=========================================================")
                                        print('ERROR -102: / weight / should be an integer ' + strTemp + ' (Line No.:' + str(
                                            line_no) + ')')
                                        print(
                                            "=========================================================")
                                        sys.exit(1)

                                    newStr = newStr[rightIndex + 1:].strip()

                                self.parenthesisDict[nid].append(
                                    Element(newStr, weight))
                            newUtter = newUtter[:startIndex] + \
                                id + newUtter[endIndex + 1:]

                            i = len(newUtter[:startIndex] + id)

                        elif ch == "]":
                            if len(parStack) <= 0:
                                print(
                                    "=========================================================")
                                print('ERROR -2: parenthesis is not matched in ' + state + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            par = parStack[len(parStack) - 1]
                            startIndex = parIndexStack[len(parIndexStack) - 1]
                            endIndex = i

                            if par == "(" or par == "{":
                                print(
                                    "=========================================================")
                                print('ERROR -3: parenthesis is not matched in ' + state + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            parStack.pop()
                            parIndexStack.pop()

                            id = "#" + str(self.parenthesisIndex)
                            nid = self.parenthesisIndex

                            self.parenthesisIndex += 1
                            content = newUtter[startIndex + 1:endIndex]
                            if '(' in content or '[' in content or ')' in content or ']' in content:
                                print(
                                    "=========================================================")
                                print('ERROR -1: parenthesis error in "' +
                                      state + '"' + ' (Line No.:' + str(line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            splits2 = content.split('|')

                            self.parenthesisDict.append([])
                            self.parenthesisDict[nid].append(Element("", 1))
                            for strTemp in splits2:
                                newStr = strTemp.strip()
                                weight = 1

                                leftIndex = newStr.find('/')
                                if leftIndex >= 0:
                                    rightIndex = newStr.rfind('/')

                                    if leftIndex == rightIndex:
                                        print(
                                            "=========================================================")
                                        print('ERROR -101: / is used for weight as (/70/ what| /30/where)' + strTemp + ' (Line No.:' + str(
                                            line_no) + ')')
                                        print(
                                            "=========================================================")
                                        sys.exit(1)

                                    weight = self.try_parse(
                                        newStr[leftIndex + 1:rightIndex].strip())

                                    if weight == None:
                                        print(
                                            "=========================================================")
                                        print('ERROR -102: / weight / should be an integer ' + strTemp + ' (Line No.:' + str(
                                            line_no) + ')')
                                        print(
                                            "=========================================================")
                                        sys.exit(1)

                                    newStr = newStr[rightIndex + 1:].strip()
                                self.parenthesisDict[nid].append(
                                    Element(newStr, weight))

                            newUtter = newUtter[:startIndex] + \
                                id + newUtter[endIndex + 1:]

                            i = len(newUtter[:startIndex] + id)
                        i += 1

                    newUtter = newUtter.replace(
                        "  ", " ").replace("  ", " ").strip()
                    splits3 = newUtter.split('|')
                    for strTemp in splits3:
                        newStr = strTemp.strip()
                        weight = 1

                        leftIndex = newStr.find('/')
                        if leftIndex >= 0:
                            rightIndex = newStr.rfind('/')

                            if leftIndex == rightIndex:
                                print(
                                    "=========================================================")
                                print('ERROR -101: / is used for weight as (/70/ what| /30/where) at \'' + strTemp + '\'' + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            weight = self.try_parse(
                                newStr[leftIndex + 1:rightIndex].strip())

                            if weight == None:
                                print(
                                    "=========================================================")
                                print('ERROR -102: / weight / should be an integer in \'' + strTemp + '\'' + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            newStr = newStr[rightIndex + 1:].strip()

                        # self.nonTerminalGramDict.setdefault(nonTerminal, []).append(Element(newStr, weight))
                        if nonTerminal not in self.nonTerminalGramDict:
                            self.nonTerminalGramDict[nonTerminal] = []
                        self.nonTerminalGramDict[nonTerminal].append(
                            Element(newStr, weight))
                        # print nonTerminal +" "+newStr

                        if isPublic == True:
                            self.publicGramDict.append(
                                Element(nonTerminal, weight))

                    state = ""

            freadGram.close()

        else:
            print("=========================================================")
            print("ERROR 3: No grammar file '" + gramFileName + "'")
            print("=========================================================")
            sys.exit(1)

    def readImportGram(self, gramFileName):
        line_no = 0
        if os.path.isfile(gramFileName) == True:
            freadGram = codecs.open(gramFileName, 'r', encoding='utf8')

            weight = None
            state = ""
            for line in freadGram:
                line_no += 1
                if '#' in line:
                    line = line[:line.find('#')]

                newLine = line.replace("\n", "").replace(
                    "\r", "").replace("\t", "")

                if len(newLine.strip()) == 0:
                    continue

                if newLine.find(";") < 0:
                    state += newLine + " "
                    continue

                else:
                    state += newLine.replace(";", "")
                    state = state.replace("(", " ( ").replace("[", " [ ").replace(")", " ) ").replace("]",
                                                                                                      " ] ").replace(
                        "|", " | ").replace("/", " / ").replace("  ", " ")

                    if 'public ' in state[:7]:
                        state = ""
                        continue

                    if state[:8] == "grammar ":
                        state = ""
                        continue

                    if state[:7] == 'import ':
                        importGramFileName = state[7:].strip()

                        print('Import a grammar: [' + importGramFileName + '.gram] from [' + gramFileName[
                            gramFileName.rfind(
                                '/') + 1:] + ']')
                        if importGramFileName in self.importGramList:
                            print(
                                "=========================================================")
                            print('ERROR: The grammar file ' + importGramFileName + ' is imported multiple times (Line No.:' + str(
                                line_no) + ')')
                            print(
                                "=========================================================")
                            sys.exit(1)

                        self.importGramList.append(importGramFileName)
                        importGramFileName = gramFileName[:gramFileName.rfind(
                            '/')] + '/' + importGramFileName + '.gram'
                        self.readImportGram(importGramFileName)
                        state = ""
                        continue

                    if state.find('=') < 0:
                        print(
                            "=========================================================")
                        print('ERROR: The statement has no \'=\' in ' +
                              state + ' (Line No.:' + str(line_no) + ')')
                        print(
                            "=========================================================")
                        sys.exit(1)

                    parStack = list()
                    parIndexStack = list()

                    index = 0
                    splits = state.split('=')

                    if len(splits) != 2:
                        print(
                            "=========================================================")
                        print('ERROR: The statement has multiple \'=\' or semicolon \';\' is missed in ' + state + ' (Line No.:' + str(
                            line_no) + ')')
                        print(
                            "=========================================================")
                        sys.exit(1)

                    nonTerminal = splits[0].strip()
                    # grammar error checking
                    tmpList = nonTerminal.split('__')
                    if len(tmpList) == 3:
                        print("subgoal is not well-defined: " + nonTerminal)

                    if nonTerminal[0] != "<" or nonTerminal[len(nonTerminal) - 1] != ">":
                        print(
                            "=========================================================")
                        print('ERROR: The nonterminal should be \'<XXX >\' in ' + state + ' (Line No.:' + str(
                            line_no) + ')')
                        print(
                            "=========================================================")
                        sys.exit(1)

                    if nonTerminal in self.nonTerminalGramDict:
                        print(
                            "=========================================================")
                        print('ERROR: Non-terminal ' + nonTerminal + ' is defined multiple times in ' + state + ' (Line No.:' + str(
                            line_no) + ')')
                        print(
                            "=========================================================")
                        sys.exit(1)

                    utter = splits[1].strip()  # rightHand side
                    newUtter = utter

                    i = 0
                    while True:
                        if i >= len(newUtter):
                            if len(parStack) > 0:
                                print(
                                    "=========================================================")
                                print('ERROR: parenthesis is not matched in ' + state + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)
                            break

                        ch = newUtter[i]
                        if ch == ' ':
                            i += 1
                            continue

                        if ch == '(':
                            parStack.append('(')
                            parIndexStack.append(i)

                        elif ch == "[":
                            parStack.append('[')
                            parIndexStack.append(i)

                        elif ch == ")":
                            if len(parStack) <= 0:
                                print(
                                    "=========================================================")
                                print('ERROR -5: parenthesis is not matched in ' + state + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)
                            par = parStack[len(parStack) - 1]
                            startIndex = parIndexStack[len(parIndexStack) - 1]
                            endIndex = i

                            if par == "[" or par == "{":
                                print(
                                    "=========================================================")
                                print('ERROR -4: parenthesis is not matched in ' + state + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            parStack.pop()
                            parIndexStack.pop()

                            id = "#" + str(self.parenthesisIndex)
                            nid = self.parenthesisIndex
                            self.parenthesisIndex += 1
                            content = newUtter[startIndex + 1:endIndex]
                            if '(' in content or '[' in content or ')' in content or ']' in content:
                                print(
                                    "=========================================================")
                                print('ERROR -1: parenthesis error in ' +
                                      state + ' (Line No.:' + str(line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            splits2 = content.split('|')

                            self.parenthesisDict.append([])
                            for strTemp in splits2:
                                newStr = strTemp.strip()
                                weight = 1

                                leftIndex = newStr.find('/')
                                if leftIndex >= 0:
                                    rightIndex = newStr.rfind('/')

                                    if leftIndex == rightIndex:
                                        print(
                                            "=========================================================")
                                        print('ERROR -101: / is used for weight as (/70/ what| /30/where)' + strTemp + ' (Line No.:' + str(
                                            line_no) + ')')
                                        print(
                                            "=========================================================")
                                        sys.exit(1)

                                    weight = self.try_parse(
                                        newStr[leftIndex + 1:rightIndex].strip())

                                    if weight == None:
                                        print(
                                            "=========================================================")
                                        print('ERROR -102: / weight / should be an integer ' + strTemp + ' (Line No.:' + str(
                                            line_no) + ')')
                                        print(
                                            "=========================================================")
                                        sys.exit(1)

                                    newStr = newStr[rightIndex + 1:].strip()

                                self.parenthesisDict[nid].append(
                                    Element(newStr, weight))
                            newUtter = newUtter[:startIndex] + \
                                id + newUtter[endIndex + 1:]

                            i = len(newUtter[:startIndex] + id)

                        elif ch == "]":
                            if len(parStack) <= 0:
                                print(
                                    "=========================================================")
                                print('ERROR -2: parenthesis is not matched in ' + state + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            par = parStack[len(parStack) - 1]
                            startIndex = parIndexStack[len(parIndexStack) - 1]
                            endIndex = i

                            if par == "(" or par == "{":
                                print(
                                    "=========================================================")
                                print('ERROR -3: parenthesis is not matched in ' + state + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            parStack.pop()
                            parIndexStack.pop()

                            id = "#" + str(self.parenthesisIndex)
                            nid = self.parenthesisIndex

                            self.parenthesisIndex += 1
                            content = newUtter[startIndex + 1:endIndex]
                            if '(' in content or '[' in content or ')' in content or ']' in content:
                                print(
                                    "=========================================================")
                                print('ERROR -1: parenthesis error in "' + state
                                      + '"' + ' (Line No.:' + str(line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            splits2 = content.split('|')

                            self.parenthesisDict.append([])
                            self.parenthesisDict[nid].append(Element("", 1))
                            for strTemp in splits2:
                                newStr = strTemp.strip()
                                weight = 1

                                leftIndex = newStr.find('/')
                                if leftIndex >= 0:
                                    rightIndex = newStr.rfind('/')

                                    if leftIndex == rightIndex:
                                        print(
                                            "=========================================================")
                                        print('ERROR -101: / is used for weight as (/70/ what| /30/where)' + strTemp + ' (Line No.:' + str(
                                            line_no) + ')')
                                        print(
                                            "=========================================================")
                                        sys.exit(1)

                                    weight = self.try_parse(
                                        newStr[leftIndex + 1:rightIndex].strip())

                                    if weight == None:
                                        print(
                                            "=========================================================")
                                        print('ERROR -102: / weight / should be an integer ' + strTemp + ' (Line No.:' + str(
                                            line_no) + ')')
                                        print(
                                            "=========================================================")
                                        sys.exit(1)

                                    newStr = newStr[rightIndex + 1:].strip()
                                self.parenthesisDict[nid].append(
                                    Element(newStr, weight))

                            newUtter = newUtter[:startIndex] + \
                                id + newUtter[endIndex + 1:]

                            i = len(newUtter[:startIndex] + id)
                        i += 1

                    newUtter = newUtter.replace(
                        "  ", " ").replace("  ", " ").strip()
                    splits3 = newUtter.split('|')
                    for strTemp in splits3:
                        newStr = strTemp.strip()
                        weight = 1

                        leftIndex = newStr.find('/')
                        if leftIndex >= 0:
                            rightIndex = newStr.rfind('/')

                            if leftIndex == rightIndex:
                                print(
                                    "=========================================================")
                                print('ERROR -101: / is used for weight as (/70/ what| /30/where) at \'' + strTemp + '\'' + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            weight = self.try_parse(
                                newStr[leftIndex + 1:rightIndex].strip())

                            if weight == None:
                                print(
                                    "=========================================================")
                                print('ERROR -102: / weight / should be an integer in \'' + strTemp + '\'' + ' (Line No.:' + str(
                                    line_no) + ')')
                                print(
                                    "=========================================================")
                                sys.exit(1)

                            newStr = newStr[rightIndex + 1:].strip()

                        if nonTerminal not in self.nonTerminalGramDict:
                            self.nonTerminalGramDict[nonTerminal] = []
                        self.nonTerminalGramDict[nonTerminal].append(
                            Element(newStr, weight))

                    state = ""

            freadGram.close()

        else:
            print("=========================================================")
            print("ERROR 3: No import grammar file '" + gramFileName + "'")
            print("=========================================================")
            sys.exit(1)

    def generateUtter(self, configName="", branch="", common_dir=None, domain_dir=None):
        weights = []
        for value in self.publicGramDict:
            weights += [value.word] * value.weight

        choice = random.choice(weights)

        weights = []

        for value in self.nonTerminalGramDict[choice]:
            weights += [value.word] * value.weight

        choiceWord = random.choice(weights)

        wordList = list()

        wordDeque = deque(choiceWord.split(' '))

        wordList.append(
            (')#' + choice.replace("<", "").replace(">", "") + '%' + wordDeque[0].replace("<", "").replace(">", "")))

        while True:
            if len(wordDeque) == 0:
                break

            node = wordDeque.popleft()

            if node == "":
                continue

            if node[0] == '#':
                parIndex = int(node[1:])
                if parIndex >= len(self.parenthesisDict):
                    print("=========================================================")
                    print("ERROR 6: parathesis '" + node + "' error")
                    print("=========================================================")
                    sys.exit(1)

                weights = []
                for value in self.parenthesisDict[parIndex]:
                    weights += [value.word] * value.weight

                choiceWord2 = random.choice(weights)
                wordDeque.extendleft(reversed(choiceWord2.split(' ')))

            elif node[0] == '<':
                if node[len(node) - 1] != '>':
                    print("=========================================================")
                    print("ERROR 5: '< >' is not matched in '" + node + "'")
                    print("=========================================================")
                    sys.exit(1)

                if node not in self.nonTerminalGramDict:
                    print("=========================================================")
                    print("ERROR 7: non-terminal '" +
                          node + "' is not defined")
                    print("=========================================================")
                    sys.exit(1)

                weights = []
                for value in self.nonTerminalGramDict[node]:
                    weights += [value.word] * value.weight

                choiceWord2 = random.choice(weights)

                wordItems = choiceWord2.split(' ')
                # if len(wordItems) == 1 and 'SUB__' in wordItems[0][:6].upper():
                if 'SUB__' in node[:6].upper():
                    subList = re.sub('[<>]', '', node).split(
                        '__')  # split as sub, domain, intent
                    if len(subList) == 4:

                        subItemList = ['(']
                        for itemIdx in range(len(wordItems)):
                            subItemList.append(wordItems[itemIdx])
                        # print ("subList: " + node
                        returned = subList[3]
                        tailPart = ')#' + subList[1] + \
                            '%' + subList[2] + '/B-' + returned
                        subItemList.append(tailPart)
                        wordDeque.extendleft(reversed(subItemList))
                    elif len(subList) == 3:
                        print('subGoal rule is not well-defined: '
                              + subList[0] + " " + subList[1] + " " + subList[2])

                else:
                    tmp2 = reversed(wordItems)
                    wordDeque.extendleft(tmp2)

            elif node[0] == '$':
                if node not in self.terminalListDict:
                    self.readConfig_each(
                        configName, branch, node, common_dir, domain_dir)

                if node not in self.terminalListDict:
                    print("=========================================================")
                    print("ERROR 8: '" + node + "' is not defined in json file")
                    print("=========================================================")
                    sys.exit(1)

                if node not in self.terminalTagDict:
                    print("=========================================================")
                    print("ERROR 9: '" + node +
                          "' is not defined in json file (tag)")
                    print("=========================================================")
                    sys.exit(1)

                index = random.randint(0, len(self.terminalListDict[node]) - 1)

                word = self.terminalListDict[node][index]
                tag = self.terminalTagDict[node]

                if tag != '':
                    wordItem = word.split(' ')

                    tagStartIndex = 0
                    tagEndIndex = len(word) - 1

                    if '[' in word and ']' in word:
                        for i in range(len(wordItem)):
                            if '[' in wordItem[i]:
                                tagStartIndex = i
                                wordItem[i] = wordItem[i].replace('[', '')
                            if ']' in wordItem[i]:
                                tagEndIndex = i
                                wordItem[i] = wordItem[i].replace(']', '')

                    for i in range(len(word.split(' '))):
                        wordItem[i] = wordItem[i].replace(
                            '[', '').replace(']', '')
                        if i == tagStartIndex:
                            wordList.append(wordItem[i] + "/b-" + tag)
                        elif i > tagStartIndex and i <= tagEndIndex:
                            wordList.append(wordItem[i] + "/i-" + tag)
                        else:
                            wordList.append(wordItem[i])
                else:
                    wordList.append(word)

            elif node[len(node) - 1] == '>' and node[0] != '<':
                print("=========================================================")
                print("ERROR 6: '< >' is not matched in '" + node + "'")
                print("=========================================================")
                sys.exit(1)

            else:
                if 'JOSA1__' in node[:7].upper():
                    josaGram = node.split('__')
                    if len(josaGram) != 3:
                        print("ERROR JOSA: Rule is not correctly defined")
                        sys.exit(1)
                    # pick target noun
                    nounWordKey = "$" + josaGram[1].split('_')[0].upper()
                    nounWordIdx = random.randint(
                        0, len(self.terminalListDict[nounWordKey]) - 1)
                    # make word(s) as list
                    nounWordChoice = self.terminalListDict[nounWordKey][nounWordIdx].split(
                    )
                    # pick josa
                    josaKey = '$JOSA_' + josaGram[2].upper()
                    josaIdx = random.randint(
                        0, len(self.terminalListDict[josaKey]) - 1)
                    josaChoice = self.terminalListDict[josaKey][josaIdx]
                    # combine
                    nounLastWord = nounWordChoice[-1] + josaChoice
                    JosaPhrase = []
                    for i in range(len(nounWordChoice) - 1):
                        JosaPhrase.append(nounWordChoice[i])
                    JosaPhrase.append(nounLastWord)
                    # tag this phrase
                    taggedJosaPhrase = []
                    for i in range(len(JosaPhrase)):
                        if i == 0:
                            taggedJosaPhrase.append(
                                JosaPhrase[i] + "/B-" + josaGram[1].upper())
                        else:
                            taggedJosaPhrase.append(
                                JosaPhrase[i] + "/I-" + josaGram[1].upper())

                    wordDeque.extendleft(reversed(taggedJosaPhrase))

                else:
                    wordList.append(node.lstrip().rstrip())

        # extract utterance with tags
        words = " ".join(wordList[1:]).strip()
        if len(words) < 1:
            print("")
            print("=========================================================")
            print("ERROR : Empty utterance was generated by this gram file")
            print("=========================================================")
            sys.exit(1)

        words = "(" + words
        # intent append
        words += wordList[0]
        words = words.replace(" )", ")").replace("( ", "(").replace(
            " /", "/").replace('[', '').replace(']', '')
        return words
