# Automated Utterance Generator

This Python project automates the generation of sample utterances for Natural Language Processing (NLP) tasks. By using a grammar-based approach, it ensures consistency, wider coverage, and eliminates duplicates in the generated utterances.

## Table of Contents

* [General Info](#general-info)
* [Features](#features)
* [Technologies](#technologies)
* [Setup](#setup)
    * [Creating a New Grammar](#creating-a-new-grammar)
    * [Adding Concepts](#adding-concepts)
* [Running the Generator](#running-the-generator)
* [File Examples](#file-examples)
    * [`<FOLDER-NAME>/grams/<FOLDER-NAME>_data_gen_config.json`](#folder-namegramsfolder-name_data_gen_configjson)
    * [`<FOLDER-NAME>/grams/<FOLDER-NAME>_global.gram`](#folder-namegramsfolder-name_globalgram)
    * [`<FOLDER-NAME>/grams/<FOLDER-NAME>_<NUMBER>.gram`](#folder-namegramsfolder-name_numbergram)
    * [`<FOLDER-NAME>/slot_dictionary/<ALIAS-NAME>.txt`](#folder-nameslot_dictionaryalias-nametxt)
    * [`outputs/<FOLDER-NAME>_<NUMBER>.expand`](#outputsfolder-name_numberexpand)


## General Info

This project helps in generating large sets of sample utterances, which are essential for training and evaluating NLP models, especially in the development of chatbots, voice assistants, and other conversational interfaces.

## Features

- **Grammar-based generation:** Define grammars to generate a wide range of variations.
- **Consistency and coverage:** Ensures consistent patterns and wider coverage of possible utterances.
- **Duplicate elimination:** Automatically removes duplicate utterances.
- **Reusability:**  Reuse lists and utterance collections across modules through shared slot dictionaries.
- **Concept management:** Easily add and manage concepts with associated lists.

## Technologies

- Python 3.8
- Libraries: `sys`, `argparse`, `codecs`, `time`, `json`, `os`, `shutil`, `re`, `traceback`, `random`

## Setup

### Creating a New Grammar

1. **Create a new folder** `<FOLDER-NAME>` inside the `grammars` directory.
2. **Create two subfolders:** `gram` and `slot_dictionary` within `<FOLDER-NAME>`.
3. **In the `gram` folder:**
   - Create a configuration file named `<FOLDER-NAME>_data_gen_config.json`.
   - Create one or more `.gram` files (a global grammar file and optional specific grammar files).
4. **In the `slot_dictionary` folder:**
   - Create one or more `.expand` files containing lists of words or phrases.


### Adding Concepts

To add a new concept to your configuration file, use the `add_concept.py` script:

```bash
python add_concept.py -c grammars/<FOLDER-NAME>/grams/<FOLDER-NAME>_data_gen_config.json -k <CONCEPT_KEY> -l <CONCEPT_LIST_FILE>
```
Replace <CONCEPT_KEY> with the key for your concept (e.g., MOVIE).
Replace <CONCEPT_LIST_FILE> with the path to a text file containing a list of items for the concept (e.g., movie.txt).
### Running the Generator
Use the gram_gen.py script to generate utterances:

```
python gram_gen.py -c grammars/<FOLDER-NAME>/grams/<FOLDER-NAME>_data_gen_config.json -n <NUMBER_OF_UTTERANCES>
```

Replace <FOLDER-NAME> with the name of your grammar folder.
Replace <NUMBER_OF_UTTERANCES> with the desired number of utterances to generate.
The generated utterances will be saved in the grammars/outputs directory.

### File Examples
#### CASE A. 
<FOLDER-NAME>/grams/<FOLDER-NAME>_data_gen_config.json
	``` JSON
	{
	  "DATA_GLOBAL_GEN": [
	    "gallery_global"
	  ],
	  "DATA": {
	    "$list": "grammars/gallery/slot_dictionaries/",
	    "GRAM": "grammars/gallery/grams/",
	    "SPEC": "",
	    "OUTPUT": "grammars/output/",
	    "$common_dir": "grammars/common/slot_dictionaries/"
	  },
	  "NONTERMINAL": {
	    "$LOCATION": {
	      "TYPE": "tag",
	      "TAG": "_CITIES",
	      "LIST": "$list/location.txt"
	    },
	    "$LASTNAME": {
	      "TYPE": "list",
	      "TAG": "",
	      "LIST": "$list/lastname.txt"
	    },
	    "$MOVIE": {
	      "TYPE": "list",
	      "TAG": "",
	      "LIST": "$list/movie.txt"
	    },
	    "$APP": {
	      "TYPE": "list",
	      "TAG": "_APP",
	      "LIST": "$common_dir/app.txt"
	    }
	  },
	  "DATA_GEN": [
	    ["gallery_1", 0.3],
	    ["gallery_2", 1],
	    ["gallery_3", 0.7],
	    ["gallery_4", 1],
	    ["gallery_5", 1]
	  ]
	}
	```

<FOLDER-NAME>/grams/<FOLDER-NAME>_global.gram
	```
	grammar gallery_global;
	<Location@SearchViewResult> = $LOCATION;
	<gal_edit_v> = edit|adjust|alter|change|modify|enhance|manipulate;
	<gal_picture_n> = image|photo|photograph|picture|selfie|shot|snap|snapshot;
	<gal_launch> = launch|open|start|boot up|go to|load|load up|open up|run|start up|activate|use;
	<gal_gallery_n> = gallery|photo gallery|picture gallery|camera roll;
	```
 
<FOLDER-NAME>/grams/<FOLDER-NAME>_<NUMBER>.gram
	```
	grammar gallery_2;
	public <gallery> = <Gallery_114>;
	<Gallery_114> = <SearchView> | <SearchViewResult>;
	<SearchView> = (<gal_edit_v> [the] <gal_picture_n>);
	<SearchViewResult> = (<gal_edit_v> <Location@SearchViewResult> <gal_picture_n>) ;
	#<Location@SearchViewResult> is expanded through mapping in *global.gram => *config.json => slot_dictionaries/Location.txt
	```

Another example:
	```
	grammar gallery_4;
	public <gallery> = <gallery_4>;
	<gallery_4> = <gallery_4_a>|<gallery_4_b>;
	<gallery_4_a> = Show photos taken by <lastname>;
	<gallery_4_b> =  <gal_picture_n> with <lastname>;
	<lastname> = $LASTNAME;
	```

<FOLDER-NAME>/slot_dictionary/<ALIAS-NAME>.txt
	```
	Smith
	Kowalski
	Garcia
	```

outputs/<FOLDER-NAME>_<NUMBER>.expand
	```
	gallery_2	enhance shot	o o
	gallery_2	enhance picture	o o
	gallery_2	alter firenze snapshot	o b-_CITIES o
	gallery_2	adjust hawaii snapshot	o b-_CITIES o
	gallery_2	edit hawaii snapshot	o b-_CITIES o
	gallery_2	change hawaii snap	o b-_CITIES o
	gallery_2	alter picture	o o
	gallery_2	adjust photo	o o
	gallery_2	change firenze shot	o b-_CITIES o
	gallery_2	modify picture   
		o o
	
	```
