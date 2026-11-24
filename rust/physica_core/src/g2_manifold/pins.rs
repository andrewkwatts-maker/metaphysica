//! Output pins for `flat_torus_dirac_spectrum`, taken from the pre-split code.

use super::flat_torus_dirac_spectrum;

fn spectrum_hash(v: &[f64]) -> u64 {
    let mut h = 0xcbf2_9ce4_8422_2325_u64;
    for x in v {
        for b in x.to_bits().to_le_bytes() {
            h ^= u64::from(b);
            h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
    }
    h
}

#[test]
fn rectangular_torus_is_pinned() {
    let s = flat_torus_dirac_spectrum(&[1.0, 2.0], 3).unwrap();
    assert_eq!((s.len(), spectrum_hash(&s)), (58, 11371560629488352141));
}

#[test]
fn four_torus_with_spinor_repeats_is_pinned() {
    let s = flat_torus_dirac_spectrum(&[1.0, 1.5, 2.0, 0.5], 1).unwrap();
    assert_eq!((s.len(), spectrum_hash(&s)), (124, 13153933347177639957));
}

#[test]
fn rejected_requests_stay_none() {
    assert!(flat_torus_dirac_spectrum(&[], 1).is_none());
    assert!(flat_torus_dirac_spectrum(&[1.0, -1.0], 1).is_none());
    assert!(flat_torus_dirac_spectrum(&[1.0; 3], 400).is_none());
}
