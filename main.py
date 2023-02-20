import pandas as pd
import requests
import bs4
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

driver_path = Service('chromedriver_linux64/chromedriver')
driver = webdriver.Chrome(service=driver_path)


def get_title_and_article_text():  # by using beautifulsoup
    read_xl = pd.read_excel('Input.xlsx')
    data = {}
    url_id = 37
    all_links = []
    urls = []
    for i in read_xl['URL']:
        response = requests.get(i)
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        if soup.find('h1', class_='entry-title') and soup.find('div', class_='td-post-content') is not None:
            title = soup.find('h1', class_='entry-title').text.strip()
            content = soup.find('div', class_='td-post-content').text
            data[title] = content.replace('\n', '')
            all_links.append(i)
            urls.append(url_id)
            url_id += 1
        else:
            url_id -= 1
        print(len(all_links), len(urls), url_id, len(data))
    return data, all_links, urls


def get_title_and_article_text_by_selenium():  # by using selenium webdriver
    read_xl = pd.read_excel('Input.xlsx')
    data = {}
    url_id = 37
    all_links = []
    urls = []
    for i in read_xl['URL']:
        driver.get(i)
        if driver.find_element(By.CLASS_NAME, 'entry-title') is not None and driver.find_element(By.CLASS_NAME, 'td-post-content') is not None:
            title = driver.find_element(By.CLASS_NAME, 'entry-title').text.strip()
            content = driver.find_element(By.CLASS_NAME, 'td-post-content').text
            data[title] = content.replace('\n', '')
            all_links.append(i)
            urls.append(url_id)
            url_id += 1
        else:
            url_id -= 1
        print(len(all_links), len(urls), url_id, len(data))
        driver.quit()
    return data, all_links, urls


def store_data_to_excel_file():
    data, all_links, urls = get_title_and_article_text()
    # create a Pandas dataframe from the dictionary
    df = pd.DataFrame.from_dict(data, orient='index', columns=['Value'])

    # create an Excel writer object
    writer = pd.ExcelWriter('data_collected_from_urls.xlsx')

    # write the dataframe to the Excel file
    df.to_excel(writer, sheet_name='Sheet1')

    # save the Excel file
    writer.close()


def combine_all_stopwords():
    # Define a list of file names
    file_names = ['StopWords_Auditor.txt', 'StopWords_Currencies.txt', 'StopWords_DatesandNumbers.txt',
                  'StopWords_Generic.txt', 'StopWords_GenericLong.txt', 'StopWords_Geographic.txt',
                  'StopWords_Names.txt']

    # Open the output file in write mode
    with open('combined_stop_words.txt', 'w') as outfile:
        # Loop through the list of file names
        for fname in file_names:
            # Open each file in read mode
            with open(f'StopWords/{fname}', mode='r', encoding='latin-1') as infile:
                # Read the contents of the file
                contents = infile.read()
                # Write the contents to the output file
                outfile.write(contents)
    with open('combined_stop_words.txt', mode='r', encoding='UTF-8') as file:
        a = file.readlines()
        temp = []
        for i in a:
            if '|' in i:
                temp.append(i.split('|')[0].strip().lower())
                temp.append(i.split('|')[1].strip().lower())
            else:
                temp.append(i.replace('\n', '').lower())
        return temp


def cleanStopWordsInLinks():
    read_xl = pd.read_excel('data_collected_from_urls.xlsx')
    all_articles_from_xlfile = read_xl['Value'].to_list()
    stopwords = combine_all_stopwords()
    for i in range(len(all_articles_from_xlfile)):
        words = all_articles_from_xlfile[i].split()  # split the element into a list of words
        for word in stopwords:
            if word in words:
                words.remove(word)  # remove the word if it's present in the element
        all_articles_from_xlfile[i] = ' '.join(words)  # join the remaining words back into a string
    return all_articles_from_xlfile


def positive_words_identification():
    with open('MasterDictionary/positive-words.txt', mode='r', encoding='UTF-8') as file:
        temp = file.readlines()
        positive_words = []
        positive_word_score = []
        positive_words_found_in_articles = []
        for i in temp:
            positive_words.append(i.replace('\n', ''))
        all_articles = cleanStopWordsInLinks()
        for i in range(len(all_articles)):
            positive_score = 0
            words = all_articles[i].split()  # split the element into a list of words
            for word in positive_words:
                if word in words:
                    positive_score += 1
                    positive_words_found_in_articles.append(word)
                    words.remove(word)  # remove the word if it's present in the element
            all_articles[i] = ' '.join(words)  # join the remaining words back into a string
            positive_word_score.append(positive_score)
        return positive_word_score


def negative_words_identification():
    with open('MasterDictionary/negative-words.txt', mode='r', encoding='latin-1') as file:
        temp = file.readlines()
        negative_words = []
        negative_word_score = []
        negative_words_found_in_articles = []
        for i in temp:
            negative_words.append(i.replace('\n', ''))
        all_articles = cleanStopWordsInLinks()
        for i in range(len(all_articles)):
            negative_score = 0
            words = all_articles[i].split()  # split the element into a list of words
            for word in negative_words:
                if word in words:
                    negative_score += 1
                    negative_words_found_in_articles.append(word)
                    words.remove(word)  # remove the word if it's present in the element
            all_articles[i] = ' '.join(words)  # join the remaining words back into a string
            negative_word_score.append(negative_score)
        return negative_word_score


def calculate_polarity_score():
    positive_scores = positive_words_identification()
    negative_scores = negative_words_identification()
    polarity_scores = []
    for i in range(len(positive_scores)):
        polarity_score = (positive_scores[i] - negative_scores[i]) / (
                (positive_scores[i] + negative_scores[i]) + 0.000001)
        polarity_scores.append(polarity_score)
    return polarity_scores


def calculate_subjectivity_score():
    all_articles = cleanStopWordsInLinks()
    positive_scores = positive_words_identification()
    negative_scores = negative_words_identification()
    total_words_after_cleaning = []
    for i in range(len(all_articles)):
        total_words = len(all_articles[i].split(' '))
        after_cleaning_word_count = total_words - (positive_scores[i] + negative_scores[i])
        total_words_after_cleaning.append(after_cleaning_word_count)
    subjectivity_scores = []
    for i in range(len(all_articles)):
        subjectivity_score = (positive_scores[i] + negative_scores[i]) / (total_words_after_cleaning[i] + 0.000001)
        subjectivity_scores.append(subjectivity_score)
    print(subjectivity_scores)
    return subjectivity_scores


def count_complex_words(sentence):
    # Define a regular expression that matches vowel groups
    vowel_pattern = re.compile(r'[aeiouy]+', re.IGNORECASE)

    # Split the sentence into individual words
    words = sentence.split()

    # Count the number of complex words
    complex_word_count = 0
    for word in words:
        # Count the number of vowel groups in the word
        syllable_count = len(vowel_pattern.findall(word))

        # If the word has two or more syllables, count it as complex
        if syllable_count >= 2:
            complex_word_count += 1

    return complex_word_count


def analysis_of_readability():
    all_articles = cleanStopWordsInLinks()
    average_sentence_length = []
    percentage_of_complex_words = []
    fog_index = []
    for i in range(len(all_articles)):
        no_of_words = len(all_articles[i].split(' '))
        no_of_sentences = len(all_articles[i].split('. '))
        complex_words = count_complex_words(all_articles[i])
        average_length_of_sentence = (no_of_words / no_of_sentences)
        complex_words_percentage = (complex_words / no_of_words)
        fog = (0.4 * (average_length_of_sentence + complex_words_percentage))
        average_sentence_length.append(average_length_of_sentence)
        percentage_of_complex_words.append(complex_words_percentage)
        fog_index.append(fog)
    return average_sentence_length, percentage_of_complex_words, fog_index


def get_all_data_and_convert_it_into_excel_file():
    data = {}
    data_set, all_links, urls = get_title_and_article_text()
    positive_list = positive_words_identification()
    negative_list = negative_words_identification()
    polarity_list = calculate_polarity_score()
    subjective_list = calculate_subjectivity_score()
    average_sentence_list, percentage_list, fog_list = analysis_of_readability()

    # creating data
    data['URL_ID'] = urls
    data['URL'] = all_links
    data['POSITIVE SCORE'] = positive_list
    data['NEGATIVE SCORE'] = negative_list
    data['POLARITY SCORE'] = polarity_list
    data['SUBJECTIVITY SCORE'] = subjective_list
    data['AVG SENTENCE LENGTH'] = average_sentence_list
    data['PERCENTAGE OF COMPLEX WORDS'] = percentage_list
    data['FOG INDEX'] = fog_list
    print(len(all_links), len(urls), len(positive_list), len(negative_list), len(polarity_list), len(subjective_list),
          len(average_sentence_list), len(percentage_list), len(fog_list))
    # create a Pandas dataframe from the list
    df = pd.DataFrame(data, columns=['URL_ID', 'URL', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE',
                                     'SUBJECTIVITY SCORE', 'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS',
                                     'FOG INDEX'])

    # create an Excel writer object
    writer = pd.ExcelWriter('Output Data Structure.xlsx')

    # write the dataframe to the Excel file
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    # save the Excel file
    writer.save()
    writer.close()


# get_all_data_and_convert_it_into_excel_file()
get_title_and_article_text()
