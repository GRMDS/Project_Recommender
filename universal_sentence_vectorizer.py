import tensorflow_hub as hub
from bs4 import BeautifulSoup
import numpy as np
import json


class ContentVectorizer:
    """ Vectorize content using Google's Universal Sentence Encoder """

    TITLE_WEIGHT = 0.7

    def __init__(self):
        self.__load_model()

    def __load_model(self):
        """ Load Google's Universal Sentence Encoder """
        module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
        self.model = hub.load(module_url)

    def encode_content(self, document):
        """ Static method to encode the project's title and description """
        # extract title and description
        title = np.array([document["title"]]) if document["title"] else document["title"]
        description = (
            np.array(
                [BeautifulSoup(document["description"], features="html5lib").get_text()]
            )
            if document["description"] is not None
            else document["description"]
        )

        # get title and description vector
        title_vec = self.model(title).numpy() if title is not None else np.zeros((1, 512))
        description_vec = (
            self.model(description).numpy()
            if description is not None
            else np.zeros((1, 512))
        )

        # weighted average of two vectors
        content_vec = (
            self.TITLE_WEIGHT * title_vec + (1 - self.TITLE_WEIGHT) * description_vec
        )
        return content_vec.reshape(-1)


if __name__ == "__main__":
    x = ContentVectorizer()
    results = x.encode_content({'title':'I am a superman!',"description":''})