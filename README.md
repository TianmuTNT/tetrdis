# Tetrdis - A Tetris Clone for Discord

This project implements a playable game of Tetris within Discord by cleverly using its URL preview and message editing features. The game state is rendered into a WEBP image on-the-fly by a Python Flask server.

## How It Works

The core idea is to represent the entire sequence of player actions as a string within a URL. For example, `https://your-server.com/lri.webp`.

1.  When this URL is posted in Discord, Discord's server sends a GET request to it.
2.  The Flask server receives the request, takes the action string (`lr`), and simulates a new game of Tetris from the very beginning according to those actions.
3.  The final state of the game board is rendered into a WEBP image using the Pillow library.
4.  This image is sent back to Discord, which then displays it as a preview.
5.  To make the next move, the user replies to their own message with Discord's `s/find/replace` command to edit the URL, adding a new action. For example: `s/lri/lriu`. This generates a new URL, and the process repeats.

A fixed seed for the piece sequence ensures that the game is deterministic and repeatable, which is essential for this stateless approach.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/TianmuTNT/tetrdis.git
    cd tetrdis
    ```

2.  **Install dependencies:**
    Make sure you have Python 3 installed. Then, install the required libraries using pip.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the server:**
    ```bash
    python app.py
    ```
    The server will start on `http://localhost:5000` by default.

## How to Play

1.  **Expose your local server to the internet.**
    Since Discord needs to be able to access your server, you must expose your local server to the public internet. Tools like [ngrok](https://ngrok.com/) are perfect for this.
    ```bash
    ngrok http 5000
    ```
    ngrok will give you a public URL (e.g., `https://random-string.ngrok.io`).

2.  **Start a game in Discord.**
    Post the initial game URL in any Discord channel, using your public URL from ngrok:
    ```
    https://random-string.ngrok.io/i.webp
    ```

3.  **Make your moves.**
    Reply to your own message containing the link and use the `s/` command to add moves. The actions are prepended to the `i.webp` part of the URL.

    *   **Move Left:** `s/i/li`
    *   **Move Right:** `s/i/ri`
    *   **Rotate:** `s/i/ui`
    *   **Hard Drop:** `s/i/si`

    For subsequent moves, you edit the existing action string. For example, to move right after moving left:
    `s/li/lri`

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
