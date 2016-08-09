#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import summrio
import helper
import argparse
import pydoc
import sys
import threading

#
#constant values
#
IGNORE_RECURSE_HTML_TAGS = ["a", "script", "strong"]
EXTRACT_HTML_TAGS = ['iframe', 'script', 'style']

#
#functions
#
def get_articletitle(args, soup):
	try:
		articletitle = soup.title.text
		return articletitle
	except:
		articletitle = ""

def treerecurse(node, node_parent, table_parent_wordcount, table_text):
	"""Recurse in order to get to leaf nodes and determine where text is

	Args:
		node: node to check
		node_parent: node's parent node, used as key in tables in order to find where article text is
		table_parent_wordcount: table to keep track of the number of leaf words that belong to parent, used to find where the article text is
			key: node_parent
			value: number of leaf words that belong to that parent node
		table_text: table to store all leaf text that belong to a parent node
			key: node_parent
			value: all leaf text that belong to that parent node

	Future:
		probably will want to improve this in the future, it is not very efficient. Possible recode using regex and make my own tree?
	"""
	children = node.findAll(recursive=False)
	numofchildren = len(children)
	for child in children:
		if (child.name in IGNORE_RECURSE_HTML_TAGS):
			numofchildren -= 1
		else:
			treerecurse(child, node, table_parent_wordcount, table_text)
	if (numofchildren is 0):
		node_text = node.text.encode("UTF-8").strip()
		node_text_wordcount = len(node_text.split())
		if (node_text_wordcount > 2):
			if node_parent in table_parent_wordcount:
				table_parent_wordcount[node_parent] += int(node_text_wordcount)
				table_text[node_parent].append(node_text)
			else:
				table_parent_wordcount[node_parent] = node_text_wordcount
				table_text[node_parent] = [node_text]

def loadingbar(stop_event, percent_decreased):
	iterator = 0
	while (not stop_event.is_set()):
	#while (iterator < percent_decreased):
		sys.stdout.write ("\tArticle decreased by " + str(iterator) + "% \r")
		iterator += 0.01
		sys.stdout.write ("\t\t\t\t\t\t\t\r")
	return iterator

def main(args):
	gl_url = args.url
	if not (gl_url.startswith("http://") or gl_url.startswith("https://")):
		gl_url = "https://" + gl_url
	try:
		gl_soup = helper.get_soup(gl_url)
	except IndexError, e:
		helper.print_error(e, "please pass url as arg1")
	except URLError, e:
		try:
			gl_soup = helper.get_soup_alternate(gl_url)
		except:
			helper.print_error(e, "bad url")

	gl_articletitle = get_articletitle(args, gl_soup)
	[s.extract() for s in gl_soup(EXTRACT_HTML_TAGS)]

	table_parent_wordcount = {}
	table_text = {}
	treerecurse(gl_soup, None, table_parent_wordcount, table_text)

	designated_node_parent = max(table_parent_wordcount, key=lambda k: (table_parent_wordcount[k], len(k)))
	gl_array_article_text = table_text[designated_node_parent]


	gl_table_word_frequency = summrio.get_word_frequency(gl_array_article_text, gl_articletitle)

	if args.tscore:
		helper.print_debug_title("Tag Score")
		helper.print_sorted_table_by_value(gl_table_word_frequency)

	score_all_sentences_output = summrio.score_all_sentences(args, gl_array_article_text, gl_table_word_frequency)
	sentence_stat = score_all_sentences_output[1]
	gl_table_sentence_scoreboard = score_all_sentences_output[0]
	stat_to_beat = summrio.get_stat_to_beat(args, gl_table_sentence_scoreboard, sentence_stat)
	gl_tuple_output = summrio.get_summrio(gl_array_article_text, gl_table_sentence_scoreboard, stat_to_beat)
	
	#gl_tuple_output_clean = summrio.clean_output(gl_tuple_output[0])

	t0_stop.set()
	percent_decreased = gl_tuple_output[1]

	if args.output_file:
		f = open(args.output_file, 'w')
		if args.print_title:
			f.write( ("\n\t%s\n\n") %(gl_articletitle) )
		if args.print_output:
			f.write( ('"""\n%s"""') %(gl_tuple_output[0]) )
		if args.print_stat:
			f.write( ("\n\tArticle decreased by %.2f%%\n") %(gl_tuple_output[1]) )
	else:
		if args.print_title:
			print ("\n\t%s\n\n") %(gl_articletitle)
		if args.print_output:
			print ('"""\n%s"""') %(gl_tuple_output[0])
		if args.print_stat:
			print ("\n\tArticle decreased by %.2f%%\n") %(gl_tuple_output[1])

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Optional app description')
	parser.add_argument('url', type=str, help = 'url string of news article to be summarized')

	parser.add_argument('-of', '--output_file', type=str, help = 'url string of news article to be summarized')
	parser.add_argument('-po', '--print_output', action='store_true', help='Prints the summrio')
	parser.add_argument('-ps', '--print_stat', action='store_true', help='Prints the percent the summrio reduced')
	parser.add_argument('-pt', '--print_title', action='store_true', help='Displays the article title')

	parser.add_argument('-an', '--animation', action='store_true', help='Displays the article title')

	parser.add_argument('-dts', '--tscore', action='store_true', help='DEBUG: view word tags')
	parser.add_argument('-dps', '--pscore', action='store_true', help='DEBUG: view sentence position')
	parser.add_argument('-dss', '--sscore', action='store_true', help='DEBUG: view sentence score')
	parser.add_argument('-dst', '--statscore', action='store_true', help='DEBUG: An optional switch to view stats')
	args = parser.parse_args()

	percent_decreased = 200

	t0_stop = threading.Event()
	t0 = threading.Thread(target=loadingbar, args=(t0_stop, percent_decreased))
	t1 = threading.Thread(target=main, args=(args,))

	if args.animation:
		t0.start()
	t1.start()
	t1.join()

#	main(args)
