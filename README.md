# ♟️ Nine Men's Morris – Python Game

---

## 🎮 Gameplay Overview

- Two players take turns placing their 9 pieces on a 24-point board.
- After all pieces are placed, players move their pieces to adjacent spots.
- Forming a **mill** (3 in a row) allows removal of an opponent's piece.
- Game ends when one player is left with fewer than 3 pieces or can't move.

---

## 🗺️ Board Design

The board consists of:
- 3 concentric squares with midpoints of each side connected.
- 24 total positions where pieces can be placed or moved.
- Each position (Point) stores its coordinates, connections, player status, and occupancy.

---

## ✅ Features

- 🧩 Piece placement with proper mill rule handling
- 🔄 Turn-based logic with event status displayed
- ✨ Highlighting of valid move options during movement phase
- 🎯 Mill detection and opponent piece removal system
- 🏁 Win condition detection based on piece count and mobility


  
---

## 🚀 Future Improvements

- Add a **Player vs AI** mode
- Implement **undo** functionality
- Smooth **animations** for moving pieces

---

## 🧱 Code Structure and Key Components

### 1. **Point Class**
Represents a point on the board:
- `x`, `y` – Coordinates on screen
- `occupied` – Boolean flag
- `player` – Player who owns the piece
- `connections` – List of connected points

### 2. **Key Functions**
- `my_board()` – Draws board and returns point list
- `piece_place()` – Handles piece placement
- `move_piece()` – Executes valid piece movements
- `mill_detector()` – Detects newly formed mills
- `remove_opponent_piece()` – Handles logic for piece removal
- `draw_highlights()` – Shows valid move options
- `check_win()` – Checks for game-ending conditions

---

## 🖥️ Technologies Used

- **Language:** Python
- **GUI:** Pygame

---

## 🙋‍♂️ Author

**Volety Sriram Panchamukhi**  
B.Tech, Electrical and Electronics Engineering  
Minor in Computer Science

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).

