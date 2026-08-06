# Beeminder Client

A powerful Python client library and terminal interface for Beeminder. This package provides both a programmatic API client for building Beeminder applications and a feature-rich terminal interface for managing your Beeminder goals directly from the command line.

## Features

- **Complete API Coverage**: Full implementation of the Beeminder API with type hints
- **Interactive Terminal Interface**: Curses-based UI for managing goals and datapoints
- **Type-Safe**: Built with Pydantic models for reliable data handling
- **Easy to Use**: Simple interface for both programmatic and terminal usage

## Installation

Install from PyPI:

```bash
pip install beeminder_client
```

## Configuration

The client requires a Beeminder API key and optionally your username. These can be set via environment variables:

```bash
export BEEMINDER_API_KEY="your-api-key-here"
export BEEMINDER_USERNAME="your-username"  # Optional
```

To get your API key:
1. Log into Beeminder
2. Go to https://www.beeminder.com/api/v1/auth_token.json

## Using the Terminal Interface

Start the terminal interface:

```bash
beeminder-cli
```

### Terminal Controls

- **Navigation**:
  - `↑`/`↓`: Navigate through goals
  - `i`: View detailed information for selected goal
  - `b`: Go back to goal list from detail view
  - `r`: Refresh goal data
  - `c`: Create new datapoint for selected goal
  - `w`: Open goal in web browser
  - `q`: Quit application

### Adding Datapoints

1. Select a goal using arrow keys
2. Press `c` to create new datapoint
3. Enter value when prompted
4. Optionally add a comment
5. Press Enter to submit

## Using the API Client

```python
from beeminder_client.beeminder import BeeminderAPI

# Initialize client
client = BeeminderAPI(api_key="your-api-key", default_user="username")

# Get all goals
goals = client.get_all_goals()

# Get specific goal with datapoints
goal = client.get_goal("goal-slug", datapoints=True)

# Create datapoint
client.create_datapoint(
  goal_slug="goal-slug",
  value=1.0,
  comment="Added via API"
)
```

## Program Design

The project is structured into three main components:

### 1. API Client (`beeminder.py`)
- Handles all HTTP communication with Beeminder's API
- Provides type-safe methods for all API endpoints
- Uses requests for HTTP operations
- Implements error handling and response validation

### 2. Data Models (`models.py`)
- Pydantic models for type safety and validation
- Represents Beeminder entities (Goals, Datapoints, etc.)
- Handles data parsing and serialization
- Provides clear structure for API responses

### 3. Terminal Interface (`beeminder_cli.py`)
- Built with Python's curses library
- Implements Model-View pattern:
  - `BeeminderCLI`: Main controller class
  - `InputWindow`: Helper class for user input
- Features:
  - Two-panel interface (list and detail views)
  - Efficient navigation and data entry
  - Real-time updates and feedback
  - Browser integration

### Architecture Decisions

1. **Type Safety**: Using Pydantic models ensures reliable data handling and provides excellent IDE support.
2. **Separation of Concerns**: Clear separation between API client, data models, and UI.
3. **Error Handling**: Comprehensive error handling in both API and UI layers.
4. **User Experience**: Terminal interface designed for efficiency and ease of use.
5. **Extensibility**: Easy to extend with new features or integrate into other applications.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT

## Acknowledgments

- Built using the [Beeminder API](https://api.beeminder.com/)
- Inspired by the need for a better command-line interface for Beeminder
