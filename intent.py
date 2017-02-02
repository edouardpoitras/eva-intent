import gossip
from eva_intent import EvaIntent

INTENT = EvaIntent()

@gossip.register('eva.post_boot', provides=['intent'])
def post_boot():
    gossip.trigger('eva.intent.ready_intent', intent=INTENT)
    INTENT.build()

@gossip.register('eva.pre_interaction', provides=['intent'])
def pre_interaction(context):
    context.intent = INTENT
    context.intent.compile_results(context.get_input_text())
