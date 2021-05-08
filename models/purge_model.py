import warnings, os
import numpy as np
from AssociationModels import PosTaggedModel, BasicModel
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    import gensim
    from gensim.models.keyedvectors import KeyedVectors

model_folder = '82'
model_name = 'model.bin'
binary = True
dict_name = 'word_dict.txt'

def restrict_w2v(w2v, restricted_word_set):
    new_vectors = []
    new_vocab = {}
    new_index2entity = []

    for i in range(len(w2v.vocab)):
        word = w2v.index2entity[i]
        vec = w2v.vectors[i]
        vocab = w2v.vocab[word]
        if word in restricted_word_set:
            vocab.index = len(new_index2entity)
            new_index2entity.append(word)
            new_vocab[word] = vocab
            new_vectors.append(vec)

    w2v.vocab = new_vocab
    w2v.vectors = np.asarray(new_vectors)
    w2v.index2entity = np.asarray(new_index2entity)
    w2v.index2word = np.asarray(new_index2entity)

def main():
    word_dict = set()
    with open(dict_name) as f_in:
        word_dict.update([w.split(' ')[0] for w in f_in.read().split('\n') if len(w.split(' ')) > 0])
    print(f'loaded in {len(word_dict)} words from dict')

    # pos_tagged_model = PosTaggedModel(model_folder, purge_tags_to=-1, remove_capitals=False, prefix='.')
    pos_tagged_model = BasicModel(model_folder, binary=True, name='model.bin', prefix='.')
    tag_dict = set()
    for word in word_dict:
        tag_dict.update(pos_tagged_model.get_tags(word))
    print(f'found {len(tag_dict)} unique tags in model')

    restrict_w2v(pos_tagged_model.model, tag_dict)
    print(f'purged down to {len(pos_tagged_model.model.vocab)} words')
    if not os.path.exists(f'./{model_folder}_purged'):
        os.makedirs(f'./{model_folder}_purged')
    pos_tagged_model.model.save_word2vec_format(f'./{model_folder}_purged/{model_name}', binary=True)

if __name__ == '__main__':
    main()