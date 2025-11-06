# Import necessary libraries
# Ensure core.constants defines: COLUMNS, ROWS, NO_GAME, PLAYER_AI, PLAYER_HUMAN
# Example: COLUMNS=7, ROWS=6, NO_GAME=0, PLAYER_HUMAN=1, PLAYER_AI=2
try:
    from core.constants import COLUMNS, ROWS, NO_GAME, PLAYER_AI, PLAYER_HUMAN
except ImportError:
    print("Warning: core.constants not found. Using default values for testing.")
    COLUMNS = 7
    ROWS = 6
    NO_GAME = 0
    PLAYER_HUMAN = 1  # Assume Human = Circle
    PLAYER_AI = 2  # Assume AI = Cross

import cv2
import numpy as np
import math  # For angle calculations in cross detection

# --- Constants ---
# HoughCircles parameters (critical for tuning)
HC_DP = 1.2  # Inverse ratio of accumulator resolution
HC_MIN_DIST = 40  # Minimum distance between detected centers
HC_PARAM1 = 50  # Upper threshold for Canny edge detector used in HoughCircles
HC_PARAM2 = 25  # Accumulator threshold for circle centers (lower means more circles)
HC_MIN_RADIUS = 5  # Minimum circle radius
HC_MAX_RADIUS = 40  # Maximum circle radius (adjust based on cell size)

# Cross Detection Parameters (tuning required)
CROSS_CANNY_LOW = 50
CROSS_CANNY_HIGH = 150
CROSS_HOUGH_THRESHOLD = 15  # Threshold for HoughLinesP in cell
CROSS_HOUGH_MIN_LEN = 10  # Min line length for HoughLinesP in cell
CROSS_HOUGH_MAX_GAP = 7  # Max gap for HoughLinesP in cell
CROSS_MIN_LINES_BEFORE_FILTER = 2  # Min lines from Hough before filtering
CROSS_MIN_LINES_AFTER_FILTER = 2  # Min lines needed after length/position filtering
# CROSS_ANGLE_THRESHOLD = 30 # Allowed deviation from 90 degrees (REPLACED by intersection)
CROSS_MIN_LINE_LEN_RATIO = (
    0.25  # Line length must be at least 25% of cell's min dimension
)
CROSS_CENTER_PROXIMITY_RATIO = (
    0.4  # Intersection must be within 40% of half-width/height from center
)


# --- Helper Functions ---


def get_picture():
    cap = cv2.VideoCapture(0)  # Try 1 if 0 doesn't work
    if not cap.isOpened():
        print("Error: Could not open USB webcam")
        return None

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Error: Failed to capture image")
        return None

    return frame  # Return the captured frame directly


def is_floating_move(grid, row, col):
    """
    Checks if the given move (row, col) is a 'floating' piece.
    A floating piece is not on the bottom row and has an empty cell below it.

    :param grid: 2D-Array (6x7) with the current board state.
    :param row: Row index of the new piece (0 = top row, 5 = bottom row).
    :param col: Column index of the new piece.
    :return: True if the piece is floating, False otherwise.
    """
    if row == ROWS - 1:  # Use ROWS constant
        return False
    # Check bounds for row+1 explicitly
    if row + 1 < ROWS and grid[row + 1, col] == NO_GAME:
        return True
    return False


def cluster_lines(lines, threshold=20):
    """Clusters nearly overlapping lines."""
    lines = sorted(list(set(lines)))  # Ensure unique and sorted
    if not lines:
        return []
    clustered = [lines[0]]
    for line in lines[1:]:
        # Check absolute difference against the last element of the cluster
        if abs(line - clustered[-1]) > threshold:
            clustered.append(line)
    return clustered


def line_intersection(line1, line2):
    """Finds the intersection of two lines given in the form [[x1, y1, x2, y2]]."""
    x1, y1, x2, y2 = line1[0]
    x3, y3, x4, y4 = line2[0]

    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if denominator == 0:
        return None  # Lines are parallel or coincident

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

    # If intersection is within both line segments
    if 0 <= t <= 1 and 0 <= u <= 1:
        intersect_x = x1 + t * (x2 - x1)
        intersect_y = y1 + t * (y2 - y1)
        return intersect_x, intersect_y

    return None  # Intersection is not within the segments


def detect_cross_in_cell(cell_roi):
    """
    Attempts to detect a cross shape within a cell ROI by finding
    intersecting line segments near the cell center.

    Args:
        cell_roi (np.ndarray): The image region for the cell.

    Returns:
        bool: True if a cross-like shape is detected, False otherwise.
    """
    if cell_roi is None or cell_roi.size == 0:
        return False

    cell_h, cell_w = cell_roi.shape[:2]
    if cell_h == 0 or cell_w == 0:
        return False  # Invalid cell dimensions

    # --- Preprocessing ---
    gray_cell = cv2.cvtColor(cell_roi, cv2.COLOR_BGR2GRAY)
    blurred_cell = cv2.GaussianBlur(gray_cell, (5, 5), 0)
    edges_cell = cv2.Canny(blurred_cell, CROSS_CANNY_LOW, CROSS_CANNY_HIGH)

    # --- Line Detection ---
    lines = cv2.HoughLinesP(
        edges_cell,
        rho=1,
        theta=np.pi / 180,
        threshold=CROSS_HOUGH_THRESHOLD,
        minLineLength=CROSS_HOUGH_MIN_LEN,
        maxLineGap=CROSS_HOUGH_MAX_GAP,
    )

    if lines is None or len(lines) < CROSS_MIN_LINES_BEFORE_FILTER:
        return False  # Not enough lines found initially

    # --- Line Filtering ---
    min_req_length = min(cell_h, cell_w) * CROSS_MIN_LINE_LEN_RATIO
    filtered_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        # Keep lines that are sufficiently long
        if length >= min_req_length:
            # Optional: Add filtering to remove lines too close to the border
            # border_margin = 5 # pixels
            # if x1 > border_margin and x1 < cell_w - border_margin and \
            #    x2 > border_margin and x2 < cell_w - border_margin and \
            #    y1 > border_margin and y1 < cell_h - border_margin and \
            #    y2 > border_margin and y2 < cell_h - border_margin:
            filtered_lines.append(line)

    if len(filtered_lines) < CROSS_MIN_LINES_AFTER_FILTER:
        return False  # Not enough sufficiently long lines (potentially after border filter)

    # --- Intersection Check ---
    cell_center_x, cell_center_y = cell_w / 2.0, cell_h / 2.0
    max_dist_from_center = (
        min(cell_center_x, cell_center_y) * CROSS_CENTER_PROXIMITY_RATIO
    )

    found_central_intersection = False
    for i in range(len(filtered_lines)):
        for j in range(i + 1, len(filtered_lines)):
            intersection_point = line_intersection(filtered_lines[i], filtered_lines[j])

            if intersection_point is not None:
                ix, iy = intersection_point
                # Check if the intersection is close to the cell center
                dist_sq = (ix - cell_center_x) ** 2 + (iy - cell_center_y) ** 2
                if dist_sq < max_dist_from_center**2:
                    # print(f"    CrossDetect: Found central intersection at ({ix:.1f}, {iy:.1f})")
                    found_central_intersection = True
                    break  # Found a valid cross
        if found_central_intersection:
            break

    return found_central_intersection


# --- Main Detection Function ---


def detect_board_change(prev_board):
    """
    Detects changes between a previous board state and a new image file.
    Identifies the newly placed piece (assuming one change) and its type (cross/circle)
    using shape detection (HoughCircles for circles, HoughLinesP for crosses).

    Args:
        prev_board (np.ndarray): The previous state of the board (6x7 NumPy array).
        image_path (str): Path to the image file to analyze.

    Returns:
        tuple: (position_string, is_cross_boolean) or raises ValueError on failure.
               position_string (str): e.g., "A1", "G6".
               is_cross_boolean (bool): True if the detected change is a cross, False otherwise.

    Raises:
        ValueError: If image loading fails, grid detection fails, no changes are found,
                    multiple changes are found, or a floating move is detected.
    """
    new_image = get_picture()
    if new_image is None:
        raise ValueError("Failed to load image.")

    # --- Image Preprocessing ---
    gray = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.Canny(gray, 50, 150)

    # --- Grid Line Detection ---
    lines = cv2.HoughLinesP(
        edges, rho=1, theta=np.pi / 180, threshold=60, minLineLength=60, maxLineGap=20
    )

    if lines is None:
        raise ValueError("No lines detected. Check Canny/Hough parameters.")

    # --- Separate and Cluster Lines ---
    horizontal_lines, vertical_lines = [], []
    img_height, img_width = new_image.shape[:2]
    margin = 5
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if (
            x1 < margin
            or x1 > img_width - margin
            or x2 < margin
            or x2 > img_width - margin
            or y1 < margin
            or y1 > img_height - margin
            or y2 < margin
            or y2 > img_height - margin
        ):
            continue
        angle = np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi
        if abs(angle) < 15 or abs(angle - 180) < 15:  # Horizontal
            horizontal_lines.extend([y1, y2])
        elif abs(abs(angle) - 90) < 15:  # Vertical
            vertical_lines.extend([x1, x2])

    horizontal_lines = cluster_lines(horizontal_lines, threshold=30)
    vertical_lines = cluster_lines(vertical_lines, threshold=30)

    print(f"Detected {len(horizontal_lines)} horizontal line clusters.")
    print(f"Detected {len(vertical_lines)} vertical line clusters.")

    # --- Grid Line Refinement and Validation ---
    horizontal_lines.sort()
    vertical_lines.sort()

    # Refinement logic (heuristic, might need improvement)
    if len(horizontal_lines) > ROWS + 1:
        print(
            f"Warning: Too many horizontal lines ({len(horizontal_lines)}), attempting refinement."
        )
        avg_spacing = (
            (horizontal_lines[-1] - horizontal_lines[0]) / (len(horizontal_lines) - 1)
            if len(horizontal_lines) > 1
            else 0
        )
        refined = [horizontal_lines[0]] if horizontal_lines else []
        for i in range(1, len(horizontal_lines)):
            if (
                avg_spacing == 0
                or horizontal_lines[i] - refined[-1] > avg_spacing * 0.5
            ):
                refined.append(horizontal_lines[i])
        if len(refined) > ROWS + 1:
            print(
                f"Warning: Refinement still resulted in {len(refined)} horizontal lines. Taking best guess."
            )
            horizontal_lines = refined[: ROWS + 1]
        else:
            horizontal_lines = refined
        print(f"Refined horizontal lines: {len(horizontal_lines)}")

    if len(vertical_lines) > COLUMNS + 1:
        print(
            f"Warning: Too many vertical lines ({len(vertical_lines)}), attempting refinement."
        )
        avg_spacing = (
            (vertical_lines[-1] - vertical_lines[0]) / (len(vertical_lines) - 1)
            if len(vertical_lines) > 1
            else 0
        )
        refined = [vertical_lines[0]] if vertical_lines else []
        for i in range(1, len(vertical_lines)):
            if avg_spacing == 0 or vertical_lines[i] - refined[-1] > avg_spacing * 0.5:
                refined.append(vertical_lines[i])
        if len(refined) > COLUMNS + 1:
            print(
                f"Warning: Refinement still resulted in {len(refined)} vertical lines. Taking best guess."
            )
            vertical_lines = refined[: COLUMNS + 1]
        else:
            vertical_lines = refined
        print(f"Refined vertical lines: {len(vertical_lines)}")

    if len(horizontal_lines) != ROWS + 1 or len(vertical_lines) != COLUMNS + 1:
        raise ValueError(
            f"Grid detection failed. Expected {ROWS + 1} H and {COLUMNS + 1} V lines, "
            f"found {len(horizontal_lines)} H and {len(vertical_lines)} V after refinement. "
            "Check image clarity and detection parameters."
        )

    # --- Extract Grid and Analyze Cells ---
    grid = np.full((ROWS, COLUMNS), NO_GAME, dtype=int)
    cell_padding = 8  # Adjust padding if needed

    for i in range(ROWS):  # row index
        for j in range(COLUMNS):  # column index
            if i + 1 >= len(horizontal_lines) or j + 1 >= len(vertical_lines):
                print(
                    f"Warning: Skipping cell ({i},{j}) due to insufficient detected lines."
                )
                continue

            y1_raw, y2_raw = horizontal_lines[i], horizontal_lines[i + 1]
            x1_raw, x2_raw = vertical_lines[j], vertical_lines[j + 1]

            y1 = max(0, int(y1_raw + cell_padding))
            y2 = min(img_height, int(y2_raw - cell_padding))
            x1 = max(0, int(x1_raw + cell_padding))
            x2 = min(img_width, int(x2_raw - cell_padding))

            if y1 >= y2 or x1 >= x2:
                continue

            cell = new_image[y1:y2, x1:x2]
            if cell.size == 0:
                continue

            detected_piece = NO_GAME  # Default assumption

            # --- 1. Attempt Circle Detection ---
            gray_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            blurred_cell = cv2.GaussianBlur(
                gray_cell, (7, 7), 0
            )  # Adjust blur if needed

            circles = cv2.HoughCircles(
                blurred_cell,
                cv2.HOUGH_GRADIENT,
                dp=HC_DP,
                minDist=HC_MIN_DIST,
                param1=HC_PARAM1,
                param2=HC_PARAM2,
                minRadius=HC_MIN_RADIUS,
                maxRadius=HC_MAX_RADIUS,
            )

            if circles is not None:
                # Optional: Add checks for circle size/position relative to cell
                print(f"Detected Circle at cell ({i},{j})")
                detected_piece = PLAYER_HUMAN

            # --- 2. If No Circle, Attempt Cross Detection ---
            if detected_piece == NO_GAME:
                if detect_cross_in_cell(cell):
                    print(f"Detected Cross at cell ({i},{j})")
                    detected_piece = PLAYER_AI

            # --- Assign Cell Value ---
            grid[i, j] = detected_piece

    # --- Compare with Previous Board ---
    prev_board_np = np.array(prev_board)
    if prev_board_np.shape != (ROWS, COLUMNS):
        raise ValueError(
            f"prev_board shape mismatch. Expected ({ROWS},{COLUMNS}), got {prev_board_np.shape}"
        )

    diff = grid - prev_board_np
    changed_cells = np.argwhere(diff != 0)

    # --- Validate Changes ---
    if len(changed_cells) == 0:
        print("Current detected grid:")
        print(grid)
        print("Previous board:")
        print(prev_board_np)
        raise ValueError(
            "No changes detected between previous board and current image."
        )
    elif len(changed_cells) > 1:
        print("Current detected grid:")
        print(grid)
        print("Previous board:")
        print(prev_board_np)
        print("Detected changes at (row, col indices):", changed_cells)
        valid_changes = []
        for r, c in changed_cells:
            if prev_board_np[r, c] == NO_GAME and grid[r, c] != NO_GAME:
                valid_changes.append((r, c))
            else:
                print(
                    f"Warning: Ignoring invalid change at ({r},{c}) from {prev_board_np[r, c]} to {grid[r, c]}"
                )
        if len(valid_changes) == 0:
            raise ValueError(
                "Multiple changes detected, but none were valid (empty to piece)."
            )
        elif len(valid_changes) > 1:
            raise ValueError(
                f"Multiple valid moves detected at {valid_changes}. Only one move per turn allowed."
            )
        else:
            changed_cells = np.array([valid_changes[0]])
            print(
                f"Warning: Multiple differences found, but proceeding with single valid change at {changed_cells[0]}"
            )

    # --- Process the Single Change ---
    row, col = changed_cells[0]
    changed_value = grid[row, col]

    if prev_board_np[row, col] != NO_GAME:
        raise ValueError(
            f"Internal Error: Change processed at ({row},{col}), but previous cell was not empty ({prev_board_np[row, col]})."
        )
    if changed_value == NO_GAME:
        raise ValueError(
            f"Internal Error: Change processed at ({row},{col}), but new cell is empty. Expected a piece."
        )

    is_cross = changed_value == PLAYER_AI

    # --- Check for Floating Move ---
    if is_floating_move(grid, row, col):
        column_letter_float = chr(ord("A") + col)
        row_number_float = row + 1
        raise ValueError(
            f"Floating coin detected at {column_letter_float}{row_number_float}. Invalid move."
        )

    # --- Format Output Coordinates ---
    column_letter = chr(ord("A") + col)
    row_number = row + 1

    position_string = f"{column_letter}{row_number}"

    print(
        f"Change detected at {position_string}. Piece type: {'Cross (AI)' if is_cross else 'Circle (Human)'}"
    )
    print("Final detected grid state:")
    print(grid)

    return position_string, is_cross


# # --- Test Execution Block ---
# if __name__ == "__main__":
#     print("Running test detection...")

#     # --- Test Case Setup ---
#     image_file = r"../img/image.jpeg" # Analyze the image with the circle

#     # Previous board state: Assume 'X' was placed at C5 (row 4, col 2)
#     previous_board_state = np.full((ROWS, COLUMNS), NO_GAME, dtype=int)
#     print(previous_board_state)

#     # --- Run Detection ---
#     print(f"\nAnalyzing image: {image_file}")
#     try:
#         position, is_cross_result = detect_board_change(previous_board_state, image_path=image_file)

#         # --- Report Detection Result ---
#         print("\n--- Detection Result ---")
#         print(f"Detected Change Position: {position}")
#         print(f"Is the new piece a Cross? {is_cross_result}")
#         print("------------------------")

#     except ValueError as e:
#         print(f"\n--- Detection Error ---")
#         print(f"An error occurred: {e}")
#         print("-----------------------")
#     except Exception as e:
#         print(f"\n--- Unexpected Error ---")
#         print(f"An unexpected error occurred: {e}")
#         import traceback
#         traceback.print_exc()
#         print("------------------------")
