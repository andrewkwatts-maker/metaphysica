//! Output pins for the expression tokenizer, taken from the pre-split code.

use super::{tokenize, Tok};
use crate::constants::ConstantError;

fn detail(r: Result<Vec<Tok>, ConstantError>) -> String {
    match r {
        Err(ConstantError::BadExpression { detail, .. }) => detail,
        other => format!("unexpected: {other:?}"),
    }
}

#[test]
fn tokenizes_every_token_kind() {
    let toks = tokenize("3.5e-2 + x_1*(2 - .5)/Y2E+1e3 - 7.").unwrap();
    let want = vec![
        Tok::Num(3.5e-2),
        Tok::Plus,
        Tok::Ident("x_1".to_string()),
        Tok::Star,
        Tok::LParen,
        Tok::Num(2.0),
        Tok::Minus,
        Tok::Num(0.5),
        Tok::RParen,
        Tok::Slash,
        Tok::Ident("Y2E".to_string()),
        Tok::Plus,
        Tok::Num(1000.0),
        Tok::Minus,
        Tok::Num(7.0),
    ];
    assert_eq!(toks, want);
}

#[test]
fn number_edge_cases_split_as_before() {
    let toks = tokenize("1.2.3 4e5e6 9E+2").unwrap();
    let want = vec![
        Tok::Num(1.2),
        Tok::Num(0.3),
        Tok::Num(400_000.0),
        Tok::Ident("e6".to_string()),
        Tok::Num(900.0),
    ];
    assert_eq!(toks, want);
}

#[test]
fn rejects_unknown_character() {
    assert_eq!(detail(tokenize("1 + $")), "unexpected character `$` at 4");
}

#[test]
fn rejects_bad_number() {
    assert_eq!(detail(tokenize("1e")), "bad number `1e`");
    assert_eq!(detail(tokenize(".")), "bad number `.`");
}
