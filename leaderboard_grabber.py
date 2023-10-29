from tkinter import Tk


def grab_clipboard() -> []:
    a = Tk()
    cb = a.clipboard_get()
    a.destroy()
    return cb


def create_or_update(dictionary: {}, name: str, score: str, category: int):
    if name not in dictionary:
        dictionary[name] = ["0", "0", "0", "0", "0", "0", "0", "0", "0"]
    dictionary[name][category] = score


def process_clipboard(cb: str):
    scores = []
    temp = ""
    temp_count = 0
    clipboard = grab_clipboard()
    print(f"length of clipboard is {len(clipboard)}")
    clipboard_rows = clipboard.split("\n")
    for line in clipboard_rows:
        temp += line
        temp_count += 1
        # print(temp)
        if "%" in line[-2:]:
            scores.append(temp)
            temp = ""
            temp_count = 0
        if temp_count == 2:
            temp += "\t"
    return scores


def add_to_score_dict(scores: [], category: int):
    for score in scores:
        cols = score.split("\t")
        name = cols[1]
        score = cols[2]
        create_or_update(score_dict, name, score, category)


score_dict = {}
categories = ["Open Source Intelligence", "Cryptography", "Log Analysis", "Network traffic Analysis", "Forensics",
              "Scanning & Reconnaissance", "Enumeration & Exploitation", "Web Application Exploitation", "Password "
                                                                                                         "Cracking"]
print("Please open the leaderboard on cyber skyline and select the coach, and then each category.")
print("Each set of scores will need to be on the clipboard start with '1' at the top left.")
for i, category in enumerate(categories):
    print(" ")
    input(f"Please copy the {category} leaderboard \t press enter when ready")
    add_to_score_dict(process_clipboard(grab_clipboard()), i)

with open("leaderboards.csv", "w") as output:
    for student in score_dict:
        row = student + ","
        row += ",".join(score_dict[student])
        print(row)
        output.write(row)
