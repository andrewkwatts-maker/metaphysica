//! Output pins for `adaptive_integrate`, taken from the pre-split code.

use super::{adaptive_integrate, ricci_rhs, StepGrid};

fn fnv(h: &mut u64, x: f64) {
    for b in x.to_bits().to_le_bytes() {
        *h ^= u64::from(b);
        *h = h.wrapping_mul(0x0000_0100_0000_01b3);
    }
}

fn grid_hash(g: &StepGrid) -> u64 {
    let mut h = 0xcbf2_9ce4_8422_2325_u64;
    for t in &g.ts {
        fnv(&mut h, *t);
    }
    for row in g.ys.iter().chain(g.dys.iter()) {
        for v in row {
            fnv(&mut h, *v);
        }
    }
    h
}

#[test]
fn ricci_flow_grid_is_pinned() {
    let rhs = |y: &[f64], z: f64| ricci_rhs(y, z, 24.0);
    let g = adaptive_integrate(&rhs, 0.0, 2.0, vec![1.0], 1e-8);
    assert_eq!((g.ts.len(), grid_hash(&g)), (21, 3807703328446301415));
}

#[test]
fn oscillator_grid_is_pinned() {
    let rhs = |y: &[f64], _t: f64| vec![y[1], -y[0]];
    let g = adaptive_integrate(&rhs, 0.0, 3.0, vec![1.0, 0.0], 1e-6);
    assert_eq!((g.ts.len(), grid_hash(&g)), (19, 5793007783184762214));
}
