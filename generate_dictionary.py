#!/usr/bin/env python

'''
Generates a dictionary for lemmas from Cornetto, with the format:
lemma POS luid1 luid2...
'''

import sys
from lxml import etree

def normalise_pos(long_pos):
    pos = long_pos
    if long_pos == 'adjective':
        pos = 'a'
    elif long_pos == 'adverb':
        pos = 'r'
    elif long_pos == 'noun':
        pos = 'n'
    elif long_pos == 'other':
        pos = 'other'
    elif long_pos == 'verb':
        pos = 'v'
    return pos

def generate_dictionary(path_to_cornetto):
    luids_for_lemma_pos = {}
    tree = etree.parse(path_to_cornetto,etree.XMLParser(remove_blank_text=1))
    for lex_entry in tree.findall('Lexicon/LexicalEntry'):
        long_pos = lex_entry.get('partOfSpeech')
        short_pos = normalise_pos(long_pos)
        lemma_obj = lex_entry.find('Lemma')
        if lemma_obj is not None:
            
            lemma = lemma_obj.get('writtenForm')
       
            sense = lex_entry.find('Sense').get('senseId')
        
            if (lemma,short_pos) not in luids_for_lemma_pos:
                luids_for_lemma_pos[(lemma,short_pos)] = [sense]
            else:
                luids_for_lemma_pos[(lemma,short_pos)].append(sense)
    
    print>>sys.stderr,len(luids_for_lemma_pos)
    for (lemma,short_pos), luids in luids_for_lemma_pos.items():
        print lemma.encode('utf-8')+' '+short_pos.encode('utf-8')+' '+' '.join(luids)
        
        
if __name__ == '__main__':
    path_to_cornetto_kyoto = '/home/izquierdo/wordnets/cornetto2.1_lmf/cornetto2.1.lmf.xml'
    path_to_cornetto = path_to_cornetto_kyoto
    generate_dictionary(path_to_cornetto) 