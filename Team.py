import TeamMember

class Team:
    def __init__(self, name: str, captain: str, team_members: list):
        self.name = name
        self.captain = captain
        self.team_members = team_members
        self.total = self.calculate_total()

    def calculate_total(self):
        total = 0
        for this_person in self.team_members:
            total += getattr(this_person, 'total')
        return total

    def add_team_member(self, new_member: TeamMember):
        self.team_members.append(new_member)

    def get_members(self):
        return self.team_members