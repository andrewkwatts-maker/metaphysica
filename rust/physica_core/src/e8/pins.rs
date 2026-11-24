//! Output pins for `e8_lattice_points`, taken from the pre-split code.

use super::e8_lattice_points;

fn points_hash(v: &[[f64; 8]]) -> u64 {
    let mut h = 0xcbf2_9ce4_8422_2325_u64;
    for p in v {
        for x in p {
            for b in x.to_bits().to_le_bytes() {
                h ^= u64::from(b);
                h = h.wrapping_mul(0x0000_0100_0000_01b3);
            }
        }
    }
    h
}

#[test]
fn radius_sqrt2_is_pinned() {
    let p = e8_lattice_points(2.0_f64.sqrt()).unwrap();
    assert_eq!((p.len(), points_hash(&p)), (241, 15924814606719503141));
}

#[test]
fn radius_two_is_pinned() {
    let p = e8_lattice_points(2.0).unwrap();
    assert_eq!((p.len(), points_hash(&p)), (2401, 4902698809262435877));
}

#[test]
fn radius_zero_is_origin_only() {
    let p = e8_lattice_points(0.0).unwrap();
    assert_eq!(p, vec![[0.0; 8]]);
}

#[test]
fn bad_radius_stays_none() {
    assert!(e8_lattice_points(-1.0).is_none());
    assert!(e8_lattice_points(f64::NAN).is_none());
}
