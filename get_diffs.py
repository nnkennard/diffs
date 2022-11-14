import pandas as pd
import json
import numpy as np
import nltk.data
import jellyfish
import stanza

stanza.download('en') # if needed, just once

text = "Here is a sentence. Here is another sentence, as well."

STANZA_PIPELINE = stanza.Pipeline('en',
processors='tokenize',)
output_file = 'diffs.txt'
doc = STANZA_PIPELINE(text)
for sentence in doc.sentences:
    print(sentence)

#load in events_iclr_2019.tsv, events_iclr_2020.tsv using pandas
df = pd.read_csv('events_iclr_2019.tsv', delimiter='\t')
df2 = pd.read_csv('events_iclr_2020.tsv', delimiter='\t')
main_df = pd.concat([df, df2])

def get_diffs(text, file):
    with open(output_file, 'a', encoding='utf-8') as file:
        print("GET DIFFS")
        for i in range(len(text)-1):
            text1 = text[i]
            text2 = text[i+1]
            text1 = text1.replace('\n', '')
            text2 = text2.replace('\n', '')
            distance = jellyfish.levenshtein_distance(text1, text2)
            if(distance == 0):
                file.write("No change\n")
                continue
            text1_sentences = STANZA_PIPELINE(text1).sentences
            text2_sentences = STANZA_PIPELINE(text2).sentences
            if(len(text1_sentences) != len(text2_sentences)):
                if(len(text2_sentences) > len(text1_sentences)):
                    file.write("Text 2 has {} more sentences than text 1\n".format(len(text2_sentences) - len(text1_sentences)))
                else:
                    file.write("Text 1 has {} more sentences than text 2\n".format(len(text1_sentences) - len(text2_sentences)))
            edits = []
            for i in range(len(text1_sentences)):
                distance = np.inf
                alignment = -1
                #align sentences based on minimum leventshtein distance
                for j in range(len(text2_sentences)):
                    print(text2_sentences[j].text)
                    if(jellyfish.levenshtein_distance(text1_sentences[i].text, text2_sentences[j].text) < distance):
                        distance = jellyfish.levenshtein_distance(text1_sentences[i].text, text2_sentences[j].text)
                        alignment = j
                    if(distance == 0):
                        break
                file.write("Sentence {} in the original corresponds with sentence {} in the revision\n".format(i, alignment))
                if(distance > 0):
                    file.write("Differences: {}".format(distance) + '\n')
                    file.write(text1_sentences[i].text + '\n')
                    file.write(text2_sentences[alignment].text + '\n')
                edits.append(alignment)
            #unaligned sentences in text2
            file.write("Unaligned sentences in text 2\n")
            for i in range(len(text2_sentences)):
                if(i not in edits):
                    file.write("Sentence {} in text 2: {}\n".format(i, text2_sentences[i].text) + '\n')

def evaluate_diffs(initiator, file):
    if(len(initiator['comments']['comments_raw']) > 1):
        print("COMMENT")
        get_diffs(initiator['comments']['comments_raw'], file)
    if(len(initiator['reviews']['reviews_raw']) > 1):
        print("REVIEW")
        get_diffs(initiator['reviews']['reviews_raw'], file)
replies = main_df['reply_to'].unique()
#create a dictionary with all of the useful info that there is a way to organize this in the future
#the structure will go as follows:
#reply_to: {contributor: {comments: {comments_raw: [], diffs: []}, reviews: {reviews_raw: [], diffs: []}}}
print(replies)
dictionary = {}
for r in replies:
    results = main_df[main_df['reply_to'] == r]
    refined = results[results['reference_index'] > 0]
    if(len(refined) > 0):
        if(r not in dictionary):
            dictionary[r] = {}
        for i in refined['initiator']:
            print(i)
            entries = results[results['initiator'] == i]
            print(entries)
            with open(output_file, 'a', encoding='utf-8') as f2:
                f2.write(entries['forum'].iloc[0] + "\t" + i + "\n")
                dictionary[r][i] = {'comments': {'comments_raw': [], 'diffs': []}, 'reviews': {'reviews_raw': [], 'diffs': []}}
                for entry in entries['filepath']:
                    with open(entry, 'r', encoding='utf-8') as file:
                        for line in file:
                            j = json.loads(line)
                            if 'comment' in j:
                                dictionary[r][i]['comments']['comments_raw'].append(j['comment'])
                            elif 'review' in j:
                                dictionary[r][i]['reviews']['reviews_raw'].append(j['review'])
                evaluate_diffs(dictionary[r][i], file)
        #evaluate the diffs
#convert all of this to a dictionary 

# print(main_df.iloc[0]['filepath'])
# print(main_df.iloc[1]['filepath'])
# s = main_df[main_df['forum'] == main_df.iloc[10]['forum']]
# # print(s)
# ar = s[s['event_type'] == 'comment']
# ar = ar[ar['initiator'] == 'AnonReviewer2']
# print(ar)
# review = []
# for i in range(len(ar)):
#     with open(ar.iloc[i]['filepath'], 'r', encoding='utf8') as file:
#         print(ar.iloc[i]['filepath'])
#         for line in file:
#             review.append(json.loads(line))
# #even when they are labelled as comments in the tsv, the actual json files themselves contain both review and comments
# print('\n\n')
