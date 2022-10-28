import random
from typing import List

import TeamMember


class Team:
    def __init__(self, name: str, captain: str, team_members: List[TeamMember.TeamMember]):
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
        self.total = self.calculate_total()

    def get_members(self):
        return self.team_members

    def get_name(self):
        return self.name

    def get_captain(self):
        return self.captain

    def get_highest_category_score(self):
        #  Categories are:  0-osi,1-Crypto,2-Password,3-Log,4-Network,5-Forensics,6-Scanning,7-Web Apps,8-Enumeration
        highest_scores = [0] * 9
        for member in self.team_members:
            highest_scores[0] = max(highest_scores[0], member.osi)
            highest_scores[1] = max(highest_scores[1], member.crypto)
            highest_scores[2] = max(highest_scores[2], member.password)
            highest_scores[3] = max(highest_scores[3], member.log)
            highest_scores[4] = max(highest_scores[4], member.network)
            highest_scores[5] = max(highest_scores[5], member.forensics)
            highest_scores[6] = max(highest_scores[6], member.scanning)
            highest_scores[7] = max(highest_scores[7], member.web_apps)
            highest_scores[8] = max(highest_scores[8], member.enumeration)
        return highest_scores

    def get_random_member(self):
        member = random.choice(self.team_members)
        # not the captain
        while member == self.captain:
            member = random.choice(self.team_members)

        return random.choice(self.team_members)

