"""
Reddit API credentials file

How to get your own credentials:
- Visit: https://www.reddit.com/prefs/apps
- Click "Create another app" or "Create App"
- Set type to "script"
- Fill in the name and redirect URL (can be "http://localhost:8080")
- After saving, you will see your client_id (just under the app name)
  and client_secret (to the right labeled "secret")

For more details, see: https://github.com/reddit-archive/reddit/wiki/OAuth2

Fill in your credentials below before running any scripts that access Reddit!
DO NOT share or commit your credentials to public repositories.
"""

CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
USER_AGENT = "MyRedditApp by /u/yourusername"