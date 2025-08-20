from enum import Enum



class EFantasySpreadsheets(str, Enum):
    TEST = "TestDraft"
    DYNASTY2025 = "2025DynastyDraft"
    REDRAFT2025 = "2025RegularDraft"
    PLAYERS = "NFLPlayers"
    TIERS_2025 = "2025DraftTiers"

    def __str__(self):
        return self.value