# data is assumed to be in the following format
# Discord Handle,OSI,Crypto,Password,Log,Network,Forensics,Scanning,Web Apps,Enumeration
# *note if upgrading to Python 3.9 or later change type hints from List to list
import math
import statistics
from typing import List
import display
import Team
import TeamMember


def load_scores():
    score_list = []
    skip_columns = 2
    with open("resources/NCLscores.csv", "r") as score_file:
        score_file.readline()  # this skips the column headers
        for line in score_file:
            row = line.rstrip("\n").split(",")
            score_list.append(row[skip_columns:])
        return score_list


def load_pre_selections(all_scores):
    #  Team name,Discord Handle,Team Lead
    max_team_size = 7
    teams = []
    with open("resources/Team_leads_and_partial_teams.csv", "r") as partials:
        partials.readline()
        for line in partials:
            row = line.rstrip("\n").split(",")
            team_name = row[0]
            captain = row[1]
            score = row_from_scores_by_name(captain, all_scores)
            team_member = TeamMember.TeamMember(score)
            # if this is a captain create the team else add this person to existing team
            if row[2].lower() == "true":
                teams.append(Team.Team(team_name, captain, [team_member]))
            else:
                # add this person to the right team
                for this_team in teams:
                    if this_team.name == team_name:
                        this_team.add_team_member(team_member)

    #  we need to add additional teams here if the number of teams is less than ceil(len(all_scores)/max_team_size
    required_team_count = int(math.ceil(len(all_scores)/max_team_size))
    should_add = required_team_count - len(teams)
    while should_add > 0:
        teams.append(Team.Team("Bonus Team " + str(len(teams) + 1), "TBD", []))
        should_add -= 1
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


def average_scores(score_list: List[List[int]]) -> List[int]:
    return [statistics.mean(row) for row in transpose_matrix(score_list)]


def total_scores(score_list: List[List[int]]) -> List[int]:
    return [sum(row) for row in transpose_matrix(score_list)]


def standard_deviation(score_list: List[List[int]]) -> List[int]:
    return [statistics.stdev(row) for row in transpose_matrix(score_list)]


def already_on_team(team_roster: List[Team.Team]) -> List[str]:
    return [this_member.get_name() for this_team in team_roster for this_member in this_team.team_members]


def get_low_score_team(this_roster: List[Team.Team]) -> Team.Team:
    lowest_team = this_roster[0]
    for this_team in this_roster:
        if this_team.total < lowest_team.total:
            lowest_team = this_team
    return lowest_team


def greedy_team_selection(score_list, team_roster):
    remaining_players = [p for p in score_list if p[0] not in already_on_team(team_roster)]
    remaining_team_members = [TeamMember.TeamMember(t) for t in remaining_players]
    sorted_remaining_players = sorted(remaining_team_members, key=lambda x: x.total, reverse=True)
    while sorted_remaining_players:
        lowest_team = get_low_score_team(team_roster)
        top_player_available = sorted_remaining_players.pop(0)
        lowest_team.add_team_member(top_player_available)
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

    #  the code below shows overall numbers
    names, score_matrix = matrix_from_lists(scores)
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

    column_names = ["discord handle", 'OSI', 'Crypto', 'Password', 'Log', 'Network', 'Forensics', 'Scanning',
                    'Web Apps', 'Enumeration']
    column_widths = [20, 9, 9, 9, 9, 9, 9, 9, 9, 9]

    display.clear_screen()
    display.down(5)
    display.ascii_wguncl_colored()
    display.down(5)
    display.table(scores, column_names, column_widths)
    print()
    print()

    high_score_matrix = []
    for team in roster:
        highest_per_category = [team.name + " " + str(team.total)]
        for score in team.get_highest_category_score():
            highest_per_category.append(score)
        high_score_matrix.append(highest_per_category)
    display.table(high_score_matrix, column_names, column_widths)
    print()
    print()

