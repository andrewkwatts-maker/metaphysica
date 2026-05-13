//====== Metaphysica/rust/physica_core/src/simulations.rs ======//
//!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
//!
//!This is the intellectual property of Andrew Keith Watts. Unauthorized
//!reproduction, distribution, or modification of this code, in whole or in part,
//!without the express written permission of Andrew Keith Watts is strictly prohibited.
//!
//!For inquiries, please contact AndrewKWatts@Gmail.com

//! Temporal-sync simulation (RK4) over the 24-pin torsion cage.
//!
//! Ports `simulations/PM/paper/appendices/appendix_l_omega_unwinding.py`.
//! Per-frame caller in pt-physica drives `step()`; longer-running batch
//! analyses go through `simulate_temporal_sync()`.
//!
//! Wave-1: data shapes plus a no-op stepper that preserves the state.
//! Real RK4 lands in Wave-5.

use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Errors from the temporal simulator.
#[derive(Debug, Error)]
pub enum SimulationError {
    /// Step size must be strictly positive.
    #[error("invalid step_size = {0}")]
    InvalidStepSize(f64),

    /// Iteration cap must be ≥ 1.
    #[error("invalid max_iterations = {0}")]
    InvalidMaxIterations(usize),

    /// Caller-supplied state had the wrong dimensionality.
    #[error("state vector wrong length: expected {expected}, got {got}")]
    DimensionMismatch { expected: usize, got: usize },
}

/// Number of pins on the torsion cage (24-pin geometry).
pub const PIN_COUNT: usize = 24;

/// State of the temporal-sync system at one tick.
///
/// Indexed by pin position `0..PIN_COUNT`; `phases` and `momenta` are kept
/// separate (vs. one packed state vector) so RK4 can operate on either with
/// rayon-parallel inner loops.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TemporalState {
    /// Current simulation time in seconds.
    pub t: f64,
    /// Pin phases θ_i in radians. Length = `PIN_COUNT`.
    pub phases: Vec<f64>,
    /// Pin angular momenta p_i (conjugate to `phases`). Length = `PIN_COUNT`.
    pub momenta: Vec<f64>,
}

impl TemporalState {
    /// Construct a zero-initialised state at t = 0.
    #[must_use]
    pub fn zero() -> Self {
        Self {
            t: 0.0,
            phases: vec![0.0; PIN_COUNT],
            momenta: vec![0.0; PIN_COUNT],
        }
    }

    /// Validate vector lengths match `PIN_COUNT`.
    pub fn validate(&self) -> Result<(), SimulationError> {
        if self.phases.len() != PIN_COUNT {
            return Err(SimulationError::DimensionMismatch {
                expected: PIN_COUNT,
                got: self.phases.len(),
            });
        }
        if self.momenta.len() != PIN_COUNT {
            return Err(SimulationError::DimensionMismatch {
                expected: PIN_COUNT,
                got: self.momenta.len(),
            });
        }
        Ok(())
    }
}

/// RK4 driver over [`TemporalState`].
#[derive(Debug, Clone, Copy)]
pub struct TemporalSimulator {
    /// Integration step in seconds.
    pub step_size: f64,
    /// Hard upper bound on iterations per simulation call.
    pub max_iterations: usize,
}

impl TemporalSimulator {
    /// Construct with explicit parameters; rejects non-positive step or zero
    /// iteration cap so all subsequent loops have fixed bounds.
    pub fn new(step_size: f64, max_iterations: usize) -> Result<Self, SimulationError> {
        if !(step_size > 0.0) {
            return Err(SimulationError::InvalidStepSize(step_size));
        }
        if max_iterations == 0 {
            return Err(SimulationError::InvalidMaxIterations(max_iterations));
        }
        Ok(Self {
            step_size,
            max_iterations,
        })
    }

    /// Sane defaults for engine per-frame ticking.
    #[must_use]
    pub fn default_engine() -> Self {
        Self {
            step_size: 1.0e-3,
            max_iterations: 10_000,
        }
    }
}

/// Run the temporal-sync simulation for `duration` seconds.
///
/// Wave-1 stub: validates inputs and advances `t`; pin state is unchanged.
pub fn simulate_temporal_sync(
    sim: &TemporalSimulator,
    initial: TemporalState,
    duration: f64,
) -> Result<TemporalState, SimulationError> {
    initial.validate()?;
    if !(duration >= 0.0) {
        return Err(SimulationError::InvalidStepSize(duration));
    }
    let n_steps = ((duration / sim.step_size).ceil() as usize).min(sim.max_iterations);
    let mut state = initial;
    for _ in 0..n_steps {
        state.t += sim.step_size;
        // Wave-5: RK4 update of phases & momenta over the 24-pin cage.
    }
    Ok(state)
}

/// Run the Ω-unwinding trajectory analysis (basin-of-attraction sweep).
///
/// Wave-1 stub: returns the zero state. Real analysis lands in Wave-5.
#[must_use]
pub fn simulate_unwinding_trajectory() -> TemporalState {
    TemporalState::zero()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn zero_state_validates() {
        assert!(TemporalState::zero().validate().is_ok());
    }

    #[test]
    fn invalid_step_size_rejected() {
        let err = TemporalSimulator::new(0.0, 100).unwrap_err();
        matches!(err, SimulationError::InvalidStepSize(_));
    }

    #[test]
    fn zero_iterations_rejected() {
        let err = TemporalSimulator::new(1e-3, 0).unwrap_err();
        matches!(err, SimulationError::InvalidMaxIterations(_));
    }

    #[test]
    fn simulate_advances_time() {
        let sim = TemporalSimulator::default_engine();
        let s0 = TemporalState::zero();
        let s1 = simulate_temporal_sync(&sim, s0, 1e-3).unwrap();
        assert!(s1.t > 0.0);
    }
}
