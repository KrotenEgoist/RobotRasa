class IntentYamlGenerator:

    def __init__(self, intent_name, filename):
        self.filename = filename

        head = f'version: "3.1"\n\nnlu:\n- intent: {intent_name}\n  example: |\n'
        with open(self.filename, 'w') as file:
            file.write(head)

    def add(self, sentences):
        with open(self.filename, 'a') as file:
            for sent in sentences:
                text = f'    - {sent}\n'
                file.write(text)


if __name__ == '__main__':
    patrol = IntentYamlGenerator('patrol', 'intent_patrol.yml')
    patrol.add(['патрулируй', 'разведывай'])