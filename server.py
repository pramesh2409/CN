import socket
import threading

board = [' ' for _ in range(9)]
current_turn = 'X' 

clients = []

def check_winner():
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
                      (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
                      (0, 4, 8), (2, 4, 6)]  # Diagonals
    for (x, y, z) in win_conditions:
        if board[x] == board[y] == board[z] and board[x] != ' ':
            return board[x]
    return None

# Function to check if the board is full (draw)
def is_draw():
    return ' ' not in board

# Broadcast the board to both players
def broadcast(message):
    for client in clients:
        client.send(message.encode('utf-8'))

# Handle player moves and game logic
def handle_client(client_socket, player_symbol):
    global current_turn
    client_socket.send(f"Welcome Player {player_symbol}! Waiting for other player...".encode('utf-8'))

    while len(clients) < 2:
        pass  # Wait for both players to connect

    if player_symbol == 'X':
        broadcast("Player X's turn!")

    while True:
        try:
            # Receive player move
            move = int(client_socket.recv(1024).decode('utf-8'))

            if board[move] == ' ' and current_turn == player_symbol:
                board[move] = player_symbol

                # Check for winner or draw
                winner = check_winner()
                if winner:
                    broadcast(f"Player {winner} wins!")
                    broadcast_board()
                    break
                elif is_draw():
                    broadcast("It's a draw!")
                    broadcast_board()
                    break

                # Change turn
                current_turn = 'O' if current_turn == 'X' else 'X'
                broadcast(f"Player {current_turn}'s turn!")
                broadcast_board()
            else:
                client_socket.send("Invalid move or not your turn!".encode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            break

# Function to print and broadcast the board
def broadcast_board():
    board_str = f"\n{board[0]} | {board[1]} | {board[2]}\n---------\n{board[3]} | {board[4]} | {board[5]}\n---------\n{board[6]} | {board[7]} | {board[8]}"
    broadcast(board_str)

# Start the game server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('https://cn-dp0y.onrender.com', 5555))
    server.listen(2)  # Accept up to 2 clients

    print("Server started. Waiting for players to connect...")

    player_symbols = ['X', 'O']

    while len(clients) < 2:
        client_socket, client_address = server.accept()
        print(f"Player connected from {client_address}")

        clients.append(client_socket)
        player_symbol = player_symbols[len(clients) - 1]

        # Start a new thread to handle the player
        thread = threading.Thread(target=handle_client, args=(client_socket, player_symbol))
        thread.start()

if __name__ == "__main__":
    start_server()
