import subprocess
import time
from pathlib import Path
import sys

class UCIEngine:
    def __init__(self, engine_name, binary_path, difficulty=1, move_time_ms=None, secondary_binary_path=None):
        self.engine_name = engine_name
        self.name = f"{engine_name} | UCI | Difficulty: {difficulty}"
        self.binary_path = binary_path
        self.secondary_binary_path = secondary_binary_path
        self.difficulty = difficulty
        self.move_time_ms = move_time_ms
        self.process = None

    def _init_uci(self, timeout=5):
        """Initialize the UCI engine."""
        self._start_process()
        self._send_command("uci")
        self._read_until("uciok", timeout)
        self._send_command("isready")
        self._read_until("readyok", timeout)

    def _start_process(self):
        """Start the UCI engine process."""
        if self.process and self.process.poll() is None:
            return  # Process already started
        if not self.binary_path and not self.secondary_binary_path:
            raise ValueError("Binary path for UCI engine is not set.")
        try:
            if self.binary_path is not None:
                if not sys.platform.startswith("win"):
                    try:
                        Path(self.binary_path).chmod(Path(self.binary_path).stat().st_mode | 0o111)
                    except Exception as e:
                        print(f"Warning: Failed to set executable permissions for {self.binary_path}: {e}")
                self.process = subprocess.Popen(
                    [self.binary_path],
                    **self._subprocess_kwargs()
                )
            else:
                raise ValueError("Primary binary path is not set for UCI engine.")
        except Exception as e:
            if self.secondary_binary_path:
                try:
                    if not sys.platform.startswith("win"):
                        try:
                            Path(self.secondary_binary_path).chmod(Path(self.secondary_binary_path).stat().st_mode | 0o111)
                        except Exception as e:
                            print(f"Warning: Failed to set executable permissions for {self.secondary_binary_path}: {e}")
                    self.process = subprocess.Popen(
                        [self.secondary_binary_path],
                        **self._subprocess_kwargs()
                    )
                    self.binary_path = self.secondary_binary_path  # Update to secondary path
                except Exception as e:
                    raise RuntimeError(f"Failed to start UCI engine process with both primary and secondary binaries: {e}")
            else:
                raise RuntimeError(f"Failed to start UCI engine process: {e}")
            
    def _subprocess_kwargs(self):
        """Return the keyword arguments for subprocess.Popen."""
        if sys.platform.startswith("win"):
            return {
                "creationflags": subprocess.CREATE_NO_WINDOW,
                "stdin": subprocess.PIPE,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.STDOUT,
                "text": True,
                "bufsize": 1,  # Line-buffered
            }
        else:
            return {
                "stdin": subprocess.PIPE,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.STDOUT,
                "text": True,
                "bufsize": 1,  # Line-buffered
            }

    def _send_command(self, command):
        """Send a command to the UCI engine."""
        if not self.process or self.process.poll() is not None or self.process.stdin is None:
            raise RuntimeError("UCI engine process is not running or stdin is not available.")
        try:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
        except Exception as e:
            raise RuntimeError(f"Failed to send command to UCI engine: {e} Command: {command}")

    def _read_until(self, token, timeout):
        """Read a specific token from the UCI engine's output."""
        if not self.process or self.process.poll() is not None or self.process.stdout is None:
            raise RuntimeError("UCI engine process is not running or stdout is not available.")
        deadline = time.monotonic() + timeout if timeout else None
        while deadline is None or time.monotonic() <= deadline:
            line = self.process.stdout.readline()
            if not line:
                if self.process.poll() is not None:
                    raise RuntimeError("UCI engine process has terminated.")
                time.sleep(0.01)  # Avoid busy waiting
                continue
            line = line.strip()
            if token in line:
                return line
        raise TimeoutError(f"Timeout while waiting for token '{token}' from UCI engine.")

    def read_response(self, timeout=5):
        """Read a response from the UCI engine."""
        if not self.process or self.process.poll() is not None or self.process.stdout is None:
            raise RuntimeError("UCI engine process is not running or stdout is not available.")
        deadline = time.monotonic() + timeout if timeout else None
        while deadline is None or time.monotonic() <= deadline:
                line = self.process.stdout.readline().strip()

                if not line:
                    if self.process.poll() is not None:
                        raise RuntimeError("UCI engine process has terminated.")
                    time.sleep(0.01)  # Avoid busy waiting
                    continue

                if not line.startswith("bestmove "):
                    continue

                return self._parse_bestmove(line)
        raise TimeoutError("Timeout while waiting for bestmove from UCI engine.")

    def _stop(self):
        """Stop the UCI engine process."""
        if not self.process or self.process.poll() is not None:
            return  # Process already stopped
        try:
            self._send_command("quit")
            self.process.wait(timeout=1)
            if self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=5)
                if self.process.poll() is None:
                    self.process.kill()
        except Exception as e:
            raise RuntimeError(f"Failed to stop UCI engine process: {e}")
        finally:
            self.process = None

    def _build_position_command(self, game):
        """Build the UCI position command based on the current game state."""
        moves = []
        if game.move_history is None:
            return "position startpos"
        for move in game.move_history:
            from_sq = move["from"]
            to_sq = move["to"]
            if move["was_promotion"]:
                moves.append(f"{from_sq}{to_sq}{move['promotion_choice'].lower()}")
            else:
                moves.append(f"{from_sq}{to_sq}")
        if not moves:
            return "position startpos"
        return f"position startpos moves {' '.join(moves)}"

    def difficulty_to_go_args(self):
        """Depth or skill level arguments for the UCI engine based on the difficulty setting."""
        if self.move_time_ms is not None and self.move_time_ms > 0:
            return f"go movetime {self.move_time_ms}"
        else:
            return f"go depth 12"  # Default depth if no move time is specified to 12 for now.

    def _parse_bestmove(self, line):
        """Parse the best move from the UCI engine's output."""
        if not line.startswith("bestmove"):
            raise ValueError(f"Unexpected response from UCI engine: {line}")
        parts = line.split()
        move_token = parts[1] if len(parts) > 1 else None
        if not parts or len(parts) < 2:
            raise ValueError(f"Invalid bestmove format from UCI engine: {line}")
        if move_token == "(none)":
            return None  # No valid move available
        from_sq = move_token[:2]
        to_sq = move_token[2:4]
        promotion_choice = move_token[4] if len(move_token) == 5 else None
        if len(move_token) == 4 and from_sq[0] in "abcdefgh" and from_sq[1] in "12345678" and to_sq[0] in "abcdefgh" and to_sq[1] in "12345678":
            return (from_sq, to_sq)
        elif len(move_token) == 5 and from_sq[0] in "abcdefgh" and from_sq[1] in "12345678" and to_sq[0] in "abcdefgh" and to_sq[1] in "12345678" and promotion_choice in "qrbn":
            return (from_sq, to_sq, promotion_choice.upper())
        raise ValueError(f"Invalid move format from UCI engine: {move_token}")
    
    def get_move(self, game):
        """Get the best move from the UCI engine based on the current game state."""
        if game.game_over:
            return None  # No moves available if the game is over
        try:
            self._init_uci()
            position_command = self._build_position_command(game)
            self._send_command(position_command)
            go_args = self.difficulty_to_go_args()
            self._send_command(go_args)
            best_move = self.read_response()
            if best_move is None:
                return None  # No valid move available
            return best_move
        except Exception as e:
            try:
                self._stop()  # Ensure the engine process is stopped on error
            except Exception as stop_exception:
                print(f"Failed to stop UCI engine process: {stop_exception}")
            raise RuntimeError(f"Failed to get move from UCI engine: {e}")