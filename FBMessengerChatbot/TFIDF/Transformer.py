import numpy as np
import pandas as pd
from FBMessengerChatbot.TFIDF.PreProcessing import text_process, lem

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Transformer:
    def __init__(self, file):
        """
        initialize corpus, BoW and TFIDF from file
        """
        self.FAQ = pd.read_csv(file, keep_default_na=False, encoding='iso-8859-1')
        self.questions = self.FAQ.question
        self.answers = self.FAQ.answer
        self.corpus = self.FAQ.question + ' ' + self.FAQ.answer
        # for questions
        self.question_BoW_transformer = CountVectorizer(analyzer=text_process).fit(self.questions)
        self.question_BoW = self.question_BoW_transformer.transform(self.questions)
        self.question_tfidf_transformer = TfidfTransformer().fit(self.question_BoW)
        self.question_tfidf = self.question_tfidf_transformer.transform(self.question_BoW)
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
        return (index, similarity value) of string argument query which is most similar
        :param query:
        :return:
        """
        # for questions
        question_query_BoW = self.question_BoW_transformer.transform([query])
        question_query_tfidf = self.question_tfidf_transformer.transform(question_query_BoW)
        # for answers
        answer_query_BoW = self.answer_BoW_transformer.transform([query])
        answer_query_tfidf = self.answer_tfidf_transformer.transform(answer_query_BoW)
        # for corpus
        corpus_query_BoW = self.corpus_BoW_transformer.transform([query])
        corpus_query_tfidf = self.corpus_tfidf_transformer.transform(corpus_query_BoW)

        answer_similarities = np.transpose(cosine_similarity(answer_query_tfidf, self.answer_tfidf))
        question_similarities = np.transpose(cosine_similarity(question_query_tfidf, self.question_tfidf))
        corpus_similarities = np.transpose(cosine_similarity(corpus_query_tfidf, self.corpus_tfidf))

        answer_max_similarity = answer_similarities.max()
        answer_max_index = np.argmax(answer_similarities)

        question_max_similarity = question_similarities.max()
        quesiton_max_index = np.argmax(question_similarities)

        corpus_max_similarity = corpus_similarities.max()
        corpus_max_index = np.argmax(corpus_similarities)

        index_dict = {answer_max_similarity: answer_max_index,
                      question_max_similarity: quesiton_max_index,
                      corpus_max_similarity: corpus_max_index}
        _max = max([answer_max_similarity, question_max_similarity, corpus_max_similarity])
        return index_dict[_max], _max

    def match_query(self, query):
        """
        Return most similar match in FAQ to user query
        :param query:
        :return:
        """
        index, similarity = self.tfidf_similarity(query)
        response = self.FAQ.answer.iloc[index]

        return response
