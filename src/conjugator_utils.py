""""
Conjugation Utilites

Provides functions to ease in finding a verb's
proper Verb class.
"""

import re
import src.verbs as v
import src.verb_utils as vutils
from enum import IntEnum

# TO DO:

# DONE1. add better doc strings, even if just the one-liner ones
# DONE2. make the 'indexing constants' be an int-enum class
# DONE3. make elif trees for simple assignments be done with maps instead (not sure about verb class disambiguations...)
# DONE4. remove the regex strings (already defined in vutils)
# 5. tests:
#	DONE1. check that the irregular verbs get the right classes
# 	2. check that regular verbs get the right classes
#	3. check that ambiguous matches get the right classes
#	4. add verb tests/attribute for a prefix portion
#		(stems and such now be determined via the root) (the negation rule for the future still applies)
#		(now just appending a prefix string to corresponding stem!)
# 6. ADD TYPE HINTS

class IrregularIdx(IntEnum):
	RGX_INFINITIVE = 0
	CONJUGATION_CLASS = 1
	PRESENT_STEM = 2
	PAST_STEM = 3
	IMPERATIVE_STEM = 4
	#PASSIVE_STEM = 5
	#TRANSGRESSIVE_STEM = 6

# dictionaries
int_to_verb_class= { 1 : v.Class1, 2 : v.Class2, 3: v.Class3, 4: v.Class4 }

def get_irregular_verbs() -> list:
	"""
	Retrieve the irregular verb constructions from the file and store them as a list of tuples.
	
	Each line becomes its own tuple, with each element within each tuple being the following:
	0 (IrregularIdx.RGX_INFINITIVE): The irregular verb's infinitive
	1 (IrregularIdx.CONJUGATION_CLASS): The irregular verb's conjugation class (determines which literal Verb class to construct).
	2 (IrregularIdx.PRESENT_STEM): The irregular verb's present stem for present tense conjugations.
	3 (IrregularIdx.PAST_STEM): The irregular verb's past participle stem for past tense and conditional mood conjugations.
	4 (IrregularIdx.IMPERATIVE_STEM): The irregular verb's imperative stem for imperative mood conjugations.

	Return:
		list[tuple[str, int, str, str, str]]
	"""
	file = open("../data/irregular.txt", "r")
	lines = file.readlines()
	file.close()

	verbs = []
	for line in lines:
		verb = line.split()
		verb[IrregularIdx.CONJUGATION_CLASS] = int(verb[IrregularIdx.CONJUGATION_CLASS]) # from str to int
		verb = tuple(verb)
		verbs.append(verb)
	return verbs

def find_verb_matches(word : str, verbs : list) -> list:
	"""
	Return all verb-tuples that end with <word>.
	
		Construct a list of matches by comparing <word> with the infinitive in <verbs> and if they
		end identically. If so, it is added to the list.

		Parameters:
			word: str --> string to compare the irregular verbs to.
			verbs: list[tuple[str, int, str, str, str]] --> list holding the irregular verb information.
		Return:
			list[tuple[str, int, str, str, str]] --> list of irregular verb-tuples that match the word-ending regex pattern.
	"""
	matches = [verb for verb in verbs if re.findall("(" + verb[IrregularIdx.RGX_INFINITIVE] + ")" + "$", word) != []]
	return matches

def verb_class(word : str, class_num: int) -> v.Verb:
	"""Return corresponding base class Verb (Class 1-4 ONLY) from provided <class_num>"""
	return vutils.get_val_from_dict(int_to_verb_class, class_num)(word)

def construct_verb(word : str, match : tuple) -> v.Verb:
	"""Construct a Verb object manually by overwriting stem values from __init__()."""
	remainder = word[:-len(match[IrregularIdx.RGX_INFINITIVE])]
	verb = v.Verb()
	verb = verb_class(word, match[IrregularIdx.CONJUGATION_CLASS])
	verb.present_stem = remainder + match[IrregularIdx.PRESENT_STEM]
	verb.past_stem = remainder + match[IrregularIdx.PAST_STEM]
	verb.imperative_stem = remainder + match[IrregularIdx.IMPERATIVE_STEM]
	return verb

# removes ambiguities in irregular matches and constructs from the correct match
# TODO: this can be def be refactored a bit, just don't know how.
# TODO: make tests to verify that this works
def disambiguate_verb(match : list , word : str, root : str) -> v.Verb:
	"""Disambiguates between an irregular verb match and a regular verb, constructing the irregular verb."""
	verb = v.Verb()
	m = match[0][IrregularIdx.RGX_INFINITIVE]
	if m == "být" and word == "být" or word == "nebýt":
		verb = v.Byt(word)
	elif m == "dít" and word == "dít":
		# set the stems and use the appropriate constructor
		verb = construct_verb(word, match[0])
	elif m == "stat" or word == "vstát":
		# construct 1st
		verb = construct_verb(word, match[0])
	elif m == "stát":
		if word == "stát":
			# construct both matches
			verb2 = construct_verb(word, match[1])
			verb2.conjugate()
			verb = construct_verb(word, match[0])
		else:
			# construct the 2ND match
			verb = construct_verb(word, match[1])

	# regular verbs that have irregular verb as a substring
	elif (m == "bát" and re.findall("dbát$", word)) or (m == "tát" and re.findall("ptát$", word)):
		verb = None
	elif (m == "kat" and (root != "kat" or re.findall("sekat$", word)) or (m == "kát" and root != "kát")):
		verb = None
	elif (m == "tít" and re.findall("(dštít|křtít)$", word)):
		verb = None
	elif (m == "stít" and re.findall("mstít|lstít$", word)):
		verb = None
	elif m == "pět" and re.findall("(čpět)$", word):
		verb = None
	else:
		verb = construct_verb(word, match[0])
	return verb

# TODO: refactor, do better naming
# TODO: add tests to verify that this works
def determine_verb_class(word : str, root : str) -> v.Verb:
	"""Construct the proper Verb class based on the ending of <word> or <word> as <root>.
	
	Examine the ending found in either <word> or <root>. Slightly irregular
	cases (adhering to a class but having an atypical albeit regular ending)
	have their stems manually added.
	"""
	verb  = v.Verb()
	x = []

	# chovat is class1 otherwise class 2
	if (x := re.findall("ovat$", root)) and not re.search("chovat$", word):
		verb = v.Class2_ovat(word, x[0])
	elif x := re.findall("ít|ýt$", word):
		# řít endings, přít added manually since without t looks like pří prefix and not part of 'root'
		if y := re.findall("řít$", word):
			# class4 general constructor. manually set stems. ...řu, ...řel, ...ři, ending ít
			verb = v.Class4(word, x[0])
			stem = word[:-len(x[0])]
			verb.set_stem(stem)
			verb.set_present_stem(stem)
			verb.set_past_stem(stem + "el")
			verb.set_imperative_stem(stem + "i")
		# cluster rule
		elif re.search(vutils.consonant + "{2,}ít$", root):
			# class3 general constructor. manually set stems. past thematic vowel is e if stem ends in l, if ends in v/d/n/b: ě, +i to stem in imperative, present stem is stem
			verb = v.Class3(word, x[0])
			stem = word[:-2]
			verb.set_stem(stem)
			verb.set_present_stem(stem)
			past = "el" if stem[-1] == "l" else ("ěl" if stem[-1] == "v" or stem[-1] == "d" or stem[-1] == "n" else "il")
			verb.set_past_stem(stem + past)
			verb.set_imperative_stem(stem + "i")
		else:
			verb = v.Class2_ityt(word, x[0])
	elif x := re.findall("at|át$", root):
		if re.search("ápat$", root):
			# class4 general constructor. manusally set stems. present stem is sans at, past: t->l, imperative: at->ej
			verb = v.Class4(word, x[0])
			stem = word[:-len(x[0])]
			verb.set_stem(stem)
			verb.set_present_stem(stem)
			verb.set_past_stem(stem + "al")
			verb.set_imperative_stem(stem + "ej")
		else:
			verb = v.Class1_at(word, x[0])
	elif x := re.findall("it|ět|et$", root):
		verb = v.Class3_itet(word, x[0])
	elif x := re.findall("nout$", root):
		verb = v.Class4_nout(word, x[0])
	elif bool(x := re.findall(vutils.long_vowel + "ct$", root)) or bool(x := re.findall("ouct$", root)):
		verb = v.Class4_ct(word, x[0][-2:])
	elif x := re.findall(vutils.long_vowel + "st$", root):
		verb = v.Class4_st(word, x[0][-2:])
	elif x := re.findall(vutils.long_vowel + "zt$", root):
		verb = v.Class4_zt(word, x[0][-2:])
	elif x := re.findall("out$", root):
		# -out ending. class2 general. manually set stems: present uj, past ul, imperative uj
		verb = v.Class2(word, x[0])
		stem = word[:-len(x[0])]
		verb.set_stem(stem)
		verb.set_present_stem(stem + "uj")
		verb.set_past_stem(stem + "ul")
		verb.set_imperative_stem(stem + "uj")
	else:
		# TODO: print out a different message!
		print("none of the above")
		verb = None
	return verb

# returns .txt as a single regex string to represent the prefixes a verb may begin with
def get_prefixes() -> str:
	"""Retrieve the prefixes from the file as a single regex expression."""
	file = open("../data/prefix.txt", "r")
	lines = file.readlines()
	file.close()

	# append each line (excluding the new line) within an OR capture
	prefixes = "^("
	for line in lines:
		prefixes += "(" + line[:-1] + ")|"
	prefixes =  prefixes[:-1] + ")" # remove last/redundant "|"
	return prefixes


def get_last_prefix(matches : tuple):
	"""Return the last non-empty element in tuple <matches>."""
	prefix_match = ""
	for match in matches:
		if match:
			prefix_match = match # the previous match is overwritten.
	return prefix_match


def get_prefix(word : str, prefixes_expr: str) -> tuple:
	"""
	Extract the prefixes from provided <word>.
	
	Continuously appends consecutive prefixes to string <prefixes> in order to obtain
	a string containing all of the contained prefixes within <word> that
	adhere to the <prefixes> regex pattern. As a result, as <prefixes> expands,
	the remaining length of <word> decreases, eventually reducing it to its
	unprefixed root.

	Parameters:
		word : str --> word to extract the prefixes from.
		prefixes_expr : str -->  regex expression containing all valid verbal prefixes.
	Return:
		tuple[str, str] --> [0]: The resulting string from appending all of the consecutively found prefixes in <word>.
							[1]: The resulting string from removing the found prefixes from <word> within <word> (the root).
	"""
	prefixes = ""
	prefix = ""
	root = ""
	while(1):
		# keep extracting last prefix matched until all have been found.
		word = word[len(prefix):]
		found_prefixes = re.findall(prefixes_expr, word)
		if found_prefixes == []:
			break
		found_prefixes = found_prefixes[0] # list is a singleton
		prefix = get_last_prefix(found_prefixes)
		prefixes += prefix
	root = word
	return (prefixes, root)