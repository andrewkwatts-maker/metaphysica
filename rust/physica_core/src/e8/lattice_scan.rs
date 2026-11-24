//! Odometer helpers for the E8 lattice-point enumeration.

use super::{LATTICE_COORD_CAP, NORM_SQ_TOL};

/// Per-axis coordinate bound for `radius`, clamped to [`LATTICE_COORD_CAP`].
///
/// Saturating cast: a huge radius clamps to the cap, which is what the
/// Python's `min(..., 3)` does too.
pub(super) fn coordinate_bound(radius: f64) -> i32 {
    let bound = (radius.ceil() as i64 + 1).min(i64::from(LATTICE_COORD_CAP)) as i32;
    debug_assert!(
        bound >= 1,
        "the bound must admit at least the origin's neighbours"
    );
    debug_assert!(
        bound <= LATTICE_COORD_CAP,
        "the coordinate bound escaped its cap"
    );
    bound
}

/// Squared-norm acceptance threshold for `radius`, with the Python's slack.
pub(super) fn radius_sq_threshold(radius: f64) -> f64 {
    radius * radius + NORM_SQ_TOL
}

/// Test the odometer position against both E8 cosets.
///
/// Returns `(integer_hit, half_integer_hit)`; each is `Some(point)` when the
/// coordinate sum is even and the point lies inside the ball `r_sq`.
pub(super) fn classify_position(
    digits: &[usize; 8],
    bound: i32,
    r_sq: f64,
) -> (Option<[f64; 8]>, Option<[f64; 8]>) {
    let mut coord_sum = 0_i32;
    let mut norm_sq = 0.0_f64;
    let mut half_norm_sq = 0.0_f64;
    let mut v = [0.0_f64; 8];
    for k in 0..8 {
        let n = digits[k] as i32 - bound;
        coord_sum += n;
        let x = f64::from(n);
        v[k] = x;
        norm_sq += x * x;
        let xh = x + 0.5;
        half_norm_sq += xh * xh;
    }
    // Sum(n_i + 1/2) = Sum(n_i) + 4, so both cosets test the same parity.
    if coord_sum % 2 != 0 {
        return (None, None);
    }
    let integer_hit = (norm_sq <= r_sq).then_some(v);
    let half_hit = (half_norm_sq <= r_sq).then(|| {
        let mut h = v;
        for c in &mut h {
            *c += 0.5;
        }
        h
    });
    (integer_hit, half_hit)
}

/// Increment the odometer, last coordinate fastest, wrapping at `side`.
pub(super) fn advance_odometer(digits: &mut [usize; 8], side: usize) {
    for digit in digits.iter_mut().rev() {
        *digit += 1;
        if *digit < side {
            break;
        }
        *digit = 0;
    }
}
