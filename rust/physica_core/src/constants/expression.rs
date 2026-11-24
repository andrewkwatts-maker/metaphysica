//! Closed-micro-language expression evaluator used by `FormulasRegistry`.

use super::{ConstantError, FormulasRegistry};

// ─── Mini expression evaluator ────────────────────────────────────────────
//
// Minimal infix evaluator supporting `+ - * /`, parenthesised sub-expressions,
// numeric literals, and unqualified constant names that resolve through the
// registry. Deliberately a closed micro-language (NOT a general parser) so
// `derive()` remains deterministic, bounded, and safe per CLAUDE.md §10
// (no eval-of-arbitrary-strings, only this dedicated walker).

/// Public entry point so unit tests / quark module can reuse the evaluator.
pub fn evaluate_expression(
    src: &str,
    registry: &FormulasRegistry,
    visiting: &mut Vec<String>,
) -> Result<f64, ConstantError> {
    debug_assert!(!src.is_empty());
    let tokens = tokenize(src)?;
    debug_assert!(
        !tokens.is_empty(),
        "expression tokenized to nothing: `{src}`"
    );
    let mut parser = Parser { tokens, pos: 0 };
    let v = parser.parse_expr(registry, visiting)?;
    if parser.pos != parser.tokens.len() {
        return Err(ConstantError::BadExpression {
            name: src.to_string(),
            detail: format!("trailing tokens at pos {}", parser.pos),
        });
    }
    Ok(v)
}

#[derive(Debug, Clone, PartialEq)]
enum Tok {
    Num(f64),
    Ident(String),
    Plus,
    Minus,
    Star,
    Slash,
    LParen,
    RParen,
}

/// Single-character operator or bracket token for `c`, if it is one.
fn punctuation_token(c: char) -> Option<Tok> {
    match c {
        '+' => Some(Tok::Plus),
        '-' => Some(Tok::Minus),
        '*' => Some(Tok::Star),
        '/' => Some(Tok::Slash),
        '(' => Some(Tok::LParen),
        ')' => Some(Tok::RParen),
        _ => None,
    }
}

/// Scan a numeric literal starting at `*i` (a digit or `.`); advances `*i`.
fn scan_number(chars: &[char], i: &mut usize, src: &str) -> Result<Tok, ConstantError> {
    let start = *i;
    let mut saw_dot = chars[start] == '.';
    let mut saw_exp = false;
    *i += 1;
    while *i < chars.len() {
        let n = chars[*i];
        if n.is_ascii_digit() {
            *i += 1;
        } else if n == '.' && !saw_dot && !saw_exp {
            saw_dot = true;
            *i += 1;
        } else if (n == 'e' || n == 'E') && !saw_exp {
            saw_exp = true;
            *i += 1;
            if *i < chars.len() && (chars[*i] == '+' || chars[*i] == '-') {
                *i += 1;
            }
        } else {
            break;
        }
    }
    let lit: String = chars[start..*i].iter().collect();
    let v: f64 = lit.parse().map_err(|_| ConstantError::BadExpression {
        name: src.to_string(),
        detail: format!("bad number `{lit}`"),
    })?;
    Ok(Tok::Num(v))
}

/// Scan an identifier starting at `*i` (a letter or `_`); advances `*i`.
fn scan_ident(chars: &[char], i: &mut usize) -> Tok {
    let start = *i;
    *i += 1;
    while *i < chars.len() && (chars[*i].is_ascii_alphanumeric() || chars[*i] == '_') {
        *i += 1;
    }
    Tok::Ident(chars[start..*i].iter().collect())
}

/// Scan the token starting at `*i` (non-whitespace); advances `*i` past it.
fn next_token(chars: &[char], i: &mut usize, src: &str) -> Result<Tok, ConstantError> {
    let c = chars[*i];
    if let Some(tok) = punctuation_token(c) {
        *i += 1;
        return Ok(tok);
    }
    if c.is_ascii_digit() || c == '.' {
        return scan_number(chars, i, src);
    }
    if c.is_ascii_alphabetic() || c == '_' {
        return Ok(scan_ident(chars, i));
    }
    Err(ConstantError::BadExpression {
        name: src.to_string(),
        detail: format!("unexpected character `{c}` at {}", *i),
    })
}

fn tokenize(src: &str) -> Result<Vec<Tok>, ConstantError> {
    debug_assert!(!src.is_empty());
    let mut out: Vec<Tok> = Vec::with_capacity(src.len());
    let bytes: Vec<char> = src.chars().collect();
    let mut i = 0usize;
    let max_iter = bytes.len() + 1; // Bounded loop (CLAUDE.md safety §2).
    let mut guard = 0usize;
    while i < bytes.len() {
        guard += 1;
        if guard > max_iter * 4 {
            return Err(ConstantError::BadExpression {
                name: src.to_string(),
                detail: "tokenizer runaway".to_string(),
            });
        }
        if bytes[i].is_whitespace() {
            i += 1;
            continue;
        }
        out.push(next_token(&bytes, &mut i, src)?);
    }
    Ok(out)
}

struct Parser {
    tokens: Vec<Tok>,
    pos: usize,
}

impl Parser {
    fn peek(&self) -> Option<&Tok> {
        self.tokens.get(self.pos)
    }
    fn advance(&mut self) -> Option<Tok> {
        let t = self.tokens.get(self.pos).cloned();
        if t.is_some() {
            self.pos += 1;
        }
        t
    }

    fn parse_expr(
        &mut self,
        reg: &FormulasRegistry,
        visiting: &mut Vec<String>,
    ) -> Result<f64, ConstantError> {
        let mut lhs = self.parse_term(reg, visiting)?;
        let max_steps = self.tokens.len() + 1;
        let mut iter = 0usize;
        while iter < max_steps {
            iter += 1;
            match self.peek() {
                Some(Tok::Plus) => {
                    self.advance();
                    let rhs = self.parse_term(reg, visiting)?;
                    lhs += rhs;
                }
                Some(Tok::Minus) => {
                    self.advance();
                    let rhs = self.parse_term(reg, visiting)?;
                    lhs -= rhs;
                }
                _ => break,
            }
        }
        debug_assert!(iter <= max_steps);
        Ok(lhs)
    }

    fn parse_term(
        &mut self,
        reg: &FormulasRegistry,
        visiting: &mut Vec<String>,
    ) -> Result<f64, ConstantError> {
        let mut lhs = self.parse_factor(reg, visiting)?;
        let max_steps = self.tokens.len() + 1;
        let mut iter = 0usize;
        while iter < max_steps {
            iter += 1;
            match self.peek() {
                Some(Tok::Star) => {
                    self.advance();
                    let rhs = self.parse_factor(reg, visiting)?;
                    lhs *= rhs;
                }
                Some(Tok::Slash) => {
                    self.advance();
                    let rhs = self.parse_factor(reg, visiting)?;
                    if rhs == 0.0 {
                        return Err(ConstantError::BadExpression {
                            name: "<term>".to_string(),
                            detail: "division by zero".to_string(),
                        });
                    }
                    lhs /= rhs;
                }
                _ => break,
            }
        }
        debug_assert!(iter <= max_steps);
        Ok(lhs)
    }

    fn parse_factor(
        &mut self,
        reg: &FormulasRegistry,
        visiting: &mut Vec<String>,
    ) -> Result<f64, ConstantError> {
        match self.advance() {
            Some(Tok::Num(v)) => Ok(v),
            Some(Tok::Minus) => {
                let v = self.parse_factor(reg, visiting)?;
                Ok(-v)
            }
            Some(Tok::Plus) => self.parse_factor(reg, visiting),
            Some(Tok::LParen) => {
                let v = self.parse_expr(reg, visiting)?;
                match self.advance() {
                    Some(Tok::RParen) => Ok(v),
                    _ => Err(ConstantError::BadExpression {
                        name: "<paren>".to_string(),
                        detail: "missing `)`".to_string(),
                    }),
                }
            }
            Some(Tok::Ident(name)) => reg.derive_inner(&name, visiting),
            other => Err(ConstantError::BadExpression {
                name: format!("{other:?}"),
                detail: "unexpected token".to_string(),
            }),
        }
    }
}

#[cfg(test)]
mod pins;
