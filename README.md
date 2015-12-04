svm_dsc
======

- Project: DutchSemCor
- Project number: 380-70-011
- Funded by the Dutch National Science Foundation (NWO).
- website: http://www2.let.vu.nl/oz/cltl/dutchsemcor/index.html
- Start date: September, 2009
- End date: August, 2012
- Software: svm_wsd
- Version: 1.0
- Author: Ruben Izquierdo, VU University of Amsterdam
- Email: ruben.izquierdobevia@vu.nl


File listing:
------------
- dsc_wsd_tagger.py: main script for tagging an input plain text
- install.sh: script for installing libraries and dependencies
- COPYING-GPL.TXT
- LICENSESOFTWARE.TXT
- README.TXT
  

LICENSE:
-------
This work is licensed under a Creative Commons Attribution 3.0 Unported License: http://creativecommons.org/licenses/by/3.0/legalcode
href="http://creativecommons.org/licenses/by/3.0/deed.en_US". See the file LICENSEDATA.TXT and COPYING-CC.TXT that should be in the
top-directory of this distribution.


Description and installation
----------------------------

This program svm_wsd implements a machine learning Word Sense Disambiguation system based on Support Vector
Machines. We use a bag-of-words model for representing the features. It has been implemented in python, so a valid installation of python is required, at least version 2.6. There are also
some dependencies that will be automatically downloaded and installed by the script install.sh
- libsvm: library implementing a SVM engine (https://github.com/cjlin1/libsvm)
- treetagger: part-of-speech and lemmatizer (http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger)
OR
- NafParserPy: parser of NAF files in python (https://github.com/cltl/NafParserPy)
- models_DSC: models trained on the DutchSemCor project for WSD

To install this program you have to follow 2 steps:
- 1) Download/clone this repository
- 2) Go to the folder and run the install.sh script, which will install libsvm, treetagger and the models for WSD.
or
- 2) Go to the folder and run the install_naf.sh script to work with NAF files (not treetagger)

In summary:

````shell
$ git clone git@github.com:cltl/svm_wsd.git
$ cd svm_wsd
$ . install.sh OR . install_naf.sh

````

Usage
-----

The input for the program has to be valid UTF-8 plain text. The script dsc_wsd_tagger.py will read the text from the standard
input. So there are 2 easy ways to call the program:

For working with plain files and call treetagger for lemma and pos tagging:

````shell
$ echo 'Dit is een input text' | dsc_wsd_tagger.py
$ cat my_input_file.txt | dsc_wsd_tagger.py
````

The output will be an XML file with a structure similar to the one used by the SemCor corpus:

````shell
<text>
  <sent s_num="sentence number">
    <wf id="identifier" lemma="lemma" pos="part-of-speech' sense_confidence="value" sense_label="lexical-unit-label">token</wf>
    <wf...>
    ...
  </sent>
  <sent...
  ...
</text>
````

The attributes sense_confidence and sense_label are only present when the token is disambiguated.

For working with NAF files:
````shell
$ cat input.naf | dsc_wsd_tagger.py --naf -ref odwnSY> output.naf
````
The parameter `ref` represents what type of reference we want to have in the output:

* corLU: for cornetto lexical unit ids
* odwnLU: OpenDutchWordNet lexical unit ids
* odwnSY: OpenDutchWordNet synset ids.

The output is the NAF extended with the senses and confidences, represented as external references on the term--> externalReferences element. 
The ranking of all the senses with the returned confidence value according to SVM are included on the output.

Contact
------

* Ruben Izquierdo Bevia
* ruben.izquierdobevia@vu.nl
* http://rubenizquierdobevia.com/
* Vrije University of Amsterdam

