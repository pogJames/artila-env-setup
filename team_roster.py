# Team Roster Management System

class TeamMember:
    def __init__(self, name, role, favorite_language):
        self.name = name
        self.role = role
        self.favorite_language = favorite_language
    
    def introduce(self):
        return f"Hi! I'm {self.name}, a {self.role}. I love coding in {self.favorite_language}!"


# Team roster - Add yourself here!
team = [
    TeamMember("Alice Chen", "Senior Developer", "Python"),
    TeamMember("Bob Wang", "DevOps Engineer", "Go"),
    TeamMember("Carol Lin", "Frontend Developer", "JavaScript"),
    # TODO: Add your name below this line
    
]


def display_team():
    """Display all team members"""
    print("=" * 50)
    print("TEAM ROSTER")
    print("=" * 50)
    for member in team:
        print(member.introduce())
    print(f"\nTotal team members: {len(team)}")
    print("=" * 50)


def add_member(name, role, favorite_language):
    """Add a new team member"""
    new_member = TeamMember(name, role, favorite_language)
    team.append(new_member)
    print(f"Welcome {name} to the team!")


def find_member(name):
    """Find a team member by name"""
    for member in team:
        if member.name.lower() == name.lower():
            return member
    return None


# Main execution
if __name__ == "__main__":
    display_team()
    
    # Example: Uncomment to add yourself
    # add_member("Your Name", "Intern", "Python")
    # display_team()
