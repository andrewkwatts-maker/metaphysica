//====== Metaphysica/rust/physica_core/src/gates.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! 28-bit Sheffer-stroke logic-closure gate evaluator.
//!
//! Ports the Python `gate_28` evaluator. **The Python version is recursive;
//! the Rust port is mandatorily *iterative*** — see plan §D.2 #4 — so deep
//! traversals on the 288-pin lattice cannot blow the stack.
//!
//! Wave-1: the iterative skeleton is in place. The transition function is a
//! pass-through identity until the real Sheffer-stroke kernel lands in Wave-5.

use thiserror::Error;

/// Errors from gate evaluation.
#[derive(Debug, Error)]
pub enum GateError {
    /// `max_depth` was exceeded before convergence.
    #[error("gate_28 exceeded max_depth = {0} without convergence")]
    DepthExceeded(usize),

    /// `max_depth` of zero is invalid (no work would be done).
    #[error("max_depth must be ≥ 1, got {0}")]
    InvalidDepth(usize),
}

/// Width of the lattice — fixed at 288 (= `LOGIC_CLOSURE`).
pub const LATTICE_WIDTH: usize = 288;

/// Iterative 28-bit gate evaluator.
///
/// **Iterative, not recursive** (per plan §D.2 #4 and the Power-of-Ten
/// safety-critical rule "avoid recursion"): walks the 288-element state
/// using an explicit work stack and a fixed-bound iteration count. Returns
/// `DepthExceeded` if `max_depth` is reached without the state stabilising.
///
/// Wave-1 stub: copies `initial_state` into the working buffer and returns
/// it after one trivial pass. The real Sheffer-stroke transition lands in
/// Wave-5.
pub fn gate_28_iterative(
    initial_state: [u32; LATTICE_WIDTH],
    max_depth: usize,
) -> Result<[u32; LATTICE_WIDTH], GateError> {
    if max_depth == 0 {
        return Err(GateError::InvalidDepth(max_depth));
    }

    let current: [u32; LATTICE_WIDTH] = initial_state;
    let mut work_stack: Vec<usize> = Vec::with_capacity(LATTICE_WIDTH);
    work_stack.extend(0..LATTICE_WIDTH);

    let mut iter = 0usize;
    while let Some(_idx) = work_stack.pop() {
        // Wave-5 will compute next_state[idx] = sheffer_28(current, idx)
        // and push its dependents back on the stack if it changed.
        // For wave-1 we just bound the loop and pass through.
        iter += 1;
        if iter >= max_depth {
            return Err(GateError::DepthExceeded(max_depth));
        }
    }

    Ok(current)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lattice_width_matches_logic_closure() {
        assert_eq!(LATTICE_WIDTH, 288);
    }

    #[test]
    fn empty_pass_returns_initial_state() {
        let init = [0u32; LATTICE_WIDTH];
        let out = gate_28_iterative(init, LATTICE_WIDTH + 1).unwrap();
        assert_eq!(out, init);
    }

    #[test]
    fn zero_depth_rejected() {
        let init = [0u32; LATTICE_WIDTH];
        let err = gate_28_iterative(init, 0).unwrap_err();
        matches!(err, GateError::InvalidDepth(_));
    }

    #[test]
    fn small_depth_exceeds_before_completion() {
        let init = [0u32; LATTICE_WIDTH];
        let err = gate_28_iterative(init, 1).unwrap_err();
        matches!(err, GateError::DepthExceeded(_));
    }
}
