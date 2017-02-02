from operator import itemgetter
from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine

class EvaIntent(object):
    """
    Wrapper around the adapt intent engine.
    """
    def __init__(self):
        self.engine = IntentDeterminationEngine()
        self.results = []
        self.entities = {}

    def add_option(self, intent_name, entity_name, value=None, required=True):
        """
        Method used to add parser values to the intent engine.
        """
        if intent_name not in self.entities:
            # New intent_name, a new plugin is adding some intents.
            self.entities[intent_name] = {}
        if entity_name not in self.entities[intent_name]:
            if value is None:
                # Assume regex is not value is provided.
                self.entities[intent_name][entity_name] = {'required': required}
            else:
                # First time adding value to this entity_name.
                self.entities[intent_name][entity_name] = {'values': [value],
                                                           'required': required}
        else:
            # Already have values on this entity_name, add this one as well.
            self.entities[intent_name][entity_name]['values'].append(value)
            # Updated the required value in case it's being overriden.
            self.entities[intent_name][entity_name]['required'] = required

    def build(self):
        """
        Builds out all the options specified and compiles them into the intent
        engine.
        """
        for intent_name, entities in self.entities.items():
            new_intent = IntentBuilder(intent_name)
            for entity_name, data in entities.items():
                # If regex entity.
                if 'values' not in data:
                    self.engine.register_regex_entity(entity_name)
                    # Parse out name in regex (assume between < and >).
                    keyword = entity_name.split('<')[1].split('>')[0]
                    if data['required']:
                        new_intent = new_intent.require(keyword)
                    else:
                        new_intent = new_intent.optionally(keyword)
                else:
                    for value in data['values']:
                        self.engine.register_entity(value, entity_name)
                    if data['required']:
                        new_intent = new_intent.require(entity_name)
                    else:
                        new_intent = new_intent.optionally(entity_name)
            new_intent = new_intent.build()
            self.engine.register_intent_parser(new_intent)

    def compile_results(self, text):
        """
        Feed the input_text to the intent engine and order the results by
        confidence.
        """
        results = []
        for intent in self.engine.determine_intent(text):
            results.append(intent)
        # Sort by confidence, descending.
        self.results = sorted(results,
                              key=itemgetter('confidence'),
                              reverse=True)

    def best_intent(self):
        """
        Returns the intent with the highest confidence.
        """
        if len(self.results) > 0:
            return self.results[0]
        return None

    def all_intents(self):
        """
        Returns all intents found by the intent engine.
        """
        return self.results
