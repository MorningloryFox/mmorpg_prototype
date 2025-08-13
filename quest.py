class Quest:
    def __init__(self, quest_id, description, goal):
        self.id = quest_id
        self.description = description
        self.goal = goal
        self.completed = False


class QuestManager:
    def __init__(self):
        self.quests = {}

    def add_quest(self, quest: Quest):
        self.quests[quest.id] = quest

    def complete(self, quest_id: str):
        if quest_id in self.quests:
            self.quests[quest_id].completed = True

    def to_dict(self):
        return {qid: q.completed for qid, q in self.quests.items()}

    def load_from_dict(self, data):
        for qid, completed in data.items():
            self.quests[qid] = Quest(qid, "", 0)
            self.quests[qid].completed = completed
