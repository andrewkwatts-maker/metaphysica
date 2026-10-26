use super::*;

fn flat(gs: &[Iso]) -> Vec<i64> {
    gs.iter().flat_map(|g| g.to_row()).collect()
}

fn flip_four() -> Iso {
    let mut g = Iso::identity();
    for i in 0..4 {
        g.m[i][i] = -1;
    }
    g
}

#[test]
fn z2_on_four_coordinates_gives_sixteen_a1_loci() {
    let g = close_group_rows(&flat(&[flip_four()]), 10).unwrap();
    let v: Value = serde_json::from_str(&analyse_rows(&g, 1).unwrap()).unwrap();
    assert_eq!(v["order"], 2);
    assert_eq!(v["n_loci"], 16);
    let strata = v["strata"].as_array().unwrap();
    assert_eq!(strata.len(), 16);
    assert!(strata.iter().all(|s| s["label"] == "A1" && s["betti"] == json!([1, 3, 3, 1])));
    assert_eq!(v["flat_betti"], json!([1, 3, 9, 19, 19, 9, 3, 1]));
}

#[test]
fn bad_buffer_length_is_rejected() {
    assert!(analyse_rows(&[1, 2, 3], 1).is_err());
}
