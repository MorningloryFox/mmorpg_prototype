"""Simple event triggers based on player position."""

MAP_EVENTS = {
    # map of (x, y) tile -> quest to complete
    (5, 5): {'quest_complete': 'intro'}
}


def check_events(player, quest_manager):
    tile = (player.rect.x // 32, player.rect.y // 32)
    event = MAP_EVENTS.get(tile)
    if not event:
        return
    quest_id = event.get('quest_complete')
    if quest_id:
        quest_manager.complete(quest_id)
