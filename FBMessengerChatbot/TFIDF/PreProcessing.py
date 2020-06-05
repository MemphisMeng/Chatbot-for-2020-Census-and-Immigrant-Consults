import string
from nltk.stem import WordNetLemmatizer


def lem(words):
    """
    Return a list of lemmas from word list
    :param words: list
    :return: lem_sentence (list)
    """
    wordnet_lemmatizer = WordNetLemmatizer()
    lem_sentence = []
    for word in words:
        lem_sentence.append(wordnet_lemmatizer.lemmatize(word))
    return lem_sentence


def text_process(mess, lemmas=True):
    """
    Return a list of tokens in mess (string), without punctuations
    :param mess:
    :param lemmas: True when we need to lemmatize words
    :return: tokenized list
    """
    clean = [punc if punc not in string.punctuation else ' ' for punc in mess]
    clean = ''.join(clean)
    clean = [word.lower() for word in clean.split()]
    return clean