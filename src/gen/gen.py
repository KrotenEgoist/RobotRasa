import re
import random
import pymorphy2


morph = pymorphy2.MorphAnalyzer()

dictionary = {
    "robot": ["Робот|excl", ],
    "action": ["идти", "двигаться"],
    "to": ["к|datv", "до|gent"],
    "object": ["дом", "дерево", "камень"],
    "relation": ["около|gent", "позади|gent", "перед|ablt"]
}


sample = '[robot] [action] [to] [object] [relation] [object]'
general_pattern = re.compile(r'\w+')

subjects = general_pattern.findall(sample)

sentence = []

case = None
for i in subjects:
    sub = random.choice(dictionary[i])

    try:
        word, case = general_pattern.findall(sub)
    except ValueError:
        word, case = general_pattern.search(sub).group(), None



# text = ' '.join(sentence)
#
# print(text)
