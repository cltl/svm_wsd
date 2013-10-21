#!/usr/bin/env python

############################################################
# Author:   Ruben Izquierdo Bevia ruben.izquierdobevia@vu.nl       
# Version:  1.0
# Date:     16 Sep 2013
#############################################################



import sys
import codecs
import os
import subprocess
import getopt
from collections import defaultdict
from operator import itemgetter
from xml.etree.ElementTree import ElementTree, Element


## Code for seting the paths for the local installation of 

#Code for importing svmutil
this_folder = os.path.dirname(__file__)
libsvmfolder = os.path.join(this_folder,'lib','libsvm','python')
sys.path.append(libsvmfolder)
from svmutil import *
###########################



TREETAGGER=os.path.join(this_folder,'lib','treetagger')
POS_NOUN = 'n'
POS_VERB = 'v'
POS_ADJ = 'a'
MODELS_FOLDER = os.path.join(this_folder,'models')
NAF_INPUT = 'naf'


def loadDictionary(filename):
    dictionary = {}
    fic = codecs.open(filename,'r','utf-8')
    for line in fic:
      fields = line.strip().split()
      lemma = fields[0]
      pos = fields[1]
      dictionary[(lemma,pos)]=set(fields[2:])
    fic.close()
    return dictionary 

def is_noun(pos,type_input):
    if type_input == NAF_INPUT:
        return pos in ['N','R']
    else:
        return pos.startswith('noun')

def is_verb(pos,type_input):
     if type_input == NAF_INPUT:
         return pos in ['V']
     else:
         return pos.startswith('verb')

def is_adj(pos,type_input):
    if type_input == NAF_INPUT:
        return pos in ['G']
    else:
        return pos.startswith('adj')

#Input is unicode text
def treetagger(text):
    tokens = []     # List of token,pos,lemma,num_sent
    global TREETAGGER
    treetagger_cmd = TREETAGGER+'/cmd/tree-tagger-dutch-utf8'
    tt_proc = subprocess.Popen(treetagger_cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    tt_out, tt_err = tt_proc.communicate(text.encode('utf-8'))
    #print>>sys.stderr,'Output error TreeTagger:',tt_err
    num_sent = 1
    num_token = 0
    for line in tt_out.splitlines():
        
        fields = line.decode('utf-8').split('\t')
        if len(fields) != 3:
            print>>sys.stderr,'Error parsing',line
        else:
            token_id = 'w'+str(num_token)
            token,pos,lemma = fields
            if lemma == '<unknown>': 
                lemma = token.lower()
            elif '|' in lemma:
                lemma = lemma.split('|')[0] #parse cases like wezen|zijn
                
            tokens.append((token_id,token,pos,lemma,num_sent))
            if pos == '$.': num_sent += 1
            num_token += 1
    return tokens
    
    
def createTestTokens(tokens):
    test_tokens = []
    n = 0 
    for wordid, sense, lemma, pos in self.testset:
      if (lemma,pos) in self.dictionary:
          possibleClasses = self.dictionary[(lemma,pos)]
          self.testClasses |= possibleClasses
          token = TestToken(wordid,lemma,pos,possibleClasses)
          self.testTokens.append(token)
          n+=1
    
    
def extract_features(idx,list_tokens):
    features = defaultdict(int)
    ctx_size = 20
    for current_relative_idx in range(-ctx_size, ctx_size):
        absolute_idx = idx + current_relative_idx
        if not (absolute_idx < 0 or absolute_idx >= len(list_tokens)):
            token_id, token, pos, lemma, num_sentence = list_tokens[absolute_idx]
            
            #wordforms
            feature = token+'#W_'+str(current_relative_idx)
            features[feature]+=1
            
            feature = token+'#W_BOW'
            features[feature]+=1
            
            
            #lemmas
            feature = lemma+'#L_'+str(current_relative_idx)
            features[feature]+=1
            
            feature = lemma+'#L_BOW'
            features[feature]+=1
    return features

def loadIndexFeatures(filename):
    idx = {}
  
    fic = codecs.open(filename,'r','utf-8')
    for n, line in enumerate(fic):
      fields = line.strip().split(' ')  ##FEATURE FREQ
      feat = fields[0]
      freq = float(fields[1])
      idx[feat] = (n,freq)
    fic.close()
    return idx
    
    
def resolve_list(senses_values):
    sorted_list = sorted(senses_values,key=itemgetter(1),reverse=True)
    return sorted_list[0]


def generate_xml_semcor(tokens,final_results):
    my_xml = Element('text')   ## Root
    my_xml.tail = my_xml.text = '\n'
    previous_sent = None
    sent_ele = None
                
    
    for token_id, token, pos, lemma, num_sentence in tokens:
        guess = final_results.get(token_id)
        
        if previous_sent is None:
            sent_ele = Element('sent',{'sent_num':str(num_sentence)})
        elif num_sentence != previous_sent:
            sent_ele.tail = sent_ele.text ='\n'
            my_xml.append(sent_ele)
            sent_ele = Element('sent',{'s_num':str(num_sentence)})
            
        wf_ele = Element('wf',{'id':token_id,'lemma':lemma, 'pos':pos})
        wf_ele.text = token
        if guess is not None: 
            wf_ele.set('sense_label',str(guess[0]))
            wf_ele.set('sense_confidence',str(round(guess[1],4)))
        wf_ele.tail = '\n'
        previous_sent = num_sentence
        sent_ele.append(wf_ele)
        
    sent_ele.tail = sent_ele.text = '\n'
    my_xml.append(sent_ele) ## append the last one
    my_tree = ElementTree(element=my_xml)
    my_tree.write(sys.stdout, encoding="UTF8")


if __name__ == '__main__':
    if sys.stdin.isatty():
        print>>sys.stderr,'Error. Usage:'
        print>>sys.stderr,'\tcat file | ',sys.argv[0],' --naf (optional: input is NAF, also output)'
        print>>sys.stderr,'\techo "This is my text" |',sys.argv[0]
        sys.exit(-1)
        
    type_input = 'plain'
    try:
        opts, args = getopt.getopt(sys.argv[1:],'',['naf'])
        for opt,value in opts:
            if opt == '--naf':
                type_input = NAF_INPUT
    except getopt.GetoptError, e:
        print>>sys.stderr,'Warning!!!',str(e)+'. Ignored'
        
    print>>sys.stderr,'Type of input/output:',type_input
            
    dictionary = loadDictionary(os.path.join(MODELS_FOLDER,'dictionary'))
    tokens = []
    if type_input==NAF_INPUT:
        
        from NafParserPy import NafParser
        naf_obj = NafParser(sys.stdin)
        lemma_pos_for_tokid = {}
        for term in naf_obj.get_terms():
            lemma = term.get_lemma()
            pos = term.get_pos()
            for tokid in term.get_span():
                lemma_pos_for_tokid[tokid] = (lemma,pos)
        
        for token in naf_obj.get_tokens():
            tokenid = token.get_id()
            tokval = token.get_text()
            sent = token.get_sent()
            lemma,pos = lemma_pos_for_tokid[tokenid]
            tokens.append((tokenid,tokval,pos,lemma,sent))
    else:
        input_text = sys.stdin.read().decode('utf-8','ignore')
        tokens = treetagger(input_text)     # List of (token_id, token,pos,lemma,num_sent)
    
    
    ## Extracting features for each token
    features_for_tokenid = {}
    for idx in xrange(len(tokens)):
        token_id = tokens[idx][0]
        features = extract_features(idx,tokens)
        features_for_tokenid[token_id] = features
    ##############################
    
    senses_for_tokenid = {}
    pos_for_sense = {}
    ##Extract possible senses for each token
    all_senses = set()
    for token_id, _, pos, lemma, _ in tokens:
        possible_senses = None
        if is_noun(pos,type_input): possible_senses = dictionary.get((lemma,POS_NOUN),None)
        elif is_verb(pos,type_input): possible_senses = dictionary.get((lemma,POS_VERB),None)
        elif is_adj(pos,type_input): possible_senses = dictionary.get((lemma,POS_ADJ),None)

                    
        if possible_senses is not None:
            for sense in possible_senses:  pos_for_sense[sense] = pos
            senses_for_tokenid[token_id] = possible_senses
            all_senses = all_senses | possible_senses
    #########################################
    
    ## Tag using each classifier
    results_for_tokenid = defaultdict(list)
    for sense in all_senses:
        my_pos = pos_for_sense[sense]
        if is_noun(my_pos,type_input): pos_folder = 'nouns'
        elif is_verb(my_pos,type_input): pos_folder = 'verbs'
        elif is_adj(my_pos,type_input): pos_folder = 'adjs'
        
        featurefile = os.path.join(MODELS_FOLDER,pos_folder,sense+'.filterFeatures')
        modelfile =   os.path.join(MODELS_FOLDER,pos_folder,sense+'.model')
        
        if os.path.exists(featurefile) and os.path.exists(modelfile):
            ## LOAD IDX OF FEATURES
            idxForFeatures = loadIndexFeatures(featurefile)
            
            ## LOAD SVM MODEL
            model = svm_load_model(modelfile.encode('utf-8'))            
            
            for token_id, token, pos, lemma, num_sentence in tokens:
                possible_senses = senses_for_tokenid.get(token_id)
                if possible_senses is not None and sense in possible_senses:
                    encodedFeatures = {}
                    for feat, freq in features_for_tokenid[token_id].items():
                        indexFeature, value = idxForFeatures.get(feat,(-1,-1))
                        if indexFeature!=-1:
                            encodedFeatures[int(indexFeature)]=value
                    #print encodedFeatures
                    predicted_label,_,predicted_values = svm_predict([0],[encodedFeatures],model,"-b 1 -q")
                    probability_for_positive = predicted_values[0][0]
                    results_for_tokenid[token_id].append((sense,probability_for_positive))
    ######
    # Resolve and assign the most possible
    final_results = {}
    for token_id, _, _, _, _ in tokens:
        r = results_for_tokenid.get(token_id,None)
        if r is not None:
            best_sense_and_probability = resolve_list(r)
            final_results[token_id] = best_sense_and_probability
    #############
      
    generate_xml_semcor(tokens,final_results)

    sys.exit(0)