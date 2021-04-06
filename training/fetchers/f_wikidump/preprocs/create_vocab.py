import spacy

nlp = spacy.load("en_core_web_sm")

words = set()
for word in nlp.vocab.strings:
    words.add(word.lower())

with open('vocab_v1.txt', 'w') as f:
    for word in words:
        try:
            if word.isalpha():
                f.write(word+'\n')
        except Exception:
            pass