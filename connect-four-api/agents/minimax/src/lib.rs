use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

const ROWS: usize = 6;
const COLS: usize = 7;

#[pyfunction]
fn get_best_move(board: Vec<Vec<i32>>, depth: usize) -> PyResult<String> {
    // Validate the board dimensions.
    assert_eq!(board.len(), ROWS);
    for row in &board {
        assert_eq!(row.len(), COLS);
    }

    let best_col = minimax_decision(&board, depth);
    let best_col_char = (b'A' + best_col as u8) as char;
    Ok(best_col_char.to_string())
}

fn minimax_decision(board: &Vec<Vec<i32>>, depth: usize) -> usize {
    let possible_moves = get_valid_moves(board);
    let mut best_score = i32::MIN;
    let mut best_move = 0;
    let mut alpha = i32::MIN;
    let beta = i32::MAX;

    let mut scored_moves: Vec<(i32, usize)> = possible_moves
        .iter()
        .map(|&col| {
            let mut new_board = board.clone();
            drop_piece(&mut new_board, col, 1);
            (score_position(&new_board, 1), col)
        })
        .collect();

    scored_moves.sort_by(|a, b| b.0.cmp(&a.0));

    for (_, col) in scored_moves {
        let mut new_board = board.clone();
        drop_piece(&mut new_board, col, 1);
        let score = minimax(&new_board, depth - 1, alpha, beta, false);

        if score > best_score {
            best_score = score;
            best_move = col;
        }
        if score > alpha {
            alpha = score;
        }
    }

    best_move
}

fn minimax(
    board: &Vec<Vec<i32>>,
    depth: usize,
    mut alpha: i32,
    mut beta: i32,
    maximizing_player: bool,
) -> i32 {
    if is_terminal_node(board) {
        if check_win(board, 1) {
            return 1_000_000_000;
        } else if check_win(board, 2) {
            return -1_000_000_000;
        } else {
            return 0;
        }
    }

    if depth == 0 {
        let current_player = if maximizing_player { 1 } else { 2 };
        return score_position(board, current_player);
    }

    let possible_moves = get_valid_moves(board);
    if possible_moves.is_empty() {
        return 0;
    }

    if maximizing_player {
        let mut value = i32::MIN;
        for &col in &possible_moves {
            let mut new_board = board.clone();
            drop_piece(&mut new_board, col, 1);
            let new_score = minimax(&new_board, depth - 1, alpha, beta, false);
            value = value.max(new_score);
            alpha = alpha.max(value);
            if alpha >= beta {
                break;
            }
        }
        value
    } else {
        let mut value = i32::MAX;
        for &col in &possible_moves {
            let mut new_board = board.clone();
            drop_piece(&mut new_board, col, 2);
            let new_score = minimax(&new_board, depth - 1, alpha, beta, true);
            value = value.min(new_score);
            beta = beta.min(value);
            if beta <= alpha {
                break;
            }
        }
        value
    }
}

fn get_valid_moves(board: &Vec<Vec<i32>>) -> Vec<usize> {
    let mut moves = Vec::new();
    for col in 0..COLS {
        if board[0][col] == 0 {
            moves.push(col);
        }
    }
    moves
}

fn drop_piece(board: &mut Vec<Vec<i32>>, col: usize, player: i32) {
    for row in (0..ROWS).rev() {
        if board[row][col] == 0 {
            board[row][col] = player;
            break;
        }
    }
}

fn is_terminal_node(board: &Vec<Vec<i32>>) -> bool {
    check_win(board, 1) || check_win(board, 2) || get_valid_moves(board).is_empty()
}

fn check_win(board: &Vec<Vec<i32>>, player: i32) -> bool {
    for r in 0..ROWS {
        for c in 0..(COLS - 3) {
            if board[r][c] == player
                && board[r][c + 1] == player
                && board[r][c + 2] == player
                && board[r][c + 3] == player
            {
                return true;
            }
        }
    }

    for c in 0..COLS {
        for r in 0..(ROWS - 3) {
            if board[r][c] == player
                && board[r + 1][c] == player
                && board[r + 2][c] == player
                && board[r + 3][c] == player
            {
                return true;
            }
        }
    }

    for r in 0..(ROWS - 3) {
        for c in 0..(COLS - 3) {
            if board[r][c] == player
                && board[r + 1][c + 1] == player
                && board[r + 2][c + 2] == player
                && board[r + 3][c + 3] == player
            {
                return true;
            }
        }
    }

    for r in 3..ROWS {
        for c in 0..(COLS - 3) {
            if board[r][c] == player
                && board[r - 1][c + 1] == player
                && board[r - 2][c + 2] == player
                && board[r - 3][c + 3] == player
            {
                return true;
            }
        }
    }

    false
}

fn score_position(board: &Vec<Vec<i32>>, player: i32) -> i32 {
    let mut score = 0;

    let center_col = COLS / 2;
    let mut center_count = 0;
    for r in 0..ROWS {
        if board[r][center_col] == player {
            center_count += 1;
        }
    }
    score += center_count * 3;

    for r in 0..ROWS {
        for c in 0..(COLS - 3) {
            let window = &board[r][c..c + 4];
            score += evaluate_window(window, player);
        }
    }

    for c in 0..COLS {
        for r in 0..(ROWS - 3) {
            let mut window = vec![];
            for i in 0..4 {
                window.push(board[r + i][c]);
            }
            score += evaluate_window(&window, player);
        }
    }

    for r in 0..(ROWS - 3) {
        for c in 0..(COLS - 3) {
            let mut window = vec![];
            for i in 0..4 {
                window.push(board[r + i][c + i]);
            }
            score += evaluate_window(&window, player);
        }
    }

    for r in 3..ROWS {
        for c in 0..(COLS - 3) {
            let mut window = vec![];
            for i in 0..4 {
                window.push(board[r - i][c + i]);
            }
            score += evaluate_window(&window, player);
        }
    }

    score
}

fn evaluate_window(window: &[i32], player: i32) -> i32 {
    let mut score = 0;
    let opponent = if player == 1 { 2 } else { 1 };

    let player_count = window.iter().filter(|&&x| x == player).count();
    let empty_count = window.iter().filter(|&&x| x == 0).count();
    let opponent_count = window.iter().filter(|&&x| x == opponent).count();

    if player_count == 4 {
        score += 100;
    } else if player_count == 3 && empty_count == 1 {
        score += 5;
    } else if player_count == 2 && empty_count == 2 {
        score += 2;
    }

    if opponent_count == 3 && empty_count == 1 {
        score -= 4;
    }

    score
}

#[pymodule]
fn minimax_algorithm(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_best_move, m)?)?;
    Ok(())
}
