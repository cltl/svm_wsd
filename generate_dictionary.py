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

def generate_dictionary(path_to_cornetto, map_cornettoluid_odwnluid, map_odwnLU_to_odwnSY):
    #Load mapping from cornetto_lu to odwn_lu
    f = open(map_cornettoluid_odwnluid,'r')
    cornetto_lu_to_odwn_lu = {}
    for line in f:
        fields = line.strip().split()
        cornetto_lu_to_odwn_lu[fields[0]] = fields[1]
    f.close()
    #########
    
    #Load map odwn LU to odwn SY
    odwn_lu_to_odwn_synset = {}
    f = open(map_odwnLU_to_odwnSY)
    for line in f:
        fields = line.strip().split()
        odwn_lu_to_odwn_synset[fields[0]] = fields[1]
    f.close()
    
    
    
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
    print '###lemma pos cornettoLU1 odwnLU1 odwnSYNSET1 [cornettoLU2 odwnLU2 odwnSYNSET2] [... ... ...]'
    for (lemma,short_pos), luids in luids_for_lemma_pos.items():
        print lemma.encode('utf-8')+' '+short_pos.encode('utf-8'),
        for cornettoLU in set(luids):
            #1 Map to odwn LU
            odwnLU = None
            if cornettoLU[0] in ['r','c']:
                odwnLU = cornettoLU
            elif cornettoLU[0] == 'd':
                odwnLU = cornetto_lu_to_odwn_lu.get(cornettoLU)
            else:
                #Ignore the rest
                odwnLU = None
            
            # 2 map go odwn Synset
            odwnSY = None
            if odwnLU is not None:
                odwnSY = odwn_lu_to_odwn_synset.get(odwnLU)
            print cornettoLU+' '+str(odwnLU)+' '+str(odwnSY),
        print
            
        
        
if __name__ == '__main__':
    path_to_cornetto_kyoto = '/home/izquierdo/wordnets/cornetto2.1_lmf/cornetto2.1.lmf.xml'
    map_cornettoluid_odwnluid = '/home/izquierdo/wordnets/cornetto2.1_lmf/mapping_cornettoLU_2_odwnLU'
    map_odwnLU_to_odwnSY = '/home/izquierdo/wordnets/cornetto2.1_lmf/mapping_odwnLU_2_odwnSY'
    path_to_cornetto = path_to_cornetto_kyoto
    generate_dictionary(path_to_cornetto, map_cornettoluid_odwnluid, map_odwnLU_to_odwnSY) 