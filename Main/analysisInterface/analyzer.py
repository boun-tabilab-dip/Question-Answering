
# -*- coding: utf-8 -*-

import sys

analDir = '../SyntacticAnalyzer/';

sys.path.append(analDir + 'fm-distiller')
sys.path.append(analDir + 'dataBackup')
sys.path.append(analDir + 'visualizer')
sys.path.append(analDir + 'glasses')
sys.path.append(analDir + 'classBags')

sys.path.append('parserInterface')

import qVisualizer
from question import Question, QPart
from distiller import Distiller
from hmmLearner import *
from hmmGlasses import *

from hybridClassifier import coarseFinder

import codecs;

class QuestionAnalysis:
    question = None;

    def __init__(self, question = None):
        self.question = question;

    def visualizeQuestion(self):
        qVisualizer.produceVisualPage(self.question.questionParts)

    @staticmethod
    def visualizeAll(questions):
        qVisualizer.visualizeAllQuestions(questions)
        
    @staticmethod
    def combineGlasses(glassResult1, glassResult2):
        result = []
        for i in range(0, len(glassResult1)):
            fmnConfPart1 = glassResult1[i]
            fmnConfPart2 = glassResult2[i]

            if fmnConfPart1[0] ==  fmnConfPart2[0]:
                if fmnConfPart1[1] >= fmnConfPart2[1]:
                    result.append(fmnConfPart1)
                else:
                    result.append(fmnConfPart2)
            else:
                if fmnConfPart1[0] == 'FOC':
                    result.append(fmnConfPart1)
                elif fmnConfPart2[0] == 'FOC':
                    result.append(fmnConfPart2)
                else:
                    if fmnConfPart1[1] >= fmnConfPart2[1]:
                        result.append(fmnConfPart1)
                    else:
                        result.append(fmnConfPart2)

        return result


    @staticmethod
    def baselineFocusExtract(question, proximity=1):
        includeQstnWords = ['hangi ', 
                            'kaç ', 
                            'Kaç ',
                            ' kim ',
                            'kimin ',
                            'ne zaman',
                            'nereye',
                            'nereden',
                            'nerede ',
                            'yüzde kaç', 
                            'ne denir',
                            'kaçtır',
                            'neresidir']
                            
        excludeQstnWords = ['nedir',
                            'hangisidir',
                            'hangileridir',
                            'verilir',
                            'ne kadardır',
                            'nerelerdir',
                            'neye']

        unknownQstnWord = ['ne zamandır', 'ne zamandan', 'nerededir']

        qstnWords = question.questionText.split(' ')

        focusParts = []
        
        #print(question.questionText)


        """
        CAUTION: TERRIBLE CODING

        DESPARATELY NEEDS A REFEACTOR
        """

        for qstnWord in unknownQstnWord:
            if qstnWord.decode('utf-8') in question.questionText:
                return []

        for inQword in includeQstnWords:
            if inQword.decode('utf-8') in question.questionText:
                qWordParts = inQword.split(' ')
                if qWordParts[0] == '':
                    qWordParts = qWordParts[1:len(qWordParts)]
                # space cleaning
                if len(qWordParts) >= 2 and qWordParts[len(qWordParts)-1] == '':
                    qWordParts = qWordParts[0:len(qWordParts)-1]

                if qWordParts[0].decode('utf-8') == 'yüzde'.decode('utf-8'):
                    yIndex = qstnWords.index('yüzde'.decode('utf-8'))
                    if yIndex-proximity < 0:
                        focusParts.extend([qstnWords[yIndex-1], qstnWords[yIndex], qstnWords[yIndex+1]])
                    else:
                        proximityWords = []
                        for i in range(yIndex-proximity, yIndex):
                            proximityWords.append(qstnWords[i])

                        focusParts.extend(proximityWords)
                        focusParts.extend([qstnWords[yIndex], qstnWords[yIndex+1]])
                    break
                elif (len(qWordParts) > 1) and qWordParts[1] == 'denir':
                    nIndex = qstnWords.index('ne')
                    if nIndex-proximity < 0:
                        focusParts.extend([qstnWords[nIndex-1], qstnWords[nIndex+1]])
                    else:
                        proximityWords = []
                        for i in range(nIndex-proximity, nIndex):
                            proximityWords.append(qstnWords[i])

                        focusParts.extend(proximityWords)
                        focusParts.extend([qstnWords[nIndex+1]]) 
                    break
                elif qWordParts[0].decode('utf-8') == 'kaçtır'.decode('utf-8'):
                    kIndex = qstnWords.index('kaçtır'.decode('utf-8'))

                    if kIndex-proximity < 0:
                        focusParts.extend([qstnWords[kIndex-1], qstnWords[kIndex+1]])
                    else:
                        proximityWords = []
                        for i in range(kIndex-proximity, kIndex):
                            proximityWords.append(qstnWords[i])

                        focusParts.extend(proximityWords)
                        focusParts.extend([qWordParts[0]])

                    break
                elif qWordParts[0].decode('utf-8') == 'neresidir'.decode('utf-8'):
                    kIndex = qstnWords.index('neresidir'.decode('utf-8'))

                    if kIndex-proximity < 0:
                        focusParts.extend([qstnWords[kIndex-1], qstnWords[kIndex+1]])
                    else:
                        proximityWords = []
                        for i in range(kIndex-proximity, kIndex):
                            proximityWords.append(qstnWords[i])

                        focusParts.extend(proximityWords)
                        focusParts.extend([qWordParts[0]])
                    break
                else:
                    element = qWordParts[len(qWordParts)-1].decode('utf-8')
                    eIndex = qstnWords.index(element)
                    if eIndex + proximity >= len(qstnWords):
                        focusParts = qWordParts + [qstnWords[eIndex+1]]
                    else:
                        proximityWords = []
                        for i in range(1,proximity+1):
                            proximityWords.append(qstnWords[eIndex+i])

                        focusParts = qWordParts + proximityWords
                    break
                    
            return focusParts
            

        for outQword in excludeQstnWords:
            if outQword.decode('utf-8') in question.questionText:
                qWordParts = outQword.split(' ')
                # space cleaning
                if len(qWordParts) >= 2 and qWordParts[len(qWordParts)-1] == '':
                    qWordParts = qWordParts[0:len(qWordParts)-1]
                

                if qWordParts[0] == 'neye':
                    nIndex = qstnWords.index('neye')

                    if nIndex + proximity >= len(qstnWords):
                        focusParts = qWordParts + [qstnWords[nIndex+1]]
                    else:
                        proximityWords = []
                        for i in range(1,proximity+1):
                            proximityWords.append(qstnWords[nIndex+i])

                        focusParts = qWordParts + proximityWords
                    break
                else:
                    element = qWordParts[0].encode('utf-8')
                    eIndex = qstnWords.index(element.encode('utf-8'))

                    if eIndex-proximity < 0:
                        focusParts = [qstnWords[eIndex-1]]
                    else:
                        proximityWords = []
                        for i in range(eIndex-proximity, eIndex):
                            proximityWords.append(qstnWords[i])

                        focusParts.extend(proximityWords)

                    break

        return focusParts


    def combineDistillerGlasses(self, ruleFocus, fRuleConf, hmmResults):

        """ Combining Focus Parts of both distiller and hmm-glasses"""
        focusCombined = []
        focusConfidences = []
        # note : order in serialization doesn't matter at this point
        for part in serializeDepTree(self.question.questionParts):
            # checking first what does hmm-glasses thinks about this part
            inHmmFoc = False
            for hmmRes in hmmResults:
                if part == hmmRes[2] and hmmRes[0] == 'FOC':
                    inHmmFoc = hmmRes
                    break

            if part in ruleFocus:
                if inHmmFoc: # both distiller and hmm thinks it should be focus
                    focusCombined.append(part)
                    focusConfidences.append(max(fRuleConf, inHmmFoc[1]))
                else: # hmm doesn't think it's a focus, but distiller does
                    focusCombined.append(part)
                    focusConfidences.append(fRuleConf)

            elif inHmmFoc: 
                # hmm-glasses thinks this part is focus, 
                # but distiller doesn't agree
                
                # in hmm-glasses we trust!
                focusCombined.append(part)
                focusConfidences.append(inHmmFoc[1])
            # we don't do anything for the part for which both distiller and hmm-glasses think that it doesn't belong to focus
                
        focusCombined.reverse()
        focusConfidences.reverse()

        return focusCombined, focusConfidences
        

    def extractFocusMod(self, reverseGlass, normalGlass, onlyDistiller=False, onlyForward=False, genericEnable=True, whichDistEnable=False):
        dist = Distiller(self.question, genericEnable)

        ruleFocus, ruleMod, fRuleConf, mRuleConf, whichDist = dist.FM_Distiller()
        #print(ruleFocus)
        if onlyDistiller:
            focusCombined = ruleFocus
            focusConfidences = fRuleConf # <= TODO: focusCondidences is supposed to be a list of number, not a number
            hmmResults = []
        else:
            if onlyForward:
                hmmResults = normalGlass.computeFocusProbs(self.question)
            else:
                mostProbRevSeq = reverseGlass.computeFocusProbs(self.question)
                mostProbSeq = normalGlass.computeFocusProbs(self.question)

                hmmResults = QuestionAnalysis.combineGlasses(mostProbRevSeq, mostProbSeq)
            # Combining distiller and hmm results
            focusCombined, focusConfidences = self.combineDistillerGlasses(ruleFocus, fRuleConf, hmmResults)
    

        #self.question.focus = focusCombined
        self.question.setFocusParts(focusCombined)
        self.question.focusConfidence = focusConfidences

        self.question.mod = ruleMod # out of question at this point
        self.question.focusConfidence = mRuleConf # out of question at this point

        if whichDistEnable:
            return ruleFocus, hmmResults, focusCombined, focusConfidences, whichDist
        else:
            return ruleFocus, hmmResults, focusCombined, focusConfidences

    def showFocusMod(self, reverseGlass, normalGlass, onlyDistiller=False):
        ruleFocus, hmmResults, focusCombined, focusConfidences = self.extractFocusMod(reverseGlass, normalGlass, onlyDistiller)

        focusText, modText = self.question.extract_FM_Text()

        print('Focus : ' + focusText)
        print('QText : ' + self.question.questionText)
        
        #print(u"Q: {} || Focus: {} || ActualClass: {} || Answer: {}".format(self.question.questionText, focusText, self.question.coarseClass + " - " + self.question.fineClass, self.question.answer))

    def pnounAnalysis(self):
        parts = self.question.questionParts

        pnouns = []

        for part in parts:
            if QPart.getPartField(part, 'POStag') == 'Noun' and QPart.getPartField(part, 'POSDetail') == 'Prop':
                pnouns.append(part)

        self.question.pnouns = pnouns
        return pnouns

    """
    Grabs all MODIFIERS that are connected to ANY ONE of the focus parts, along with their CLASSIFIERS
    """
    def modAnalysis(self):
        mods = []

        #find MODIFIERS that are connected to any ONE of the focus parts
        fParts = self.question.focus
        parts = self.question.questionParts

        for part in parts:
            if QPart.getPartField(part, 'depenTag') == 'MODIFIER':
                rootOfPart = QPart.getPartField(part, 'rootID')
                # is this rootID matches with any depenID of any focus?
                for fPart in fParts:
                    if rootOfPart == QPart.getPartField(fPart, 'depenID'):
                        # we add this modifier along with its modifier/classifier children
                        tmp = [part]
                        
                        tmp.extend(self.question.traceFromFoldTamlama('back', part, includePOSS=False, includeCLASS=True, includeMODIF=True, includeSEN=False, includeOBJ=False))

                        tmp = [p for p in tmp if QPart.getPartField(p, 'depenTag') != 'DERIV' and (QPart.getPartField(p, 'text') not in self.question.exclusionWords)]
                        tmp.reverse()
                        mods.append(tmp)

        #mods.reverse()
        self.question.mod = mods
        return self.question.mod
        
    # extracts the subject with its classifiers
    def subjectAnalysis(self):
        parts = self.question.questionParts

        # find the subject (BUG ALERT: what if multiple subjects are there?)
        SUBJlist = QPart.getAllPartsWithField(parts, 'depenTag', 'SUBJECT')

        if SUBJlist == []:
            SUBJ = False
        else:
            SUBJ = SUBJlist[len(SUBJlist)-1]

        if not SUBJ: # no subjects in the question
            wholeSubject = []
        else:
            wholeSubject = [SUBJ]

            # now we find the classifier children of subject
        
            wholeSubject.extend(self.question.findChildrenDepenTag(SUBJ, 'CLASSIFIER'))
            wholeSubject.extend(self.question.findChildrenDepenTag(SUBJ, 'MODIFIER'))

        self.question.subject = wholeSubject # list of parts
        return wholeSubject


    def fullAnalysis(self, reverseGlass, normalGlass, onlyDistiller=False):
        ruleFocus, hmmResults, focusCombined, focusConfidences = self.extractFocusMod(reverseGlass, normalGlass, onlyDistiller)

        self.modAnalysis() # this overrides all of the mod analyses before, so it should always kept before the next line

        focusText, modText = self.question.extract_FM_Text()
        focusMorph, modMorph = self.question.extract_FM_Text(morphORtext='morphRoot')

        qClass = coarseFinder(self.question)

        self.pnounAnalysis()

        qPnounText = self.question.extract_Prop_Noun_Text()

        self.subjectAnalysis()

        subjects = self.question.extractSubjectText()
        #print(".")
        """
        print("Full Analysis\n\n")
        print("Subject: " + subjects)
        print("Focus: " + focusText)
        print("Focus Roots: " + focusMorph)
        print("Mod: " + modText)
        print("Class: " + qClass)
        print("Proper Nouns: " + qPnounText)
        """
        return focusText.strip(), focusMorph.strip(), modText.strip(), qClass, qPnounText.strip(), subjects.strip()
