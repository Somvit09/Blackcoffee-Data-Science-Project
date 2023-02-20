import pandas as pd
import requests
import bs4


def get_title_and_article_text():
    read_xl = pd.read_excel('Input.xlsx')
    data = {}
    for i in read_xl['URL']:
        response = requests.get(i)
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        if soup.find('h1', class_='entry-title') and soup.find('div', class_='td-post-content') is not None:
            title = soup.find('h1', class_='entry-title').text.strip()
            content = soup.find('div', class_='td-post-content').text
            data[title] = content.replace('\n', '')
        else:
            pass
    return data


def store_data_to_excel_file():
    # create a Pandas dataframe from the dictionary
    df = pd.DataFrame.from_dict(get_title_and_article_text(), orient='index', columns=['Value'])

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






negative_words_identification()

