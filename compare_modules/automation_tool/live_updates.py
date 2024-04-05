from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_updates(owner, armies):
    message = owner + " has " + str(armies) + " to deploy"
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('updates',
    {
        'type': 'updates',
        'message': "event_trigered_from_views"
    })