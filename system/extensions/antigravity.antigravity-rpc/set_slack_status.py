import sys
import json
from composio import ComposioToolSet, Action
from composio.exceptions import ApiKeyNotProvidedError

def main():
    if len(sys.argv) < 2:
        print("Usage: python set_slack_status.py <status_text> [emoji]")
        sys.exit(1)
        
    status_text = sys.argv[1]
    
    if status_text == "CLEAR":
        action = Action.SLACK_CLEAR_STATUS
        params = {}
    else:
        action = Action.SLACK_SET_STATUS
        emoji = sys.argv[2] if len(sys.argv) > 2 else ":computer:"
        params = {
            "status_text": status_text[:100],
            "status_emoji": emoji
        }
        
    try:
        toolset = ComposioToolSet()
        toolset.execute_action(action=action, params=params)
    except ApiKeyNotProvidedError:
        print("Error: Composio is not authenticated.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error executing Composio action: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
