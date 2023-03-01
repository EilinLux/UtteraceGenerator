## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Files Examples](#Files-examples)

## General info
This project aims to automatize the process of utterance generation. This is generally considered a best practise in Natural Language Processing (NLP), since it better consistency and wider coverage of sample utterances improve the natural language understanding. 

Additional reasons to use the present code are that
* it is faster to define a grammar rather than to write down one by one the possible variations
* it eliminates duplicates
* it reuse lists and utterance collections across the modules by writing files in ```\grammars\common\slot_dictionaries```
	
## Technologies
Project is written in Python (3.8) and uses the following libraries:
* sys
* argparse
* codecs
* time
* json
* os
* shutil
* re
* traceback
* ranodm
	
## Setup
To run this project, install it locally:
1. create folder ```<FOLDER-NAME>``` in ```grammars``` folder
2. inside ```<FOLDER-NAME>```create a ```gram``` folder and a ```slot_dictionary```
3. in ```gram``` folder, write a  ```<FOLDER-NAME>_data_gen_config.json``` file
4. in ```gram``` folder, write one or more ```.gram``` file(s) (a global one and one or more specific ones )
5. in ```slot_dictionary```, write one or more ```.expand``` file(s) 

to generate use the following command
```
python gram_gen.py -c grammars/<FOLDER-NAME>/grams/<FOLDER-NAME>_data_gen_config.json -n <NUMBER-OF-UTTERANCE-TO-BE-GENERATED>
```

the outputs are at ```grammars/outputs```


NB: for reating concept in config json:
python add_concept.py -c grammars/gallery/grams/Gallery_data_gen_config.json -k MOVIE -l movie.txt

## Files Examples 
##### <FOLDER-NAME>/grams/<FOLDER-NAME>_data_gen_config.json 

```
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
        ["gallery_2",1],
        ["gallery_3",0.7],
        ["gallery_4",1],
        ["gallery_5",1]
    ]
}
```

##### <FOLDER-NAME>/grams/<FOLDER-NAME>_global.gram

```
grammar gallery_global;

<Location@SearchViewResult> = $LOCATION;
<gal_edit_v> = edit|adjust|alter|change|modify|enhance|manipulate;
<gal_picture_n> = image|photo|photograph|picture|selfie|shot|snap|snapshot;

<gal_launch> = launch|open|start|boot up|go to|load|load up|open up|run|start up|activate|use;

<gal_gallery_n> = gallery|photo gallery|picture gallery|camera roll;
```
##### <FOLDER-NAME>/grams/<FOLDER-NAME>_<NUMBER>.gram

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
##### <FOLDER-NAME>/slot_dictionary/<ALIAS-NAME>.txt

```
Smith
Kowalski
Garcia
```

##### outputs/<FOLDER-NAME>_<NUMBER>.expand

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
gallery_2	modify picture	o o
```



