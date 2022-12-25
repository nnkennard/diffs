import pandas as pd
import json
import numpy as np
import nltk.data
import jellyfish
import stanza
import copy

stanza.download('en') # if needed, just once

STANZA_PIPELINE = stanza.Pipeline('en',
processors='tokenize',)

#load in events_iclr_2019.tsv, events_iclr_2020.tsv using pandas
df = pd.read_csv('events_iclr_2019.tsv', delimiter='\t')
df2 = pd.read_csv('events_iclr_2020.tsv', delimiter='\t')
main_df = pd.concat([df, df2])
global diff_df
diff_df = pd.DataFrame(columns=["forum", "initiator", "type", "file1", "file2", "sentence1", "sentence2", "align1", "align2", "distance", "replyTo", "score1", "score2", "confidence1", "confidence2"])
def get_diffs(text):
        diffs = []
        print("GET DIFFS")
        for i in range(len(text)-1):
            text1 = text[i]
            text2 = text[i+1]
            text1 = text1.replace('\n', '')
            text2 = text2.replace('\n', '')
            text1_sentences = STANZA_PIPELINE(text1).sentences
            text2_sentences = STANZA_PIPELINE(text2).sentences
            if(len(text1_sentences) != len(text2_sentences)):
                if(len(text2_sentences) > len(text1_sentences)):
                    print("Text 2 has {} more sentences than text 1\n".format(len(text2_sentences) - len(text1_sentences)))
                else:
                    print("Text 1 has {} more sentences than text 2\n".format(len(text1_sentences) - len(text2_sentences)))
            edits = []
            sentences = []
            for i in range(len(text1_sentences)):
                distance = jellyfish.levenshtein_distance(text1_sentences[i].text, "")
                alignment = -1
                #align sentences based on minimum leventshtein distance
                for j in range(len(text2_sentences)):
                    # print(text2_sentences[j].text)
                    if(jellyfish.levenshtein_distance(text1_sentences[i].text, text2_sentences[j].text) < distance):
                        distance = jellyfish.levenshtein_distance(text1_sentences[i].text, text2_sentences[j].text)
                        alignment = j
                entry = (text1_sentences[i].text, text2_sentences[alignment].text, i, alignment, distance)
                edits.append(entry)
                sentences.append(alignment)
            #unaligned sentences in text2
            print("Unaligned sentences in text 2\n")
            for i in range(len(text2_sentences)):
                if(i not in sentences):
                    # print("Sentence {} in text 2: {}\n".format(i, text2_sentences[i].text) + '\n')
                    entry = ("", text2_sentences[i].text, -1, i, len(text2_sentences[i].text))
                    edits.append(entry)
            diffs.append(edits)
        return diffs

def evaluate_diffs(reviews_raw, comments_raw, dict):
    # if(len(reviews_raw) > 0):
    #     print("REVIEWS")
    #     text = []
    #     for entry in reviews_raw:
    #         text.append(entry[0]['review'])
    #     diffs = get_diffs(text)
    #     print(len(diffs))
    #     dict['type'] = "review"
    #     for i in range(len(diffs)):
    #         template = copy.deepcopy(dict)
    #         template["type"] = "review"
    #         template["file1"] = reviews_raw[i][1]
    #         template["file2"] = reviews_raw[i+1][1]
    #         template["score1"] = reviews_raw[i][0]['rating'][0]
    #         template["score2"] = reviews_raw[i+1][0]['rating'][0]
    #         template["confidence1"] = reviews_raw[i][0]['confidence'][0]
    #         template["confidence2"] = reviews_raw[i+1][0]['confidence'][0]
    #         for entry in diffs[i]:
    #             template_sentence = copy.deepcopy(template)
    #             template_sentence["sentence1"] = entry[0]
    #             template_sentence["sentence2"] = entry[1]
    #             template_sentence["align1"] = entry[2]
    #             template_sentence["align2"] = entry[3]
    #             template_sentence["distance"] = entry[4]
    #             template_df = pd.DataFrame(template_sentence, index=[0])
    #             global diff_df
    #             diff_df = pd.concat([diff_df, template_df], ignore_index=True)
    if(len(comments_raw) > 0):
        text = []
        for entry in comments_raw:
            text.append(entry[0]['comment'])
        diffs = get_diffs(text)
        dict['type'] = "comment"
        for i in range(len(diffs)):
            template = copy.deepcopy(dict)
            template["type"] = "comment"
            template["file1"] = reviews_raw[i][1]
            template["file2"] = reviews_raw[i+1][1]
            for entry in diffs[i]:
                template_sentence = copy.deepcopy(template)
                template_sentence["sentence1"] = entry[0]
                template_sentence["sentence2"] = entry[1]
                template_sentence["align1"] = entry[2]
                template_sentence["align2"] = entry[3]
                template_sentence["distance"] = entry[4]
                template_df = pd.DataFrame(template_sentence, index=[0])
                global diff_df
                diff_df = pd.concat([diff_df, template_df], ignore_index=True)
    diff_df.to_csv('Test.csv')
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
        print(refined)
        for initiator in refined['initiator']:
                print("Initiator: {}".format(initiator))
                dict = {
                    "forum": refined['forum'].iloc[0],
                    "initiator": initiator,
                    "reply_to": refined['reply_to'].iloc[0]
                }
                print(dict)
                entries = results[results['initiator'] == initiator]
                print(entries['reference_index'])
                reviews_raw = []
                comments_raw = []
                for entry in entries['filepath']:
                    with open(entry, 'r', encoding='utf-8') as file:
                        for line in file:
                            j = json.loads(line)
                            if 'comment' in j:
                                comments_raw.append((j, entry))
                            elif 'review' in j:
                                reviews_raw.append((j, entry))
                evaluate_diffs(reviews_raw, comments_raw, dict)
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
