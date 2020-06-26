import numpy as np
import pandas as pd
from FBMessengerChatbot.TFIDF.PreProcessing import text_process, lem

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Transformer:
    def __init__(self, englishFile, simplifiedChineseFile, traditionalChineseFile, spanishFile):
        """
        initialize corpus, BoW and TFIDF from file
        """
        English_FAQ = pd.read_csv(englishFile, keep_default_na=False, encoding='cp1252')
        Spanish_FAQ = pd.read_csv(spanishFile, keep_default_na=False, encoding='cp1252')
        simplifiedChinese_FAQ = pd.read_csv(simplifiedChineseFile, keep_default_na=False, encoding='utf-16')

        # with open(simplifiedChineseFile, 'rb') as f:
        #     simplifiedChinese_FAQ = f.read()
        # simplifiedChinese_FAQ  = simplifiedChinese_FAQ .decode("utf-16").encode('gb18030')
        # with open(traditionalChineseFile, 'rb') as f:
        #     traditionalChinese_FAQ = f.read()
        # traditionalChinese_FAQ  = traditionalChinese_FAQ .decode("utf-16").encode('big5hkscs')
        # traditionalChinese_FAQ  = traditionalChinese_FAQ .split("\r\n")
        # for i in range(1, len(traditionalChinese_FAQ)):
        #     traditionalChinese_FAQ[i] = traditionalChinese_FAQ[i].strip()
        #     traditionalChinese_FAQ[i] = traditionalChinese_FAQ[i].split('\t')
        # del simplifiedChinese_FAQ[0]
        # del traditionalChinese_FAQ[0]
        # simplifiedChinese_FAQ = pd.DataFrame(simplifiedChinese_FAQ, columns=['question', 'answer'])
        # traditionalChinese_FAQ = pd.DataFrame(traditionalChinese_FAQ, columns=['question', 'answer'])
        self.FAQ = pd.concat([English_FAQ, simplifiedChinese_FAQ, Spanish_FAQ], ignore_index=True)
        self.questions = self.FAQ.question
        self.answers = self.FAQ.answer
        self.corpus = self.FAQ.question + ' ' + self.FAQ.answer

        # impute
        self.questions, self.answers, self.corpus = self.questions.fillna(' '), self.answers.fillna(' '), self.corpus.fillna(' ')

        # for questions
        self.question_BoW_transformer = CountVectorizer(analyzer=text_process).fit(self.questions)
        self.question_BoW = self.question_BoW_transformer.transform(self.questions) # count the number of each word appearing in the questions
        self.question_tfidf_transformer = TfidfTransformer().fit(self.question_BoW)
        self.question_tfidf = self.question_tfidf_transformer.transform(self.question_BoW) # calculate the TF/IDF of each word
        # for answers
        self.answer_BoW_transformer = CountVectorizer(analyzer=text_process).fit(self.answers)
        self.answer_BoW = self.answer_BoW_transformer.transform(self.answers)
        self.answer_tfidf_transformer = TfidfTransformer().fit(self.answer_BoW)
        self.answer_tfidf = self.answer_tfidf_transformer.transform(self.answer_BoW)
        # for corpus
        self.corpus_BoW_transformer = CountVectorizer(analyzer=text_process).fit(self.corpus)
        self.corpus_BoW = self.corpus_BoW_transformer.transform(self.corpus)
        self.corpus_tfidf_transformer = TfidfTransformer().fit(self.corpus_BoW)
        self.corpus_tfidf = self.corpus_tfidf_transformer.transform(self.corpus_BoW)

    def tfidf_similarity(self, query):
        """
        Three circumstances we assume:
        1. the query is similar to an existing question in the pool
        2. the query is similar to an existing answer in the pool
        3. the query is similar to an existing pair of Q&A in the pool
        return (index, similarity value) of string argument query which is most similar
        :param query: the question asked from a user
        :return: index of the answer that is supposed to be retrieved & the similarity value of the answer
        """
        # circumstance No.1
        question_query_BoW = self.question_BoW_transformer.transform([query])
        question_query_tfidf = self.question_tfidf_transformer.transform(question_query_BoW)
        # circumstance No.2
        answer_query_BoW = self.answer_BoW_transformer.transform([query])
        answer_query_tfidf = self.answer_tfidf_transformer.transform(answer_query_BoW)
        # circumstance No.3
        corpus_query_BoW = self.corpus_BoW_transformer.transform([query])
        corpus_query_tfidf = self.corpus_tfidf_transformer.transform(corpus_query_BoW)

        # calculate all similarities in three circumstances
        answer_similarities = np.transpose(cosine_similarity(answer_query_tfidf, self.answer_tfidf))
        question_similarities = np.transpose(cosine_similarity(question_query_tfidf, self.question_tfidf))
        corpus_similarities = np.transpose(cosine_similarity(corpus_query_tfidf, self.corpus_tfidf))

        # obtain the max of answer similarity
        answer_max_similarity = answer_similarities.max()
        answer_max_index = np.argmax(answer_similarities)

        # obtain the max of question similarity
        question_max_similarity = question_similarities.max()
        quesiton_max_index = np.argmax(question_similarities)

        # obtain the max of Q&A pair similarity
        corpus_max_similarity = corpus_similarities.max()
        corpus_max_index = np.argmax(corpus_similarities)

        index_dict = {answer_max_similarity: answer_max_index,
                      question_max_similarity: quesiton_max_index,
                      corpus_max_similarity: corpus_max_index}

        # get the most similar one (the largest value of the three above)
        _max = max([answer_max_similarity, question_max_similarity, corpus_max_similarity])
        return index_dict[_max], _max

    def match_query(self, query):
        """
        Return most similar match in FAQ to user query
        :param query: question asked by a user
        :return: response: corresponding answer & its similarity value
        """
        index, similarity = self.tfidf_similarity(query)
        response = self.FAQ.answer.iloc[index]
        return response, similarity
