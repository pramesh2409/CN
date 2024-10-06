import socket
import streamlit as st
import threading

# Define the client-side game state
class TicTacToeClient:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # Initialize the board
        self.current_turn = 'X'  # Player X starts the game
        self.client_socket = None
        self.player_symbol = None
        self.game_over = False

    def connect_to_server(self, host='127.0.0.1', port=5555):
        """Connect to the Tic-Tac-Toe server."""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    def send_move(self, move):
        """Send the move to the server."""
        if self.client_socket and self.board[move] == ' ' and not self.game_over:
            self.client_socket.send(str(move).encode('utf-8'))

    def receive_messages(self):
        """Receive messages from the server."""
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.handle_server_message(message)
            except:
                break

    def handle_server_message(self, message):
        """Process the server's messages (like game updates)."""
        if "Welcome" in message:
            self.player_symbol = message.split()[-1]
        elif "Player" in message and "wins" in message:
            self.game_over = True
            st.warning(message)
        elif "draw" in message:
            self.game_over = True
            st.info("It's a draw!")
        elif "turn" in message:
            st.info(message)
        else:
            # Update board
            self.update_board(message)

    def update_board(self, board_state):
        """Update the board with the latest state from the server."""
        new_board = list(board_state.strip())
        if len(new_board) == 9:
            self.board = new_board

# Initialize the game client
client = TicTacToeClient()

# Create the Streamlit UI
st.title("Tic-Tac-Toe")

# Connect to the server
if st.button("Connect to Server"):
    client.connect_to_server()
    st.success("Connected to the server!")
    threading.Thread(target=client.receive_messages, daemon=True).start()

# Display the game board
for row in range(3):
    cols = st.columns(3)
    for col in range(3):
        idx = row * 3 + col
        with cols[col]:
            if st.button(client.board[idx], key=str(idx)):
                client.send_move(idx)

# Show current game state
if client.player_symbol:
    st.write(f"You are Player {client.player_symbol}")
if client.game_over:
    st.warning("Game Over!")
