from ConnectState import ConnectState

def play():
    state = ConnectState()

    while not state.is_game_over():
        print("Current state:")
        state.print()

        user_move = int(input("Enter a move: "))
        while user_move not in state.get_legal_moves():
            print("Illegal move")
            user_move = int(input("Enter a move: "))

        state.move(user_move)

        if state.is_game_over():
            state.print()
            print("Game over!")
            break


if __name__ == "__main__":
    play()
