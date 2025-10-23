import streamlit as st
import random
import copy

# --- Rainbow Configuration and Aesthetics (RAINBOW COLORS) ---

# Define the thematic content for each tile value using rainbow colors
RAINBOW_TILES = {
    0: {"text": "", "emoji": "  ", "color": "#fdfdfd", "text_color": "#776e65"},  # Empty tile (Off-White)
    2: {"text": "Cell", "emoji": "🧬", "color": "#ff6347", "text_color": "#f9f6f2"}, # Tomato Red
    4: {"text": "Monkey", "emoji": "🐵", "color": "#ff8c00", "text_color": "#f9f6f2"}, # Dark Orange
    8: {"text": "Prokey", "emoji": "🐒", "color": "#ffd700", "text_color": "#3c3a32"}, # Gold Yellow
    16: {"text": "Gorilla", "emoji": "🦍", "color": "#3cb371", "text_color": "#f9f6f2"}, # Medium Sea Green
    32: {"text": "Orangutan", "emoji": "🦧", "color": "#1e90ff", "text_color": "#f9f6f2"}, # Dodger Blue
    64: {"text": "Brain", "emoji": "🧠", "color": "#4b0082", "text_color": "#f9f6f2"}, # Indigo
    128: {"text": "Human", "emoji": "😀", "color": "#9400d3", "text_color": "#f9f6f2"}, # Dark Violet
    256: {"text": "Clown", "emoji": "🤡", "color": "#ff69b4", "text_color": "#f9f6f2"}, # Hot Pink
    512: {"text": "Poop", "emoji": "💩", "color": "#00ced1", "text_color": "#3c3a32"}, # Dark Turquoise
    1024: {"text": "Ghost", "emoji": "👻", "color": "#ff00ff", "text_color": "#f9f6f2"}, # Magenta
    2048: {"text": "Alien", "emoji": "👽", "color": "#ffbf00", "text_color": "#f9f6f2"}, # Vibrant Gold for Rainbow King
}

HIGH_TILE_COLOR = ("#3c3a32", "#f9f6f2") # For tiles > 2048 (beyond 2048, still dark)
BOARD_SIZE = 4

# --- Core Game Logic (Unchanged) ---

def initialize_board():
    """Initializes the 4x4 board with two random starting tiles."""
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    add_new_tile(board)
    add_new_tile(board)
    st.session_state.board = board
    st.session_state.score = 0
    st.session_state.game_status = "playing"

def add_new_tile(board):
    """Adds a new tile (90% chance of 2, 10% chance of 4) to a random empty spot."""
    empty_cells = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = 2 if random.random() < 0.9 else 4

def compress(row):
    """Moves non-zero tiles to the start of the row."""
    new_row = [i for i in row if i != 0]
    new_row += [0] * (BOARD_SIZE - len(new_row))
    return new_row

def merge_tiles(row):
    """Merges adjacent identical tiles."""
    score_increment = 0
    for i in range(BOARD_SIZE - 1):
        if row[i] == row[i+1] and row[i] != 0:
            row[i] *= 2
            score_increment += row[i]
            row[i+1] = 0
    return row, score_increment

def move_row(row):
    """Performs the full move logic on a single row."""
    row = compress(row)
    row, score_increment = merge_tiles(row)
    row = compress(row)
    return row, score_increment

def transpose_board(board):
    """Swaps rows and columns (used for Up/Down moves)."""
    return [list(t) for t in zip(*board)]

def reverse_board(board):
    """Reverses each row (used for Right move)."""
    new_board = []
    for row in board:
        new_board.append(row[::-1])
    return new_board

def is_game_over(board):
    """Checks if there are no empty tiles AND no possible moves/merges."""
    # Check for empty cells
    if any(0 in row for row in board):
        return False

    # Check for possible horizontal/vertical merges
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE - 1):
            if board[r][c] == board[r][c+1] or board[c][r] == board[c+1][r]:
                return False
                
    return True

def make_move(direction):
    """Handles the move in the specified direction."""
    if st.session_state.game_status not in ["playing", "won"]:
        return

    original_board = copy.deepcopy(st.session_state.board)
    current_board = st.session_state.board
    new_score = st.session_state.score
    
    # Orient the board so the move is always "Left"
    if direction == "up":
        current_board = transpose_board(current_board)
    elif direction == "down":
        current_board = transpose_board(reverse_board(current_board))
    elif direction == "right":
        current_board = reverse_board(current_board)

    # Apply move logic
    new_board = []
    total_score_increment = 0
    for row in current_board:
        new_row, score_increment = move_row(row)
        new_board.append(new_row)
        total_score_increment += score_increment
        
    new_score += total_score_increment

    # Re-orient the board back
    if direction == "up":
        final_board = transpose_board(new_board)
    elif direction == "down":
        final_board = reverse_board(transpose_board(new_board))
    elif direction == "right":
        final_board = reverse_board(new_board)
    else: # "left"
        final_board = new_board

    # Check if a move occurred
    if final_board != original_board:
        add_new_tile(final_board)
        st.session_state.board = final_board
        st.session_state.score = new_score
    else:
        # Check Game Over if no move was made
        if is_game_over(st.session_state.board):
            st.session_state.game_status = "lost"
    
    # Check for 2048 win (does not stop the game)
    if any(2048 in row for row in st.session_state.board) and st.session_state.game_status != "won":
        st.session_state.game_status = "won"


# --- UI and Rendering ---

def get_tile_html(value):
    """Generates the HTML/CSS for a single tile based on its value and theme."""
    
    # Use the RAINBOW_TILES configuration
    tile_info = RAINBOW_TILES.get(value, {"text": str(value), "emoji": "❓", "color": HIGH_TILE_COLOR[0], "text_color": HIGH_TILE_COLOR[1]})
    
    bg_color = tile_info["color"]
    text_color = tile_info["text_color"]
    tile_text = tile_info["text"]
    tile_emoji = tile_info["emoji"]
    
    # Adjust font size based on content length
    font_size_class = "text-sm" if len(tile_text) > 10 else "text-lg" if len(tile_text) > 5 else "text-xl"
    
    # Special handling for 2048 tile (RAINBOW KING)
    if value >= 2048:
        # Placeholder for a multi-colored/rainbow image if possible, otherwise a vibrant color
        image_url = "https://placehold.co/100x100/ffbf00/f9f6f2/png?text=👽+EVO" 
        
        content_html = f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
            <img src="{image_url}" alt="Alien Evolution" style="width: 75%; height: 75%; object-fit: cover; border-radius: 4px; border: 2px solid {text_color};">
            <span style="font-size: 14px; font-weight: bold; margin-top: 4px;">{tile_text} {tile_emoji}</span>
        </div>
        """
    elif value == 0:
         content_html = ""
    else:
        # Standard tile content (Text + Emoji)
        content_html = f"""
        <div style="text-align: center;">
            <div class="{font_size_class}" style="font-weight: 800; line-height: 1.2;">{tile_text}</div>
            <div style="font-size: 24px; line-height: 1;">{tile_emoji}</div>
        </div>
        """

    html = f"""
    <div style="
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Inter', sans-serif;
        border-radius: 8px; /* Slightly rounder for a softer rainbow feel */
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 100%;
        min-height: 80px;
        animation: tile-appear 0.15s ease-out;
        transition: transform 0.15s ease-out;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2); /* Softer shadow */
    ">
        {content_html}
    </div>
    """
    return html

def draw_board(board):
    """Renders the entire 2048 board using Streamlit's st.html()."""
    
    # Build the grid items
    grid_items = "".join(get_tile_html(board[r][c]) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))
            
    # Compile the final HTML structure with embedded CSS
    html_content = f"""
    <style>
        .game-board {{
            display: grid;
            grid-template-columns: repeat({BOARD_SIZE}, 1fr);
            grid-template-rows: repeat({BOARD_SIZE}, 1fr);
            gap: 10px; /* Slightly wider gap */
            background-color: #f0e6ef; /* Very light, slightly purplish background for contrast */
            padding: 10px;
            border-radius: 12px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 500px;
            aspect-ratio: 1 / 1;
            margin: 0 auto;
        }}
        @keyframes tile-appear {{
            0% {{ transform: scale(0.5); opacity: 0.5; }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}
    </style>
    <div class="game-board">
        {grid_items}
    </div>
    """
    st.html(html_content)

# --- Streamlit App Entry Point ---

def app():
    # Reverting page title to reflect Human Evolution theme
    st.set_page_config(page_title="2048 Human Evolution", layout="centered")
    
    # Updated Title: Keeping your name and the original theme
    st.title("Nathan's 🧬 2048: Human Evolution Merge")
    st.markdown("Merge the life forms to reach the **Alien** stage!")

    # --- Game Rules (English) ---
    st.markdown("---")
    st.subheader("How to Play (Simple Rules)")
    st.markdown("""
    1.  **Merge:** Use the directional buttons to move all tiles in that direction.
    2.  **Match:** When two tiles with the same evolutionary stage (e.g., two 'Monkey' tiles) collide, they **merge** into the next stage ('Prokey').
    3.  **New Tiles:** A new 'Cell' or 'Monkey' tile randomly appears on the board after every move.
    4.  **Win:** Reach the **Alien** tile (2048 value) to win the game!
    5.  **Lose:** If the board fills up and no more moves or merges are possible, the game is over.
    """)
    
    # --- Game Rules (Chinese) ---
    # This section remains unchanged as requested
    with st.expander("规则 (Chinese Rules)"):
        st.markdown("""
        1.  **合并 (Hé bìng):** 使用方向按钮向该方向移动所有方块。
        2.  **匹配 (Pǐ pèi):** 当两个具有相同进化阶段的方块（例如，两个 'Monkey' 方块）碰撞时，它们会**合并**成下一个阶段（'Prokey'）。
        3.  **新方块 (Xīn fāngkuài):** 每次移动后，一个新的 'Cell' 或 'Monkey' 方块会随机出现在棋盘上。
        4.  **获胜 (Huò shèng):** 达到**外星人 (Alien)** 方块（2048 值）即可赢得游戏！
        5.  **失败 (Shī bài):** 如果棋盘被填满，并且不再有移动或合并的可能性，则游戏结束。
        """)

    st.markdown("---")
    
    # 1. State Initialization
    if 'board' not in st.session_state:
        initialize_board()
        
    # Determine the status for display
    status = st.session_state.get('game_status', 'playing')
    
    # 2. Score and Status Display
    col_score, col_status = st.columns([1, 1.5])
    with col_score:
        st.metric("SCORE", st.session_state.score)

    with col_status:
        if status == "lost":
            st.error("GAME OVER! No more moves. Evolution stopped!", icon="❌")
        elif status == "won":
            st.success("You reached ALIEN! 👽 Evolution complete!", icon="👑")
        else:
            st.info("Keep merging to advance evolution!", icon="💡")


    st.markdown("---")
    
    # 3. Game Board Rendering
    draw_board(st.session_state.board)

    # 4. Controls (Directional Buttons)
    st.subheader("🧬 Move Evolution")
    
    # Layout: Group UP/LEFT and DOWN/RIGHT into two parallel rows
    
    # Row 1: UP and LEFT
    col_up, col_left = st.columns(2)
    with col_up:
        st.button("⬆️ UP", on_click=make_move, args=("up",), use_container_width=True)
        
    with col_left:
        st.button("⬅️ LEFT", on_click=make_move, args=("left",), use_container_width=True)

    # Row 2: DOWN and RIGHT
    col_down, col_right = st.columns(2)
        
    with col_down:
        st.button("⬇️ DOWN", on_click=make_move, args=("down",), use_container_width=True)
        
    with col_right:
        st.button("➡️ RIGHT", on_click=make_move, args=("right",), use_container_width=True)

    # New Game button remains full width
    st.markdown("---")
    st.button("🔄 NEW EVOLUTION GAME", on_click=initialize_board, type="primary", use_container_width=True)

    st.markdown("---")
    st.caption("Tip: This game is best played on desktop where the directional buttons are easily accessible.")

if __name__ == "__main__":
    app()
