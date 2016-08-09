# -*- coding: utf-8 -*-

import helper
import re
import argparse
import pydoc
import math

#
#constant values, placed for easy adjustment
#
IGNORE_COMMON_WORDS = ["what", "this", "asked", "tells", "that", "said", "they", "when", 'with']
#word Scores; Used to get tags
SCORE_WORD_USE = 1
SCORE_WORD_CAPITAL = 5
SCORE_WORD_INTEXTTITLE = 20
#word Ignore Values; Used to get tags
IGNORE_WORD_LENGTH_LESS_THAN = 4 #letters
IGNORE_WORD_USED_LESS_THAN = 4 #times
#sentence scores
SCORE_SENTENCE_TOP_PARAGRAPH_PROXIMITY_ELIGIBLE = 5 #first x paragraphs in text
SCORE_SENTENCE_TOP_PARAGRAPH_PROXIMITY = 60 #/iter_paragraph
SCORE_SENTENCE_TOP_SENTENCE_PROXIMITY_ELIGIBLE = 5 #first x sentences in paragraph
SCORE_SENTENCE_TOP_SENTENCE_PROXIMITY = 25 #/iter_sentence

#
#functions
#
def get_word_frequency(array_text, texttitle):
	table_word_frequency = {}
	for paragraph in array_text:
		for word in re.compile("\w+\'*\w*").findall(paragraph):
			if len(word) >= IGNORE_WORD_LENGTH_LESS_THAN:
				multiplier = SCORE_WORD_USE
				if word.istitle():
					multiplier += SCORE_WORD_CAPITAL
				word = word.lower()
				if word in table_word_frequency:
					table_word_frequency[word] += multiplier
				else:
					table_word_frequency[word] = multiplier
	for word in table_word_frequency:
		if (table_word_frequency[word] <= IGNORE_WORD_USED_LESS_THAN):
			IGNORE_COMMON_WORDS.append(word)
		if word in texttitle.lower():
			multiplier += SCORE_WORD_INTEXTTITLE
	for word in IGNORE_COMMON_WORDS:
		if word in table_word_frequency:
			del table_word_frequency[word]
	return table_word_frequency

def score_all_sentences(args, array_text, table_word_frequency):
	"""Score the sentences based on tags and proximity to top of article and paragraph

	Args:
		args:
		array_text:
		table_word_frequency:

	Returns:
		table_sentence_scoreboard:
	"""
	table_sentence_scoreboard = {}
	iter_paragraph = 0

	sentence_score_total = 0
	sentence_total = 0

	if args.pscore:
		helper.print_debug_title("Sentence Position")

	for paragraph in array_text:
		iter_paragraph += 1
		sentences = re.split(r'(?<=[!?.])(?<!\d.)\s', paragraph)
		iter_sentence = 0
		for sentence in sentences:
			iter_sentence += 1
			score_sentence = 0
			for word in re.compile("\w+\'*\w*").findall(sentence):
				try:
					score_sentence += table_word_frequency[word]
				except KeyError:
					continue
			if (iter_paragraph <= SCORE_SENTENCE_TOP_PARAGRAPH_PROXIMITY_ELIGIBLE):
				score_sentence += (SCORE_SENTENCE_TOP_PARAGRAPH_PROXIMITY/iter_paragraph)
			if (iter_sentence <= SCORE_SENTENCE_TOP_SENTENCE_PROXIMITY_ELIGIBLE):
				score_sentence += (SCORE_SENTENCE_TOP_SENTENCE_PROXIMITY/iter_sentence)

			table_sentence_scoreboard[sentence] = score_sentence
			sentence_score_total += score_sentence
			sentence_total += 1

			if args.pscore:
				print ("p%02ds%02d::: %02d ::: %s") %(iter_paragraph, iter_sentence, score_sentence, sentence)
	sentence_stat = [sentence_score_total, sentence_total]
	score_all_sentences_output = [table_sentence_scoreboard, sentence_stat]
	return score_all_sentences_output

def get_stat_to_beat(args, table_sentence_scoreboard, sentence_stat):
	"""Gets stats from the table_sentence_scoreboard and determines that stat to beat to be deemed as part of the summrio
	
	Args:
		args:
		table_sentence_scorebaord:

	Returns:
		stat_to_beat:
	"""
	sentence_score_total = sentence_stat[0]
	sentence_score_total_squared = 0
	sentence_total = sentence_stat[1]

	if args.sscore:
		helper.print_debug_title("Sentence Score")
		helper.print_sorted_table_by_value(table_sentence_scoreboard)

	p_view = [ (v,k) for k,v in table_sentence_scoreboard.iteritems() ]
	p_view.sort(reverse=True) # natively sort tuples by first element

	#Get Average
	average = sentence_score_total/sentence_total

	#Get variance
	for v,k in p_view:
		sentence_score_total_squared += ((v-average)**2)

	variance = sentence_score_total_squared/float(sentence_total)
	standard_deviation = math.sqrt(variance)
	stat_to_beat = average + standard_deviation

	if args.statscore:
		helper.print_debug_title("Stat Score")
		print "average: " + str(average)
		print "variance: " + str(variance)
		print "standard deviation: " + str(standard_deviation)
		print "stat to beat: " + str(stat_to_beat)

	return stat_to_beat

def get_summrio(array_text, table_sentence_scoreboard, stat_to_beat):
	"""Print the summrio

	Args:
		array_text:
		table_sentence_scoreboard:
		stat_to_beat:

	Returns:
		output: summrio output string
	"""
	output = ""
	sentence_total = 0
	sentence_total_summrio = 0
	for paragraph in array_text:
		neednewline = False
		sentences = re.split(r'(?<=[!?.])(?<!\d.)\s', paragraph)
		for sentence in sentences:
			sentence_total += 1
			if table_sentence_scoreboard[sentence] > stat_to_beat:
				output += sentence
				sentence_total_summrio += 1
				neednewline = True
		if neednewline is True:
			output += "\n\n"
	percent_decreased = 100*(1-(sentence_total_summrio/float(sentence_total)))
	tuple_output = (output, percent_decreased)
	return tuple_output

def clean_output(text_to_clean):
	text_to_clean.replace("ΓÇö", "--")
	return text_to_clean