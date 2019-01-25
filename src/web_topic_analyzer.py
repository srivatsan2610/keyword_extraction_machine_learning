"""
@summary: Controller class which calls all functions to 
execute steps of the algorithm
This class object is called from project_ui.py to
run the analyzer for the given input.
@author: Srivatsan Ananthakrishnan
"""
import content_extraction, html_parser
import noun_extractor
import k_means_grouper
import operator
import ranking

class WebTopicAnalyzer:
    """Analyzer to analyze the topics related to a web page"""
    def __init__(self, url):
        self.__url = url;
    
    def process(self):   
        try:
            #step 1: get text content and title
            print("INFO: Getting the text content of web page.");
            title, content = content_extraction.get_text(self.__url);
            if (title == None or content == None):
                raise ValueError("Could not retrieve text data.");
            #step 2: Get all title, h1, meta tags of the web page.
            print("INFO: Getting the title, meta and h1 tag content of web page.");
            title_content, meta_content, h1_tag_content = html_parser.parse_html(self.__url);
            #step 3: get noun words and phrases (from wiki search)
            print("INFO: Extracting single word nouns from text content and searching related phrases from wikipedia articles.");
            print("INFO: This might take a few seconds.");
            nouns = noun_extractor.get_nouns(title, content);
            is_input_small = False;
            if(len(nouns) < 15):
                is_input_small = True;
            #step 4: ranking - giving scores to each word based on several factors.
            print("INFO: Ranking words and phrases based on factors like occurrence, frequency etc.");
            ranked_words = [];
            for w in nouns:
                ranked_word = ranking.do_rank(self.__url, w, content, title_content, meta_content, h1_tag_content);
                ranked_words.append(ranked_word);
            #step 5: grouping of similar phrases and  eliminating repetition for more diverse keywords
            print("INFO: Grouping similar words to clusters and getting the most ranked words from each cluster");
            print("INFO: This might take a few seconds.");
            words, clusters = k_means_grouper.get_clusters(ranked_words);
            cluster_count = 0;
            final_ranked_words = [];
            #Add all keywords that did not have a match in data-set and hence cannot be grouped.
            final_ranked_words.extend(words)
            #sort each data clustered based on ranks and get the highest ranked data from a cluster
            for data_cluster in clusters:
                data_cluster.sort(key=operator.attrgetter('score'), reverse=True)
                #Taking the most ranked word of the cluster
                final_ranked_words.append(data_cluster[0]);
            print("INFO: Sorting all the words and phrases based on the ranking scores and getting Top 15 words.");
            #sort the final list of ranked words
            final_ranked_words.sort(key=operator.attrgetter('score'), reverse=True)
            count = 0;
            key_words = [];
            #Will show first 15 ranked keywords
            for rw in final_ranked_words:
                count += 1;
                if len(key_words) == 15:
                    break;
                else:
                    if rw.isUpper:
                        key_words.append(rw.getword().upper());
                    else:
                        key_words.append(rw.getword().title());
            print("INFO: Success, check your words in the UI.");
            if(count < 15):
                return {'words' : key_words, "is_input_small" : is_input_small};
            else:
                return {'words' : key_words};
        except ValueError as e:
            print(e);
            return {"error": e};
        except Exception as e:
            print("ERROR: Some error occurred.");
            print(e);
            return {"error": "Sorry, something went wrong! Please verify the URL."};

if __name__ == '__main__':
    print("This file can only be imported!")
