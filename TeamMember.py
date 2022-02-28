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