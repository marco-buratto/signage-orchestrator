import re


class Lang:
    @staticmethod
    def stripQuotes(sentence: str) -> str:
        # Unquotes sentence.
        if sentence:
            sentence = sentence.strip()
            if re.search("^[\'\"].*[\'\"]$", sentence):
                sentence = sentence[1:-1]

        return sentence
