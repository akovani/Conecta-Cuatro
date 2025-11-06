use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use rand::seq::SliceRandom;
use rand::thread_rng;

const ROWS: usize = 6;
const COLS: usize = 7;

#[derive(Clone)]
struct BoardState {
    board: Vec<Vec<i32>>,
    current_player: i32,
}

impl BoardState {
    fn new() -> Self {
        BoardState {
            board: vec![vec![0; COLS]; ROWS],
            current_player: 1,
        }
    }

    fn clone_with_move(&self, col: usize) -> Self {
        let mut new_state = self.clone();
        new_state.drop_piece(col);
        new_state.current_player = if self.current_player == 1 { 2 } else { 1 };
        new_state
    }

    fn drop_piece(&mut self, col: usize) {
        for row in (0..ROWS).rev() {
            if self.board[row][col] == 0 {
                self.board[row][col] = self.current_player;
                break;
            }
        }
    }

    fn get_valid_moves(&self) -> Vec<usize> {
        (0..COLS).filter(|&col| self.board[0][col] == 0).collect()
    }

    fn is_terminal(&self) -> bool {
        self.check_win(1) || self.check_win(2) || self.get_valid_moves().is_empty()
    }

    fn check_win(&self, player: i32) -> bool {
        for r in 0..ROWS {
            for c in 0..COLS - 3 {
                if (0..4).all(|i| self.board[r][c + i] == player) {
                    return true;
                }
            }
        }

        for c in 0..COLS {
            for r in 0..ROWS - 3 {
                if (0..4).all(|i| self.board[r + i][c] == player) {
                    return true;
                }
            }
        }

        for r in 0..ROWS - 3 {
            for c in 0..COLS - 3 {
                if (0..4).all(|i| self.board[r + i][c + i] == player) {
                    return true;
                }
            }
        }

        for r in 3..ROWS {
            for c in 0..COLS - 3 {
                if (0..4).all(|i| self.board[r - i][c + i] == player) {
                    return true;
                }
            }
        }

        false
    }

    fn evaluate_board(&self, player: i32) -> f64 {
        let opponent = if player == 1 { 2 } else { 1 };

        let player_potential = self.count_potential_wins(player);
        let opponent_potential = self.count_potential_wins(opponent);

        let player_center_control = self.center_column_control(player);
        let opponent_center_control = self.center_column_control(opponent);

        player_potential as f64 - opponent_potential as f64 + (player_center_control * 0.5)
            - (opponent_center_control * 0.5)
    }

    fn count_potential_wins(&self, player: i32) -> i32 {
        let mut potential_wins = 0;

        for r in 0..ROWS {
            for c in 0..COLS - 3 {
                let window: Vec<i32> = (0..4).map(|i| self.board[r][c + i]).collect();
                if is_potential_win(&window, player) {
                    potential_wins += 1;
                }
            }
        }

        potential_wins
    }

    fn center_column_control(&self, player: i32) -> f64 {
        let center_cols = [2, 3, 4];
        center_cols
            .iter()
            .map(|&col| {
                let pieces_in_col = (0..ROWS)
                    .filter(|&row| self.board[row][col] == player)
                    .count() as f64;
                pieces_in_col / ROWS as f64
            })
            .sum()
    }
}

fn is_potential_win(window: &[i32], player: i32) -> bool {
    let player_count = window.iter().filter(|&&x| x == player).count();
    let empty_count = window.iter().filter(|&&x| x == 0).count();
    player_count > 0 && empty_count > 0 && player_count + empty_count == 4
}

struct MCTSNode {
    state: BoardState,
    visits: usize,
    wins: f64,
    parent: Option<*mut MCTSNode>,
    children: Vec<MCTSNode>,
    untried_moves: Vec<usize>,
    chosen_move: Option<usize>,
}

impl MCTSNode {
    fn new(state: BoardState) -> Self {
        MCTSNode {
            untried_moves: state.get_valid_moves(),
            state,
            visits: 0,
            wins: 0.0,
            parent: None,
            children: Vec::new(),
            chosen_move: None,
        }
    }

    fn uct_score(&self, parent_visits: usize, exploration_constant: f64) -> f64 {
        if self.visits == 0 {
            f64::INFINITY
        } else {
            let win_rate = self.wins / self.visits as f64;
            let exploration = (parent_visits as f64).ln() / self.visits as f64;
            win_rate + exploration_constant * exploration.sqrt()
        }
    }
}

fn mcts(root_state: &BoardState, simulation_count: usize, exploration_constant: f64) -> usize {
    let mut root = MCTSNode::new(root_state.clone());

    for _ in 0..simulation_count {
        let mut node = select_and_expand(&mut root, exploration_constant);
        let result = simulate(&node.state);
        backpropagate(&mut node, result);
    }

    root.children
        .iter()
        .max_by_key(|child| child.visits)
        .and_then(|child| child.chosen_move)
        .unwrap_or_else(|| root_state.get_valid_moves()[0])
}

fn select_and_expand(node: &mut MCTSNode, exploration_constant: f64) -> &mut MCTSNode {
    let mut current_node = node;
    while !current_node.state.is_terminal() {
        if !current_node.untried_moves.is_empty() {
            let move_index = current_node.untried_moves.pop().unwrap();
            let new_state = current_node.state.clone_with_move(move_index);

            let mut child = MCTSNode::new(new_state);
            child.parent = Some(current_node as *mut MCTSNode);
            child.chosen_move = Some(move_index);

            current_node.children.push(child);

            return current_node.children.last_mut().unwrap();
        } else {
            let best_child_index = current_node
                .children
                .iter_mut()
                .enumerate()
                .max_by(|(_, a), (_, b)| {
                    a.uct_score(current_node.visits, exploration_constant)
                        .partial_cmp(&b.uct_score(current_node.visits, exploration_constant))
                        .unwrap()
                })
                .map(|(index, _)| index);

            if let Some(index) = best_child_index {
                current_node = &mut current_node.children[index];
            } else {
                break;
            }
        }
    }
    current_node
}

fn simulate(state: &BoardState) -> f64 {
    let mut current_state = state.clone();

    while !current_state.is_terminal() {
        let valid_moves = current_state.get_valid_moves();
        if valid_moves.is_empty() {
            break;
        }

        let strategic_moves: Vec<usize> = valid_moves
            .clone()
            .into_iter()
            .filter(|&col| is_strategic_move(&current_state, col))
            .collect();

        let chosen_move = if !strategic_moves.is_empty() {
            *strategic_moves.choose(&mut thread_rng()).unwrap()
        } else {
            *valid_moves.choose(&mut thread_rng()).unwrap()
        };

        current_state = current_state.clone_with_move(chosen_move);
    }

    if current_state.check_win(1) {
        1.0
    } else if current_state.check_win(2) {
        0.0
    } else {
        0.5 // Draw
    }
}

fn is_strategic_move(state: &BoardState, col: usize) -> bool {
    let center_cols = [2, 3, 4];

    let mut test_state = state.clone();
    test_state.drop_piece(col);

    if test_state.check_win(test_state.current_player) {
        return true;
    }

    center_cols.contains(&col)
}

fn backpropagate(node: &mut MCTSNode, result: f64) {
    let mut current = node;
    loop {
        current.visits += 1;
        current.wins += result;
        unsafe {
            if let Some(parent_ptr) = current.parent {
                current = &mut *parent_ptr;
            } else {
                break;
            }
        }
    }
}

#[pyfunction]
fn get_best_move_mcts(
    board: Vec<Vec<i32>>,
    simulation_count: usize,
    exploration_constant: f64,
) -> PyResult<String> {
    let root_state = BoardState {
        board,
        current_player: 1,
    };

    let best_col = mcts(&root_state, simulation_count, exploration_constant);
    let best_col_char = (b'A' + best_col as u8) as char;
    Ok(best_col_char.to_string())
}

#[pymodule]
fn monte_carlo_tree_search(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_best_move_mcts, m)?)?;
    Ok(())
}
