# data is assumed to be in the following format
# Discord Handle,OSI,Crypto,Password,Log,Network,Forensics,Scanning,Web Apps,Enumeration
# *note if upgrading to Python 3.9 or later change type hints from List to list

import statistics
from typing import List

import display


class TeamMember:
    def __init__(self, args):
        self.name = args[0]
        self.osi = int(args[1])
        self.crypto = int(args[2])
        self.password = int(args[3])
        self.log = int(args[4])
        self.network = int(args[5])
        self.forensics = int(args[6])
        self.scanning = int(args[7])
        self.web_apps = int(args[8])
        self.enumeration = int(args[9])
        self.total = int(args[1]) + int(args[2]) + int(args[3]) + int(args[4]) + int(args[5]) + int(args[6]) + \
                     int(args[7]) + int(args[8]) + int(args[9])

    def get_name(self):
        return self.name


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


def load_scores():
    score_list = []
    skip_columns = 2
    with open("resources/NCLscores.csv", "r") as score_file:
        score_file.readline()  # this skips the column headers
        for line in score_file:
            row = line.rstrip("\n").split(",")
            score_list.append(row[skip_columns:])
        return score_list


def load_pre_selections(scores):
    #  Team name,Discord Handle,Team Lead
    max_team_size = 7
    teams = []
    with open("resources/Team_leads_and_partial_teams.csv", "r") as partials:
        partials.readline()
        for line in partials:
            row = line.rstrip("\n").split(",")
            team_name = row[0]
            captain = row[1]
            score = row_from_scores_by_name(captain, scores)
            team_member = TeamMember(score)
            # if this is a captain create the team else add this person to existing team
            if row[2].lower() == "true":
                teams.append(Team(team_name, captain, [team_member]))
            else:
                # add this person to the right team
                for team in teams:
                    if team.name == team_name:
                        team.add_team_member(team_member)

    return teams


def matrix_get_row(i: int, score_list: List[List[str]]) -> List[int]:
    #  returns a single row from 2d list
    this_list = []
    for entry in score_list:
        this_list.append(int(entry[i]))
    return this_list


def row_from_scores_by_name(name, score_list):
    for row in score_list:
        if name in row:
            return row
    return ["Not Found"]


def matrix_from_lists(score_list: List[List[str]]):
    #  returns a list of discord names, and 2d list of scores. row index matches name index
    #  The 2d list of scores is used to find totals, and averages for each category
    number_of_scores = 9
    discord_names = []
    name_offset = 0
    matrix = [[0] * number_of_scores for _ in range(len(score_list))]
    for i, entry in enumerate(score_list):
        for j in range(10):
            if j > name_offset:
                this_item = int(entry[j])
                matrix[i][j - 1] = this_item
            else:
                discord_names.append(entry[j])
    return discord_names, matrix


def transpose_matrix(score_list: List[List[int]]):
    #  change columns to rows, only use the int values not the names
    return list(map(list, zip(*score_list)))


def average_scores(score_list: List[List[int]]):
    flipped = transpose_matrix(score_list)
    averages = []
    for row in flipped:
        averages.append(statistics.mean(row))
    return averages


def total_scores(score_list: List[List[int]]):
    flipped = transpose_matrix(score_list)
    totals = []
    for row in flipped:
        totals.append(sum(row))
    return totals


def standard_deviation(score_list: List[List[int]]):
    flipped = transpose_matrix(score_list)
    deviations = []
    for row in flipped:
        deviations.append(statistics.stdev(row))
    return deviations


def already_on_team(team_roster: List[Team]) -> List[str]:
    name_list = []
    for this_team in team_roster:
        for this_member in this_team.get_members():
            name_list.append(this_member.get_name())
    return name_list


def get_low_score_team(roster: List[Team]) -> Team:
    lowest_team = roster[0]
    for this_team in roster:
        if this_team.total < lowest_team.total:
            lowest_team = this_team
    return lowest_team


def greedy_team_selection(score_list, team_roster):
    #  new list remove players already on a team
    remaining_players = [p for p in score_list if p[0] not in already_on_team(team_roster)]
    # create TeamMember objects from list
    remaining_team_members = [TeamMember(t) for t in remaining_players]
    #  sort remaining players by total score
    sorted_remaining_players = sorted(remaining_team_members, key=lambda x: x.total, reverse=True)
    #  add the highest scoring available player to team with the least total points
    while sorted_remaining_players:
        #  find team with the lowest total score
        lowest_team = get_low_score_team(team_roster)
        #  add the highest scoring player in sorted list to that team
        player = sorted_remaining_players.pop(0)
        #  print(player.name, player.total)
        lowest_team.add_team_member(player)
        lowest_team.total = lowest_team.calculate_total()

    return sorted_remaining_players


if __name__ == '__main__':

    scores = load_scores()
    roster = load_pre_selections(scores)
    been_chosen = already_on_team(roster)
    #  print(been_chosen)

    roster_initial = greedy_team_selection(scores, roster)
    #  create a 2 column table with team.name,total.points : captian,captain.name : name,points
    for team in roster:
        column_names = [team.name + "  " + str(team.total), "Captain: " + team.captain]
        column_widths = [20, 20]
        table_data = []
        for member in team.team_members:
            table_data.append([member.name, member.total])
            # print(f"\t\t\t{member.name}{' ' * (15 - len(member.name))}{member.total}")
        display.table(table_data, column_names, column_widths)

    '''  #  the code below shows overall numbers
    
    #  totals
    totals = ["   Totals"]
    totals += total_scores(score_matrix)
    scores.append(totals)

    #  average
    average = ["   Average"]
    average += average_scores(score_matrix)
    scores.append(average)

    #  standard deviation
    deviation = ["   Deviation"]
    deviation += standard_deviation(score_matrix)
    scores.append(deviation)
    names, score_matrix = matrix_from_lists(scores)

    column_names = ["discord handle", 'OSI', 'Crypto', 'Password', 'Log', 'Network', 'Forensics', 'Scanning',
                    'Web Apps', 'Enumeration']
    column_widths = [14, 9, 9, 9, 9, 9, 9, 9, 9, 9]

    display.clear_screen()
    display.down(5)
    display.ascii_wguncl_colored()
    display.down(5)
    display.table(scores, column_names, column_widths)
    display.down(15)

    column_names = ["discord handle", 'OSI', 'Crypto', 'Password', 'Log', 'Network', 'Forensics', 'Scanning',
                    'Web Apps', 'Enumeration']
    column_widths = [14, 9, 9, 9, 9, 9, 9, 9, 9, 9]

    display.clear_screen()
    display.down(5)
    display.ascii_wguncl_colored()
    display.down(5)
    display.table(scores, column_names, column_widths)
    print()
    print()
    '''
