'''
@summary:
Extracts nouns from the content of the article and get related
keywords from wikipedia.
Uses third party libraries Spacy and wikipedia.
Spacy identifies nouns from the content,
For each identified noun word, we do a search in wikipedia to 
get 50 search results.
If any of the search result is in article content, that phrase is 
taken as a potential keyword along with the noun.
@author: Srivatsan Ananthakrishnan
'''
#Reference for Spacy implementation http://spacy.io/docs/usage/

import copy
from itertools import combinations
from time import sleep
import spacy
import wikipedia


from ranked_word import RankedWord
from newspaper import article

#Load spacy English dataset
nlp = spacy.load('en');

def get_nouns(title, content):
    """Get all noun chunks from the title and content text
    and get word phrases using wikipedia search"""
    article_content = title + " " + content;
    #Get words which are proper nouns and special case nouns
    dict_nouns = extract_nouns(article_content);
    #once we get noun candidates (individual words), we search wiki articles to 
    #see if there is any related word phrase results that is also 
    #present in our web-content
    wiki_results = {};
    for noun in dict_nouns.values():
        if noun.isPos:#Is Proper Noun? only then go for wiki search.
            wiki_phrase = search_wiki(noun, article_content, dict_nouns);
            if wiki_phrase is not None:#If wiki result matches the content, add it as a candidate
                wiki_phrase = wiki_phrase.rstrip().lstrip();
                wiki_results[wiki_phrase] = RankedWord(wiki_phrase, noun.isPos);
    #Reference: https://docs.python.org/3/library/copy.html
    #Remove duplicates by removing repetition. Ex: one word is Washington and another word is Washington Post.
    #Remove Washington, we need only Washington Post
    dict_nouns_copy = copy.deepcopy(dict_nouns)
    remove_duplicates(dict_nouns, dict_nouns_copy, True);
    #Remove duplicates by comparing noun dictionary and wiki result dict
    remove_duplicates(dict_nouns, wiki_results);
    wiki_results_copy = copy.deepcopy(wiki_results)
    #Remove duplicates by avoiding repetition in wiki_results
    remove_duplicates(wiki_results, wiki_results_copy, True);
    return list(dict_nouns.values())+list(wiki_results.values());



def extract_nouns(article_content):
    """Gets nouns in the article content using Spacy"""
    #load spacy for English
    doc = nlp(article_content)
    compound_val = '';#For compound words, Ex: First token is Donald, and second token is Trump.
    #It would be better to do a wiki search for "Donald Trump" than "Donald" and "Trump" separately 
    dict_nouns = {};
    for token in doc:
        #print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
        #  token.shape_, token.is_alpha, token.is_stop, token.ent_type_)
        isCapitalToken = token.text.isupper();#To show words like CNN as all case capital in UI.
        #recommendations and heuristics : Fine tuning candidates
        #Candidates are chosen with this algorithm:
        #1) If word is a proper noun and not too short word length 
        #2)If word is a noun that is not too short and not belonging to WH words like who, what, where.
        #3)We don't need Date nouns.
        #4)We don't want proper nouns who don't have a definite entity type.
        token_val = token.text.rstrip().lstrip().lower();
        if (token.pos_ == 'PROPN' and len(token.text) > 2 and token.ent_type_ != "") or \
        (token.pos_ == 'NOUN' and token.tag_ != 'WP' and len(token.text) > 3 ):
            if(token.ent_type_ != 'DATE' and token.ent_type_ != 'TIME'):
                wr = RankedWord(token_val, (token.pos_ == 'PROPN'), isUpper = isCapitalToken)
                if (wr.getword() not in dict_nouns):
                    dict_nouns [wr.getword()] = wr;
            elif token_val in dict_nouns:
                #Some tokens like a date could be considered Proper Noun in some context and noun in some content
                #In those case, remove it
                del dict_nouns[token_val];
        elif token_val in dict_nouns:
            del dict_nouns[token_val];#remove if it is not a noun in another context
        
        #Searching for compound values to get more specific results
        if (token.pos_ == 'NOUN' or token.pos_ == 'PROPN') and token.dep_ == 'compound':
            compound_val += ' ' + token.text;#First time compound word, save it
        elif compound_val != '':#Earlier word was compound
            if token.pos_ != "PART":
                compound_val += " " + token.text; 
            compound_val = compound_val.lstrip().rstrip();
            rw = RankedWord(compound_val, (token.pos_ == 'PROPN'));
            wiki_phrase = search_wiki(rw, article_content, dict_nouns);
            if wiki_phrase is not None:
                rw = RankedWord(wiki_phrase, (token.pos_ == 'PROPN'));
                dict_nouns[rw.getword()] = rw;
            compound_val = '';
        else:
            compound_val = '';#clearing once compound done
    return dict_nouns;


def search_wiki(noun, article_content, dict_nouns):
    """Search wikipedia for articles with noun keyword in title"""
    try:
        wiki_result = wikipedia.search(noun.getword(), results=50);
    except Exception as e:#sometimes, connection is refused because our application exceeds maximum trys.
        #So sleep for 5 seconds before doing next search.
        sleep(5);
        print(e);
        return None;
    else:
        for wiki_topic in wiki_result:
            wiki_topic = wiki_topic.lower().rstrip().lstrip();
            topics = wiki_topic.split();
            #for easier comparison, converting to lower case
            #We need only phrases here, don't need words as it would be duplicate
            #Checking if the phrase is in the web content.
            #Ex: We will have words Statue and Liberty in noun array, 
            #Wiki results will get the phrase Statue of Liberty and if it is in web page, 
            #this phrase is a potential candidate
            #https://en.wikipedia.org/wiki/Wikipedia:Article_titles#Deciding_on_an_article_title
            if len(topics) > 1  and contains(wiki_topic, article_content.lower()):
                #Dont want cases like "The Case" where we get a result as "The <existing_noun_candidate"
                if(len(topics) == 2 and topics[0] == "the"):
                    return None;
                return wiki_topic;
            #Heuristics, for places wiki standard is to add a comma, ex: San Jusan, Peuto Rico.
            #If I need to search San Juan, we need to split by , and see
            elif (',' in wiki_topic) and any(t in article_content.lower() for t in wiki_topic.lower().split(",")):
                phrases = wiki_topic.lower().split(",");
                for phrase in phrases:
                    phrase = phrase.lstrip().rstrip();
                    if phrase in article_content.lower():
                        count = 0;
                        for ph in phrase.split():
                            if ph in dict_nouns:# and dict_nouns[ph].isPos and (len(ph.split()) > 1):
                                count += 1;
                        if(count == len(phrase.split())):
                            return phrase;
                                            

def remove_duplicates(dict_1, dict_2, isSame=False):
    """Remove occurrences in dict_1 for occurrence in dict_2"""
    #For values like 'The Washington Post" in dict_2,
    #we will remove The, Washington and Post from dict_1 
    for dict_2_val in dict_2.keys():#For each key in dict_2
        arr = dict_2_val.split();
        for i in range(0,len(arr)):#Starting point varies from 0 to len
            dict_2_val_arr = dict_2_val.split()[i:len(arr)];
            for i in range(1, len(dict_2_val_arr)+1):
                #Get different combination of string in dict_2
                iter_k = combinations(dict_2_val_arr, i)
                curr_combination = ' '.join(iter_k.__next__());
                for nn in list(dict_1):#Checking if current combination is present in dict_1
                    if curr_combination.rstrip().lstrip() == nn.rstrip().lstrip():
                        #If checking for duplicates against same dict, don't erase the value
                        if isSame and (curr_combination.rstrip().lstrip() == dict_2_val.rstrip().lstrip()):
                            pass
                        else:
                            #Delete from dict_1 if present in dict_2
                            del dict_1[nn.rstrip().lstrip()];

def contains(str1, str2):
    """Check if str1 occurs in str2 in any format"""
    begin_list = [" ", ".", ". ",", ", ",", "!", "! ", "'", "(", "/"];
    end_list = [" ", ".", ". ",", ", ",", "!", "! ", "'", ")", "/"];
    for begin_str in begin_list:#Different combination of string with special characters
        #possible in text.  Ex:- searching 'Donald Trump' or Donald Trump,
        for end_str in end_list:
            if (begin_str+str1+end_str in str2):
                return True;
                            
if __name__ == '__main__':
    print("This file can only be imported!")
