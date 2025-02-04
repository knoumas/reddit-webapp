import os
from flask import Flask, render_template, request
import praw

app = Flask(__name__)

# 🔹 Reddit API Credentials (Replace with your own)
reddit = praw.Reddit(
    client_id=os.getenv("oe9zND_v3CFUyG62uikZsA"),
    client_secret=os.getenv("-sHW-Ux2i63kPzjpdqkSoYXJev659w"),
    user_agent="RedditBot",
    username=os.getenv("MCBBot"),
    password=os.getenv("Rooftop1!"),
    redirect_uri=os.getenv("https://reddit-webapp.onrender.com")  # Add this line
)

# 🔹 Route for Home Page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        target_username = request.form["username"]
        removed_count = remove_user_comments(target_username)
        return render_template("index.html", removed_count=removed_count, username=target_username)
    return render_template("index.html", removed_count=None)

# 🔹 Function to Remove Comments
def remove_user_comments(username):
    try:
        target_user = reddit.redditor(username)
        user_comments = target_user.comments.new(limit=30)  # Only remove last 30 comments
        removed = 0
        for comment in user_comments:
            if comment.subreddit.display_name.lower() == "minecraftbuddies":
                comment.mod.remove()
                removed += 1
        return removed
    except Exception as e:
        print(f"Error: {e}")
        return -1  # Return -1 if an error occurs

# 🔹 Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)

