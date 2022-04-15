# data is assumed to be in the following format
# Discord Handle,OSI,Crypto,Password,Log,Network,Forensics,Scanning,Web Apps,Enumeration
# *note if upgrading to Python 3.9 or later change type hints from List to list
import math
import os
import statistics
from os.path import exists
from typing import List
import display
import Team
import TeamMember


def load_scores():
    score_list = []
    skip_columns = 2
    with open(scores_file, "r") as score_file:
        score_file.readline()  # this skips the column headers
        for line in score_file:
            row = line.rstrip("\n").split(",")
            score_list.append(row[skip_columns:])
        return score_list


def load_pre_selections(all_scores):
    #  Team name,Discord Handle,Team Lead
    max_team_size = 7
    teams = []
    with open(captains_file, "r") as partials:
        partials.readline()  # read headers
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
    required_team_count = int(math.ceil(len(all_scores) / max_team_size))
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
    return [int(statistics.mean(row)) for row in transpose_matrix(score_list)]


def total_scores(score_list: List[List[int]]) -> List[int]:
    return [sum(row) for row in transpose_matrix(score_list)]


def standard_deviation(score_list: List[List[int]]) -> List[int]:
    return [int(statistics.stdev(row)) for row in transpose_matrix(score_list)]


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


def display_teams(full_roster):
    display.clear_screen()
    print()
    print()
    for team in full_roster:
        column_names = [team.name + "  " + str(team.total), "Captain: " + team.captain]
        column_widths = [40, 20]
        table_data = []
        for member in team.team_members:
            table_data.append([member.name, member.total])
        display.table(table_data, column_names, column_widths)
        print()
        print()
    input("press enter to return to menu  . . .")


def display_players(all_scores):
    #  separate the names from the score data
    names, score_matrix = matrix_from_lists(all_scores)

    #  totals
    totals = ["   Totals"]
    totals += total_scores(score_matrix)
    all_scores.append(totals)

    #  average
    average = ["   Average"]
    average += average_scores(score_matrix)
    all_scores.append(average)

    #  standard deviation
    deviation = ["   Deviation"]
    deviation += standard_deviation(score_matrix)
    all_scores.append(deviation)

    display.clear_screen()
    print()
    print()
    display.table(all_scores, column_names, column_widths)
    print()
    print()
    input("press enter to return to menu . . .")


def display_menu():
    display.clear_screen()
    display.ascii_wguncl_colored()
    print()
    print()
    display.main_menu()
    display.up(2)
    display.left(30)
    choice = input("Choose option > ")

    return choice


def display_team_module_score(full_roster):
    display.clear_screen()
    print()
    print()
    high_score_matrix = []
    for team in full_roster:
        highest_per_category = [team.name + " " + str(team.total)]
        for score in team.get_highest_category_score():
            highest_per_category.append(score)
        high_score_matrix.append(highest_per_category)
    display.table(high_score_matrix, column_names, column_widths)
    print()
    print()
    input("press enter to return to menu . . .")


def save_teams(this_roster):
    output = "Team name,Discord Handle,Team Lead"
    for team in this_roster:
        for member in team.get_members():
            output += team.get_name() + "," + member.get_name() + ", " + str(
                team.get_captain() == member.get_name()) + "\n"

    with open(save_file, "w") as output_file:
        output_file.write(output)
    print("The teams have been saved to ", save_file)
    input("press enter to return to menu . . .")


if __name__ == '__main__':
    if os.name == "nt":
        display.setup_windows_console()

    # files
    captains_file = "resources/Team_leads_and_partial_teams.csv"
    scores_file = "resources/NCLscores.csv"
    save_file = "resources/saved_teams.csv"

    # columns
    column_names = ["discord handle", 'OSI', 'Crypto', 'Password', 'Log', 'Network', 'Forensics', 'Scanning',
                    'Web Apps', 'Enumeration']
    column_widths = [20, 9, 9, 9, 9, 9, 9, 9, 9, 9]

    # load files
    next_screen = 0
    scores = load_scores()
    if exists(save_file):
        load_saved = input("Would you like to load saved teams Y/N")
        if load_saved == "Y" or load_saved == "y":
            captains_file = save_file

    roster = load_pre_selections(scores)
    been_chosen = already_on_team(roster)

    #  choose teams
    roster_initial = greedy_team_selection(scores, roster)

    while next_screen != "5":
        next_screen = display_menu()
        if next_screen == "1":
            display_players(scores)
        if next_screen == "2":
            display_teams(roster)
        if next_screen == "3":
            display_team_module_score(roster)
        if next_screen == "4":
            save_teams(roster)
    print(display.Colors.reset)
