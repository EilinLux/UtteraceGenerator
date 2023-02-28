#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
from Grammar import Grammar
import codecs
import time
import json
import os.path
from shutil import copyfile
import re

import traceback
from os import listdir


def parse_args():
    # print 'Number of arguments:', len(sys.argv), 'arguments.'
    "Utterance generation based on the grammar"
    parser = argparse.ArgumentParser(description='Utterance Generation')

    parser.add_argument('-c', '--config_file', type=str,
                        help='Enter a config json file name (e.g., data/date_gen_config_yelp.json)', required=True)
    parser.add_argument('-b', '--branch', type=str,
                        help='Enter a branch name (e.g., DEV, MAIN)', default='MAIN')
    parser.add_argument('-gram_dir', '--grammar_dir', type=str,
                        help='Enter a grammar file directory  (e.g., data')
    parser.add_argument('-out_dir', '--output_dir', type=str,
                        help='Enter a output file directory (e.g., utter)')
    parser.add_argument('-C', '--common_dir', type=str,
                        help='Enter a common directory  (e.g., data', required=False)
    parser.add_argument('-D', '--domain_dir', type=str,
                        help='Enter a local domain directory (e.g., utter)')
    parser.add_argument('-n', '--utterance_number', type=int,
                        help='Enter the number of utterances for generation (e.g., 10000)', default=10000)  #
    parser.add_argument('-m', '--mode', type=str,
                        help='Enter "date" or "time" for the list', default="")
    parser.add_argument('-to_gen', '--to_gen', type=str,
                        help='Enter to generate (e.g., localsearch_root, localsearch_followup)', nargs='+')
    parser.add_argument(
        '-i', '--include', help='build only grams containing include string', type=str, default='')
    parser.add_argument(
        '-r', '--gram_range', help='build only grams in the range,  ex:10000~12135', type=str)

    args = parser.parse_args()
    return args


def command_or_json(args, gram_dir, out_dir, gen_filename):
    if args.grammar_dir != None:
        gram_dir = args.grammar_dir
    if args.output_dir != None:
        out_dir = args.output_dir
    if args.to_gen != None:
        gen_filename = list()
        for elem in args.to_gen:
            print("to_gen is:", elem)
            gen_filename.append(elem)
    if args.gram_range != None:
        gram_range = list()
        gram_range = args.gram_range.split('~')
    else:
        gram_range = None

    return gram_dir, out_dir, gen_filename, gram_range


def get_path_name(inp, branch_name=None):
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


def readFilename(configName, gen_filename, global_gen_filename, override_utter_num_weights, special_data_files):
    if os.path.isfile(configName) == True:
        with codecs.open(configName, 'r', encoding='utf8') as jsonFile:
            config = json.load(jsonFile)
        try:
            jsonFile.close()
            try:
                gramdir = get_path_name(config["DATA"]["GRAM"], args.branch)
            except:
                gramdir = None

            try:
                outdir = get_path_name(config["DATA"]["OUTPUT"], args.branch)
            except:
                outdir = None

            try:
                utterNumWeight = float(config["DATA"]["UTTER_NUM_WEIGHT"])
            except:
                utterNumWeight = 1.0

            try:
                include_all_gram_files = False
                if "DATA_GEN" in config:
                    if len(config["DATA_GEN"]) == 0:
                        include_all_gram_files = True

                    for element in config["DATA_GEN"]:
                        if isinstance(element, list):
                            gramFileName = element[0]
                            overrideUtterNumWeight = float(element[1])
                            override_utter_num_weights[gramFileName] = overrideUtterNumWeight
                            gen_filename.append(gramFileName)
                        else:
                            gen_filename.append(element)
                else:
                    include_all_gram_files = True
            except Exception as e:
                gen_filename = None
                print(e)

            try:
                for element in config["DATA_GLOBAL_GEN"]:
                    global_gen_filename.append(element)
            except:
                global_gen_filename = None

            if "SPECIAL_DATA" in config:
                for f in config["SPECIAL_DATA"]:
                    special_data_files.append(f)

        except ValueError:
            print("decoding json failed")
            sys.exit(1)
    else:
        print("config file is missed")
        sys.exit(1)

    return gramdir, outdir, utterNumWeight, include_all_gram_files


def makeFilename(gramdir, outdir, each_filename, global_gen_filename):
    globalGramFileNameList = []
    try:
        for i in range(len(global_gen_filename)):
            globalGramFileName = global_gen_filename[i]
            if gramdir == "":
                globalGramFileName = globalGramFileName + ".gram"
            elif gramdir.startswith(".") | gramdir.startswith("~"):
                globalGramFileName = os.path.abspath(
                    gramdir) + "/" + globalGramFileName + ".gram"
            else:
                globalGramFileName = gramdir + "/" + globalGramFileName + ".gram"
                # check the file exists
            if os.path.isfile(globalGramFileName) is False:
                print("=========================================================")
                print("ERROR : globalGramFile is not exist:", globalGramFileName)
                print("=========================================================")
                sys.exit(1)
            else:
                globalGramFileNameList.append(globalGramFileName)

    except:
        print("=========================================================")
        print("ERROR : Enter the gramdirectory")
        print("=========================================================")
        sys.exit(1)
    try:
        if gramdir == "":
            gramFileName = each_filename + '.gram'
        elif gramdir.startswith(".") | gramdir.startswith("~"):
            gramFileName = os.path.abspath(
                gramdir) + '/' + each_filename + '.gram'
        else:
            gramFileName = gramdir + '/' + each_filename + '.gram'
    except:
        print("=========================================================")
        print("ERROR : Enter the gramdirectory")
        print("=========================================================")
        sys.exit(1)
    try:
        if outdir == "":
            outputName = each_filename.lower() + '.expand'
        elif outdir.startswith(".") | outdir.startswith("~"):
            outputName = os.path.abspath(
                outdir) + '/' + each_filename.lower() + '.expand'
        else:
            outputName = outdir + '/' + each_filename.lower() + '.expand'
    except:
        print("=========================================================")
        print("ERROR : Enter the outputdirectory")
        print("=========================================================")
        sys.exit(1)
    return globalGramFileNameList, gramFileName, outputName


utterance_re = re.compile(r'^\(([^)]*)\)(#.*)$', re.UNICODE)
tag_re = re.compile(r'/[biBI]-\w+')


def extract_annotation(line):
    match = utterance_re.match(line)
    assert match and len(match.groups()) == 2

    utterance = match.group(1)
    state = match.group(2)

    intent = state.split('__')[0]
    domain, _ = intent.split('%')

    annotations = []
    for token in utterance.split():
        match = tag_re.search(token)
        if match:
            annotations.append(match.group()[1:])
        else:
            annotations.append('o')

    annotation = ' '.join(annotations)
    utterance = tag_re.sub('', utterance)
    return [intent, utterance, annotation]


if __name__ == "__main__":

    args = parse_args()
    configName = args.config_file
    utterNum = args.utterance_number

    if args.include != None:
        include = args.include
    gen_filename = list()
    global_gen_filename = list()  # new one
    override_utter_num_weights = dict()
    special_data_files = []
    gramdir, outdir, utterNumWeight, include_all_gram_files = readFilename(configName, gen_filename,
                                                                           global_gen_filename,
                                                                           override_utter_num_weights,
                                                                           special_data_files)
    gramdir, outdir, gen_filename, gram_range = command_or_json(
        args, gramdir, outdir, gen_filename)

    if include_all_gram_files and gramdir != None and len(gen_filename) == 0:
        for f in listdir(gramdir):
            if os.path.isfile(os.path.join(gramdir, f)) and f != 'expand.json':
                gen_filename.append(os.path.splitext(f)[0])

    terminalTagDict = dict()
    terminalListDict = dict()

    # temporary directory
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    if gram_range != None:
        try:
            start = int(gram_range[0])
            end = int(gram_range[1])
        except:
            print(
                "I can't find start and end during specifying the range of gram files. usage:ex) -r 10000~12135")
            sys.exit(1)

    skip_mode = 0
    if len(include) > 0 and include.find('!') != -1:
        include = include.replace('!', '')
        skip_mode = 1

    # TODO: remove this later - now special data files are handled in Makefile.
    # They can be configured to be appended to "train mixed add/icm/stm" separately
    for f in special_data_files:
        src = os.path.join(gramdir, f)
        # dst = os.path.join(outdir, f)+".expand"
        dst = os.path.join(outdir, f)
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs((os.path.dirname(dst)))
        print("Special data: copying %s -> %s" % (src, dst))
        copyfile(src, dst)
        with open(dst, 'a') as f:
            f.writelines('\n')

    for each_filename in gen_filename:
        if len(include) > 0:
            if skip_mode > 0:
                if each_filename.lower().find(include.lower()) > -1:
                    continue
            else:
                if each_filename.lower().find(include.lower()) == -1:
                    continue

                    # to specify the range of gram files
        if gram_range != None:
            try:
                ruleIDStr = filter(lambda x: x.isdigit(), each_filename)
                if len(ruleIDStr) > 0:
                    ruleIDInt = int(ruleIDStr)
                    if ruleIDInt < start or ruleIDInt > end:
                        continue
                else:
                    print(" ! ", each_filename,
                          " file doesn't have the number in it  !")
                    continue
            except:
                print("An error occurs during specifying the range of gram files")
                sys.exit(1)

        globalGramFileNameList, localGramFileName, outputName = makeFilename(gramdir, outdir, each_filename,
                                                                             global_gen_filename)

        gram = Grammar(terminalTagDict, terminalListDict,
                       globalGramFileNameList, localGramFileName)

        mode = args.mode

        outputFileDir = os.path.dirname(outputName)
        if (not os.path.isdir(outputFileDir)):
            os.makedirs(outputFileDir)

        fwrite = codecs.open(outputName, 'w', encoding='utf8')

        gramName = each_filename

        if each_filename in override_utter_num_weights:
            targetUtterNum = utterNum * \
                override_utter_num_weights[each_filename]
        else:
            targetUtterNum = utterNum * utterNumWeight

        utterSet = set()
        dup = 0

        print("*" + args.branch + "* Start: utterance generation (" +
              localGramFileName, '+', configName + ")")

        time.time()
        index = 1
        while True:
            if (len(utterSet) >= targetUtterNum):
                break
            try:
                utter = gram.generateUtter(
                    configName, args.branch, args.common_dir, args.domain_dir)
            except Exception as e:
                print(" ")
                print(
                    "==========================================================================")
                print("ERROR 101 : syntax error, check below file ")
                print(localGramFileName)
                print(
                    "==========================================================================")
                print(traceback.print_exc())
                print(" ")
                sys.exit(1)
            if utter in utterSet:
                dup += 1
                if dup == 1000:
                    print('Termination (It generates 1000 same utterances).')
                    break
                continue

            if index % 50000 == 0:
                print(str(index) + ' UTT(s) Generated')
            index += 1

            utterSet.add(utter)
            if mode == "date" or mode == "time":
                fwrite.write(utter.split('\t')[0] + "\n")
            else:
                line = extract_annotation(utter)
                line[0] = gram.gramname
                fwrite.write('\t'.join(line) + "\n")
            dup = 0

        print('Statistics:')
        print('# of Sentences: ' + str(len(utterSet)))
        print('Done (' + str(time.perf_counter()) + " seconds)")

        fwrite.close()
