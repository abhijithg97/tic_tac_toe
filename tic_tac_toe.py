import json
import random
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


class TicTacToe:
    SCORE_FILE = Path(__file__).with_name("tic_tac_toe_scores.json")
    WINNING_COMBINATIONS = (
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    )

    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe vs Computer")
        self.root.configure(bg="#f0f0f0")
        self.root.protocol("WM_DELETE_WINDOW", self.close_game)

        self.current_player = "X"
        self.board = [""] * 9
        self.game_over = False
        self.computer_after_id = None
        self.scores = self._load_scores()
        self.mode = tk.StringVar(value="Computer")
        self.difficulty = tk.StringVar(value="Hard")

        settings = tk.Frame(root, bg="#f0f0f0")
        settings.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=(8, 4))
        tk.Label(
            settings,
            text="Mode:",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#111111"
        ).pack(side="left", padx=(4, 8))
        mode_menu = ttk.Combobox(
            settings,
            textvariable=self.mode,
            values=("Computer", "Two Players"),
            state="readonly",
            width=12
        )
        mode_menu.pack(side="left", padx=(0, 12))
        mode_menu.bind("<<ComboboxSelected>>", self.change_mode)

        tk.Label(
            settings,
            text="Difficulty:",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#111111"
        ).pack(side="left", padx=(4, 8))
        self.difficulty_menu = ttk.Combobox(
            settings,
            textvariable=self.difficulty,
            values=("Easy", "Medium", "Hard"),
            state="readonly",
            width=10
        )
        self.difficulty_menu.pack(side="left")

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                root,
                text="",
                font=("Arial", 28, "bold"),
                width=6,
                height=3,
                bg="#ffffff",
                fg="#222222",
                command=lambda idx=i: self.make_move(idx)
            )
            btn.grid(row=1 + i // 3, column=i % 3, padx=5, pady=5, sticky="nsew")
            self.buttons.append(btn)

        self.status = tk.Label(
            root,
            text="Your turn (X)",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0",
            fg="#111111"
        )
        self.status.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10, 5))

        self.score_label = tk.Label(
            root,
            text="",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        self.score_label.grid(row=5, column=0, columnspan=3, sticky="ew", pady=4)
        self._update_score_label()

        restart_btn = tk.Button(
            root,
            text="New Round",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.restart_game
        )
        restart_btn.grid(row=6, column=0, columnspan=3, sticky="ew", padx=5, pady=(4, 10))

        for c in range(3):
            self.root.grid_columnconfigure(c, weight=1)
        for r in range(7):
            self.root.grid_rowconfigure(r, weight=1)

    def make_move(self, index):
        if self.board[index] or self.game_over:
            return
        if self.mode.get() == "Computer" and self.current_player != "X":
            return

        player = self.current_player
        self._place_move(index, player)
        if self._finish_if_over(player):
            return

        self.current_player = "O" if player == "X" else "X"
        if self.mode.get() == "Computer" and self.current_player == "O":
            self.status.config(text="Computer is thinking...")
            for button in self.buttons:
                if button["state"] != "disabled":
                    button.config(state="disabled")
            self.computer_after_id = self.root.after(350, self.computer_move)
        else:
            self.status.config(text=self._turn_message())

    def computer_move(self):
        self.computer_after_id = None
        if self.game_over or self.mode.get() != "Computer":
            return

        index = self._choose_computer_move()
        self._place_move(index, "O")
        if self._finish_if_over("O"):
            return

        self.current_player = "X"
        self.status.config(text=self._turn_message())
        for i, button in enumerate(self.buttons):
            if not self.board[i]:
                button.config(state="normal")

    def _turn_message(self):
        if self.mode.get() == "Two Players":
            return f"Player {self.current_player}'s turn"
        return "Your turn (X)"

    def _place_move(self, index, player):
        self.board[index] = player
        self.buttons[index].config(
            text=player,
            state="disabled",
            fg="#1976D2" if player == "X" else "#D32F2F"
        )

    def _finish_if_over(self, player):
        winning_line = self._winning_combination(self.board, player)
        if winning_line:
            self.scores[player] += 1
            for index in winning_line:
                self.buttons[index].config(bg="#FFD54F", activebackground="#FFD54F")
            self._save_scores()

            if self.mode.get() == "Two Players":
                winner = f"Player {player} wins!"
            else:
                winner = "You win!" if player == "X" else "The computer wins!"
            self._end_round(winner, f"{winner} ({player})")
            return True

        if all(self.board):
            self.scores["draws"] += 1
            self._save_scores()
            self._end_round("It's a draw!", "It's a draw!")
            return True
        return False

    def _end_round(self, status, dialog):
        self.game_over = True
        self.status.config(text=status)
        self._update_score_label()
        for button in self.buttons:
            button.config(state="disabled")
        messagebox.showinfo("Round Over", dialog, parent=self.root)

    def _update_score_label(self):
        if self.mode.get() == "Two Players":
            score_text = (
                f"Player X: {self.scores['X']}   "
                f"Player O: {self.scores['O']}   "
                f"Draws: {self.scores['draws']}"
            )
        else:
            score_text = (
                f"You (X): {self.scores['X']}   "
                f"Computer (O): {self.scores['O']}   "
                f"Draws: {self.scores['draws']}"
            )
        self.score_label.config(text=score_text)

    def _load_scores(self):
        try:
            scores = json.loads(self.SCORE_FILE.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {"X": 0, "O": 0, "draws": 0}
        except (OSError, json.JSONDecodeError) as error:
            messagebox.showwarning(
                "Scores Could Not Be Loaded",
                f"Starting with a fresh scoreboard because the saved scores could not be read.\n\n{error}",
                parent=self.root
            )
            return {"X": 0, "O": 0, "draws": 0}

        if (
            not isinstance(scores, dict)
            or any(
                not isinstance(scores.get(key), int)
                or isinstance(scores.get(key), bool)
                or scores[key] < 0
                for key in ("X", "O", "draws")
            )
        ):
            messagebox.showwarning(
                "Invalid Saved Scores",
                "Starting with a fresh scoreboard because the saved score data is invalid.",
                parent=self.root
            )
            return {"X": 0, "O": 0, "draws": 0}

        return {key: scores[key] for key in ("X", "O", "draws")}

    def _save_scores(self):
        try:
            self.SCORE_FILE.write_text(
                json.dumps(self.scores, indent=2) + "\n",
                encoding="utf-8"
            )
        except OSError as error:
            messagebox.showerror(
                "Scores Could Not Be Saved",
                f"The round is complete, but the scoreboard could not be saved.\n\n{error}",
                parent=self.root
            )

    def change_mode(self, _event=None):
        del _event
        self.restart_game()
        self.difficulty_menu.config(
            state="disabled" if self.mode.get() == "Two Players" else "readonly"
        )
        self._update_score_label()

    def _choose_computer_move(self):
        available = [i for i, cell in enumerate(self.board) if not cell]
        difficulty = self.difficulty.get()

        if difficulty == "Easy":
            return random.choice(available)

        best_score = float("-inf")
        best_moves = []
        for index in available:
            self.board[index] = "O"
            score = self._minimax(self.board, "X", 1)
            self.board[index] = ""

            if score > best_score:
                best_score = score
                best_moves = [index]
            elif score == best_score:
                best_moves.append(index)

        if difficulty == "Medium" and random.random() < 0.5:
            return random.choice(available)
        return random.choice(best_moves)

    def _minimax(self, board, player, depth):
        if self._check_winner(board, "O"):
            return 10 - depth
        if self._check_winner(board, "X"):
            return depth - 10
        if all(board):
            return 0

        scores = []
        for index, cell in enumerate(board):
            if not cell:
                board[index] = player
                next_player = "X" if player == "O" else "O"
                scores.append(self._minimax(board, next_player, depth + 1))
                board[index] = ""

        return max(scores) if player == "O" else min(scores)

    @classmethod
    def _check_winner(cls, board, player):
        return cls._winning_combination(board, player) is not None

    @classmethod
    def _winning_combination(cls, board, player):
        return next(
            (
                combination
                for combination in cls.WINNING_COMBINATIONS
                if all(board[index] == player for index in combination)
            ),
            None
        )

    def restart_game(self):
        if self.computer_after_id is not None:
            self.root.after_cancel(self.computer_after_id)
            self.computer_after_id = None

        self.board = [""] * 9
        self.current_player = "X"
        self.game_over = False

        for button in self.buttons:
            button.config(text="", state="normal", bg="#ffffff", fg="#222222")

        self.status.config(text=self._turn_message())

    def close_game(self):
        self.scores = {"X": 0, "O": 0, "draws": 0}
        self._save_scores()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
