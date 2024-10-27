import curses
import datetime
import webbrowser
from typing import List, Optional, Tuple
from beeminder import BeeminderAPI
from models import BeeminderGoal



class InputWindow:
    """Helper class to manage input prompts"""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        height, width = stdscr.getmaxyx()
        # Create a small window in the middle of the screen
        self.window = curses.newwin(6, 60, height // 2 - 3, width // 2 - 30)
        self.window.keypad(1)

    def get_input(self, prompt: str, numeric: bool = False) -> Tuple[bool, str]:
        """
        Show an input prompt and return the user's input
        Returns (success, input_value)
        """
        self.window.clear()
        self.window.box()
        self.window.addstr(1, 2, prompt)
        self.window.addstr(2, 2, "→ ")
        self.window.addstr(4, 2, "Enter to submit, Esc to cancel")

        curses.echo()
        curses.curs_set(1)

        input_str = ""
        cur_x = 4

        while True:
            self.window.refresh()
            try:
                char = self.window.getch(2, cur_x)
            except KeyboardInterrupt:
                return False, ""

            if char == 27:  # Escape
                return False, ""
            elif char == 10:  # Enter
                if numeric:
                    try:
                        float(input_str)
                        return True, input_str
                    except ValueError:
                        self.window.addstr(4, 2, "Invalid number! Press any key...")
                        self.window.getch()
                        self.window.addstr(4, 2, "Enter to submit, Esc to cancel")
                        continue
                return True, input_str
            elif char == curses.KEY_BACKSPACE or char == 127:
                if input_str:
                    input_str = input_str[:-1]
                    cur_x -= 1
                    self.window.addch(2, cur_x, ' ')
                    self.window.move(2, cur_x)
            elif numeric and not (chr(char).isdigit() or char == ord('.')):
                continue
            elif 32 <= char <= 126:  # Printable characters
                input_str += chr(char)
                self.window.addch(2, cur_x, char)
                cur_x += 1

        curses.noecho()
        curses.curs_set(0)
        return False, ""


class BeeminderCLI:
    def __init__(self, api_key: str, username: Optional[str] = None):
        self.api = BeeminderAPI(api_key=api_key, default_user=username)
        self.username = username
        self.goals: List[BeeminderGoal] = []
        self.selected_index = 0
        self.offset = 0
        self.header = ["Slug", "Description", "Current", "Goal", "Lose Date", "Time Left", "Last Updated", "Status"]
        self.col_widths = [15, 25, 10, 10, 20, 15, 20, 10]
        self.view_mode = "list"  # "list" or "detail"
        self.detail_offset = 0
        self.current_goal_detail = None

    def open_in_browser(self):
        """Open the Beeminder dashboard in the default web browser"""
        if self.username:
            url = f"https://www.beeminder.com/{self.username}"
            webbrowser.open(url)

    def fetch_goals(self):
        """Fetch all goals from Beeminder API"""
        self.goals = self.api.get_all_goals(None)

    def fetch_goal_detail(self, goal_slug: str):
        """Fetch detailed information for a specific goal"""
        self.current_goal_detail = self.api.get_goal(None, goal_slug, datapoints=False)

    def format_date(self, timestamp: Optional[int]) -> str:
        """Convert Unix timestamp to human readable date"""
        if timestamp is None:
            return "N/A"
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

    def format_time_left(self, losedate: Optional[int]) -> str:
        """Calculate and format time remaining until losedate"""
        if losedate is None:
            return "N/A"
        now = datetime.datetime.now()
        lose_time = datetime.datetime.fromtimestamp(losedate)
        time_left = lose_time - now

        if time_left.total_seconds() < 0:
            return "EXPIRED"

        days = time_left.days
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60

        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def get_goal_status(self, goal: BeeminderGoal) -> str:
        """Determine the status of a goal"""
        if goal.lost:
            return "LOST"
        if goal.won:
            return "WON"
        if goal.frozen:
            return "FROZEN"
        return "ACTIVE"

    def draw_header(self, stdscr, start_y: int):
        """Draw the table header"""
        x = 2
        for idx, (title, width) in enumerate(zip(self.header, self.col_widths)):
            stdscr.attron(curses.A_BOLD)
            stdscr.addstr(start_y, x, title.ljust(width))
            stdscr.attroff(curses.A_BOLD)
            x += width + 2

    def truncate_text(self, text: Optional[str], width: int) -> str:
        """Truncate text to fit within width, adding ellipsis if needed"""
        if not text:
            return "".ljust(width)
        if len(text) <= width:
            return text.ljust(width)
        return (text[:width - 3] + "...").ljust(width)

    def draw_goals_list(self, stdscr):
        """Draw the goals table"""
        height, width = stdscr.getmaxyx()
        visible_rows = height - 4  # Account for header and borders

        # Draw header
        self.draw_header(stdscr, 1)

        # Draw separator line
        stdscr.addstr(2, 1, "─" * (width - 2))

        # Draw goals
        for idx, goal in enumerate(self.goals[self.offset:self.offset + visible_rows]):
            y = idx + 3
            if y >= height:
                break

            # Highlight selected row
            if idx + self.offset == self.selected_index:
                stdscr.attron(curses.A_REVERSE)

            # Format goal data
            goal_data = [
                self.truncate_text(goal.slug, self.col_widths[0]),
                self.truncate_text(goal.title, self.col_widths[1]),
                f"{goal.curval or 0:.1f}".ljust(self.col_widths[2]),
                f"{goal.goalval or 0:.1f}".ljust(self.col_widths[3]),
                self.format_date(goal.losedate).ljust(self.col_widths[4]),
                self.format_time_left(goal.losedate).ljust(self.col_widths[5]),
                self.format_date(goal.updated_at).ljust(self.col_widths[6]),
                self.get_goal_status(goal).ljust(self.col_widths[7])
            ]

            # Draw row
            x = 2
            for col_text, width in zip(goal_data, self.col_widths):
                stdscr.addstr(y, x, col_text)
                x += width + 2

            if idx + self.offset == self.selected_index:
                stdscr.attroff(curses.A_REVERSE)

    def draw_goal_detail(self, stdscr):
        """Draw detailed view of a single goal"""
        height, width = stdscr.getmaxyx()
        goal = self.current_goal_detail

        # Calculate displayable lines
        detail_lines = [
            ("Slug", goal.slug),
            ("Title", goal.title),
            ("Description", goal.description),
            ("Current Value", f"{goal.curval or 0:.1f}"),
            ("Goal Value", f"{goal.goalval or 0:.1f}"),
            ("Rate", f"{goal.rate or 0:.1f}"),
            ("Run Units", goal.runits),
            ("Goal Units", goal.gunits),
            ("Goal Type", goal.goal_type),
            ("Pledge", f"${goal.pledge or 0:.2f}"),
            ("Lose Date", self.format_date(goal.losedate)),
            ("Time Remaining", self.format_time_left(goal.losedate)),
            ("Last Updated", self.format_date(goal.updated_at)),
            ("Status", self.get_goal_status(goal)),
            ("Auto Data", goal.autodata),
            ("Fine Print", goal.fineprint),
            ("Y-Axis", goal.yaxis),
            ("Current Rate", f"{goal.currate or 0:.2f}"),
            ("Delta", goal.delta_text),
            ("Safe Buffer", f"{goal.safebuf or 0} days"),
            ("Deadline", f"{goal.deadline or 0}:00"),
            ("Weekends Off", "Yes" if goal.weekends_off else "No"),
            ("Tags", ", ".join(goal.tags or [])),
        ]

        # Draw title
        title = f"Goal Details: {goal.slug}"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)

        # Draw content
        visible_rows = height - 4
        y = 2
        for idx, (key, value) in enumerate(detail_lines[self.detail_offset:]):
            if y >= height - 2:  # Leave room for footer
                break

            stdscr.attron(curses.A_BOLD)
            stdscr.addstr(y, 2, f"{key}:".ljust(20))
            stdscr.attroff(curses.A_BOLD)

            # Handle multi-line values
            if value:
                value_str = str(value)
                while value_str and y < height - 2:
                    available_width = width - 24  # Account for left margin and key width
                    current_line = value_str[:available_width]
                    stdscr.addstr(y, 22, current_line)
                    value_str = value_str[available_width:]
                    y += 1
            else:
                stdscr.addstr(y, 22, "N/A")
                y += 1

    def run(self, stdscr):
        """Main application loop"""
        # Setup colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

        # Hide cursor
        curses.curs_set(0)

        # Fetch initial data
        self.fetch_goals()

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            if self.view_mode == "list":
                # Draw title
                title = "Beeminder Goals Status"
                stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)

                # Draw goals table
                self.draw_goals_list(stdscr)

                # Draw footer with new 'w' option
                footer = "↑↓: Navigate | q: Quit | r: Refresh | i: Show Details | c: Create Datapoint | w: Open Beeminder in browser"
                stdscr.addstr(height - 1, 1, footer)

                # Handle list view input
                key = stdscr.getch()
                if key == ord('q'):
                    break
                elif key == ord('w'):
                    self.open_in_browser()
                elif key == ord('r'):
                    self.fetch_goals()
                elif key == ord('c') and self.goals:
                    if self.create_datapoint(stdscr, self.goals[self.selected_index]):
                        self.fetch_goals()  # Refresh after successful creation
                elif key == ord('i') and self.goals:
                    self.view_mode = "detail"
                    self.detail_offset = 0
                    self.fetch_goal_detail(self.goals[self.selected_index].slug)
                elif key == curses.KEY_UP and self.selected_index > 0:
                    self.selected_index -= 1
                    if self.selected_index < self.offset:
                        self.offset = self.selected_index
                elif key == curses.KEY_DOWN and self.selected_index < len(self.goals) - 1:
                    self.selected_index += 1
                    if self.selected_index >= self.offset + height - 4:
                        self.offset = self.selected_index - (height - 5)

            else:  # detail view
                self.draw_goal_detail(stdscr)

                # Draw footer with new 'w' option
                footer = "↑↓: Scroll | b: Back to List | c: Create Datapoint | w: Open in Browser"
                stdscr.addstr(height - 1, 1, footer)

                # Handle detail view input
                key = stdscr.getch()
                if key == ord('b'):
                    self.view_mode = "list"
                elif key == ord('w'):
                    self.open_in_browser()
                elif key == ord('c'):
                    if self.create_datapoint(stdscr, self.current_goal_detail):
                        self.fetch_goal_detail(self.current_goal_detail.slug)  # Refresh after successful creation
                elif key == curses.KEY_UP and self.detail_offset > 0:
                    self.detail_offset -= 1
                elif key == curses.KEY_DOWN:
                    self.detail_offset += 1


def main():
    import os
    api_key = os.getenv("BEEMINDER_API_KEY")
    username = os.getenv("BEEMINDER_USERNAME")

    if not api_key:
        print("Please set BEEMINDER_API_KEY environment variable")
        return

    app = BeeminderCLI(api_key=api_key, username=username)
    curses.wrapper(app.run)


if __name__ == "__main__":
    main()