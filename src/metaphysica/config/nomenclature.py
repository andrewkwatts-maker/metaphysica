"""Naming schemes for shadow dimensions, G2 directions, branes and Hebrew physics labels.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""

import numpy as np

from .parameters.fitted import FittedParameters


# ==============================================================================
# SHADOW DIMENSION NOMENCLATURE (v12.9+)
# 24 Greek Letters for Shadow Spatial Dimensions
# ==============================================================================

class ShadowDimensionNomenclature:
    """
    24-Dimension Greek Letter Naming Scheme for Shadow Spatial Dimensions.

    The 13D shadow (signature 12,1) has 12 spatial dimensions. With Z₂ mirroring
    from the Sp(2,R) gauge structure, this yields 24 total shadow spatial dimensions
    across two Sitra mirror branes:

    - Gate Mirror (Σ₁): 12 dimensions
    - Foundation Mirror (Σ₂): 12 dimensions

    Dimensions are paired by cardinal wall (directionally aligned):
    - North Wall: 3 pairs (Ρ–Δ, Τ–Ε, Ζ–Γ) ← Γ (Earth) at North
    - East Wall: 3 pairs (Ο–Α, Ι–Λ, Σ–Μ) ← Α (Air) at East
    - South Wall: 3 pairs (Π–Ν, Ω–Ξ, Χ–Η) ← Π (Fire) at South
    - West Wall: 3 pairs (Υ–Θ, Β–Φ, Κ–Ψ) ← Υ (Water) at West

    The Sitra Shadow Coupling (shadow_kuf + shadow_chet) governs interactions
    across all paired dimensions.
    """

    # Cardinal walls (4 walls × 3 pairs = 12 paired dimensions)
    WALLS = ("north", "east", "south", "west")

    # Gate Mirror Greek letters - 12 dimensions (Π at South, Υ at West for Shadow_ח)
    GATE_LETTERS = ("Ρ", "Τ", "Ζ", "Ο", "Ι", "Σ", "Π", "Ω", "Χ", "Υ", "Β", "Κ")
    GATE_NAMES = ("Rho", "Tau", "Zeta", "Omicron", "Iota", "Sigma",
                  "Pi", "Omega", "Chi", "Upsilon", "Beta", "Kappa")

    # Foundation Mirror Greek letters - 12 dimensions (Α at East, Γ at North for Shadow_ק)
    FOUNDATION_LETTERS = ("Δ", "Ε", "Γ", "Α", "Λ", "Μ", "Ν", "Ξ", "Η", "Θ", "Φ", "Ψ")
    FOUNDATION_NAMES = ("Delta", "Epsilon", "Gamma", "Alpha", "Lambda", "Mu",
                        "Nu", "Xi", "Eta", "Theta", "Phi", "Psi")

    # Gate Mirror labels (historical naming convention)
    TRIBES = (
        "Reuben", "Judah", "Levi",
        "Joseph", "Benjamin", "Dan",
        "Simeon", "Issachar", "Zebulun",
        "Gad", "Asher", "Naphtali"
    )

    # Gate Mirror gemstone labels
    GEMSTONES = (
        "Ruby", "Emerald", "Zircon",
        "Onyx", "Jasper", "Sapphire",
        "Topaz", "Amethyst", "Peridot",
        "Agate", "Beryl", "Chrysoprase"
    )

    # Foundation Mirror labels (historical naming convention)
    APOSTLES = (
        "Peter", "Andrew", "James the Great",
        "John", "Philip", "Bartholomew",
        "Matthew", "Thomas", "James the Less",
        "Jude", "Simon the Zealot", "Matthias"
    )

    # Symbolic meanings for each paired dimension
    SYMBOLIC_MEANINGS = (
        "Firstborn + Rock (stability)",           # Ρ–Δ: Reuben/Peter
        "Royal + Reach (extension)",              # Τ–Ε: Judah/Andrew
        "Priestly + Heritage (inheritance)",      # Ζ–Γ: Levi/James Great
        "Fruitful + Divine Love (theology)",      # Ο–Α: Joseph/John
        "Beloved + Reason (logos)",               # Ι–Λ: Benjamin/Philip
        "Judge + Truth Spreading (manifest)",     # Σ–Μ: Dan/Bartholomew
        "Hearing + Record (numbers)",             # Π–Ν: Simeon/Matthew
        "Wisdom + Faith Sight (vision)",          # Ω–Ξ: Issachar/Thomas
        "Mariner + Steadfastness (pillar)",       # Χ–Η: Zebulun/James Less
        "Beginning + Unity",                       # Υ–Θ: Gad/Jude
        "Prosperous + Passion (fire)",            # Β–Φ: Asher/Simon Zealot
        "Free + Soul (spirit)"                    # Κ–Ψ: Naphtali/Matthias
    )

    @classmethod
    def get_wall_for_index(cls, index: int) -> str:
        """Determine which wall a dimension belongs to (0-11 → wall name)."""
        if index < 3:
            return "north"
        elif index < 6:
            return "east"
        elif index < 9:
            return "south"
        else:
            return "west"

    @classmethod
    def get_gate_dimension(cls, index: int) -> dict:
        """
        Get Gate Mirror dimension by index (0-11).

        Returns dict with greek_letter, tribe, gemstone, wall, paired letter, notation.
        """
        if not 0 <= index < 12:
            raise ValueError(f"Index must be 0-11, got {index}")

        return {
            "index": index,
            "mirror": "gate",
            "greek_letter": cls.GATE_LETTERS[index],
            "greek_name": cls.GATE_NAMES[index],
            "wall": cls.get_wall_for_index(index),
            "tribe": cls.TRIBES[index],
            "gemstone": cls.GEMSTONES[index],
            "paired_with": cls.FOUNDATION_LETTERS[index],
            "paired_apostle": cls.APOSTLES[index],
            "notation": f"X_{{Ρ–Δ}}".replace("Ρ", cls.GATE_LETTERS[index]).replace("Δ", cls.FOUNDATION_LETTERS[index]),
            "symbolic_meaning": cls.SYMBOLIC_MEANINGS[index]
        }

    @classmethod
    def get_foundation_dimension(cls, index: int) -> dict:
        """
        Get Foundation Mirror dimension by index (0-11).

        Returns dict with greek_letter, apostle, wall, paired letter, notation.
        """
        if not 0 <= index < 12:
            raise ValueError(f"Index must be 0-11, got {index}")

        return {
            "index": index,
            "mirror": "foundation",
            "greek_letter": cls.FOUNDATION_LETTERS[index],
            "greek_name": cls.FOUNDATION_NAMES[index],
            "wall": cls.get_wall_for_index(index),
            "apostle": cls.APOSTLES[index],
            "paired_with": cls.GATE_LETTERS[index],
            "paired_tribe": cls.TRIBES[index],
            "paired_gemstone": cls.GEMSTONES[index],
            "notation": f"X_{{Ρ–Δ}}".replace("Ρ", cls.GATE_LETTERS[index]).replace("Δ", cls.FOUNDATION_LETTERS[index]),
            "symbolic_meaning": cls.SYMBOLIC_MEANINGS[index]
        }

    @classmethod
    def get_paired_dimensions(cls) -> list:
        """
        Return list of all 12 paired dimension coordinates.

        Each pair contains one Gate dimension and one Foundation dimension.
        """
        pairs = []
        for i in range(12):
            pairs.append({
                "index": i,
                "wall": cls.get_wall_for_index(i),
                "gate_letter": cls.GATE_LETTERS[i],
                "foundation_letter": cls.FOUNDATION_LETTERS[i],
                "tribe": cls.TRIBES[i],
                "gemstone": cls.GEMSTONES[i],
                "apostle": cls.APOSTLES[i],
                "notation": f"X_{{{cls.GATE_LETTERS[i]}–{cls.FOUNDATION_LETTERS[i]}}}",
                "symbolic_meaning": cls.SYMBOLIC_MEANINGS[i]
            })
        return pairs

    @classmethod
    def get_wall_dimensions(cls, wall: str) -> list:
        """
        Get all 3 paired dimensions for a specific wall.

        Args:
            wall: One of "north", "east", "south", "west"

        Returns:
            List of 3 paired dimension dicts for that wall.
        """
        wall = wall.lower()
        if wall not in cls.WALLS:
            raise ValueError(f"Wall must be one of {cls.WALLS}, got {wall}")

        wall_index = cls.WALLS.index(wall)
        start_idx = wall_index * 3
        return [cls.get_paired_dimensions()[i] for i in range(start_idx, start_idx + 3)]

    @classmethod
    def get_all_dimensions(cls) -> dict:
        """
        Return complete nomenclature dictionary for JSON export.

        Structure suitable for theory_output.json and website display.
        """
        return {
            "version": "12.9",
            "description": "24-Dimension Greek Letter Naming Scheme",
            "reference": "Z₂ mirror brane structure",
            "structure": {
                "total_dimensions": 24,
                "mirrors": 2,
                "dimensions_per_mirror": 12,
                "walls": 4,
                "pairs_per_wall": 3
            },
            "gate_mirror": {
                "description": "Tribes/Gemstones (Sitra Gate - material side)",
                "letters": list(cls.GATE_LETTERS),
                "letter_names": list(cls.GATE_NAMES),
                "tribes": list(cls.TRIBES),
                "gemstones": list(cls.GEMSTONES)
            },
            "foundation_mirror": {
                "description": "Apostles (Sitra Foundation - spiritual side)",
                "letters": list(cls.FOUNDATION_LETTERS),
                "letter_names": list(cls.FOUNDATION_NAMES),
                "apostles": list(cls.APOSTLES)
            },
            "wall_pairings": {
                "north": {
                    "indices": [0, 1, 2],
                    "pairs": [
                        {"gate": "Ρ", "foundation": "Δ", "tribe": "Reuben", "apostle": "Peter"},
                        {"gate": "Τ", "foundation": "Ε", "tribe": "Judah", "apostle": "Andrew"},
                        {"gate": "Ζ", "foundation": "Γ", "tribe": "Levi", "apostle": "James the Great"}
                    ],
                    "notation": ["X_{Ρ–Δ}", "X_{Τ–Ε}", "X_{Ζ–Γ}"]
                },
                "east": {
                    "indices": [3, 4, 5],
                    "pairs": [
                        {"gate": "Ο", "foundation": "Α", "tribe": "Joseph", "apostle": "John"},
                        {"gate": "Ι", "foundation": "Λ", "tribe": "Benjamin", "apostle": "Philip"},
                        {"gate": "Σ", "foundation": "Μ", "tribe": "Dan", "apostle": "Bartholomew"}
                    ],
                    "notation": ["X_{Ο–Α}", "X_{Ι–Λ}", "X_{Σ–Μ}"]
                },
                "south": {
                    "indices": [6, 7, 8],
                    "pairs": [
                        {"gate": "Π", "foundation": "Ν", "tribe": "Simeon", "apostle": "Matthew"},
                        {"gate": "Ω", "foundation": "Ξ", "tribe": "Issachar", "apostle": "Thomas"},
                        {"gate": "Χ", "foundation": "Η", "tribe": "Zebulun", "apostle": "James the Less"}
                    ],
                    "notation": ["X_{Π–Ν}", "X_{Ω–Ξ}", "X_{Χ–Η}"]
                },
                "west": {
                    "indices": [9, 10, 11],
                    "pairs": [
                        {"gate": "Υ", "foundation": "Θ", "tribe": "Gad", "apostle": "Jude"},
                        {"gate": "Β", "foundation": "Φ", "tribe": "Asher", "apostle": "Simon the Zealot"},
                        {"gate": "Κ", "foundation": "Ψ", "tribe": "Naphtali", "apostle": "Matthias"}
                    ],
                    "notation": ["X_{Υ–Θ}", "X_{Β–Φ}", "X_{Κ–Ψ}"]
                }
            },
            "symbolic_meanings": list(cls.SYMBOLIC_MEANINGS),
            "sitra_shadow_coupling": {
                "shadow_kuf": FittedParameters.SHADOW_KUF,
                "shadow_chet": FittedParameters.SHADOW_CHET,
                "sum": FittedParameters.SHADOW_KUF + FittedParameters.SHADOW_CHET,
                "description": "Gate-Foundation coupling strength across all 24 dimensions"
            }
        }

    @classmethod
    def greek_to_index(cls, letter: str) -> tuple:
        """
        Convert Greek letter to (mirror, index) tuple.

        Args:
            letter: Single Greek letter (e.g., "Ρ", "Δ")

        Returns:
            Tuple of (mirror_name, index) where mirror_name is "gate" or "foundation"
        """
        if letter in cls.GATE_LETTERS:
            return ("gate", cls.GATE_LETTERS.index(letter))
        elif letter in cls.FOUNDATION_LETTERS:
            return ("foundation", cls.FOUNDATION_LETTERS.index(letter))
        else:
            raise ValueError(f"Unknown Greek letter: {letter}")

    @classmethod
    def notation_to_indices(cls, notation: str) -> tuple:
        """
        Parse dimension notation to get both indices.

        Args:
            notation: String like "X_{Ρ–Δ}" or "Ρ–Δ"

        Returns:
            Tuple of (gate_index, foundation_index)
        """
        # Extract letters from notation
        import re
        match = re.search(r'([ΡΓΖΟΙΣΤΩΧΑΒΚ])–([ΔΕΗΘΛΜΝΞΠΥΦΨ])', notation)
        if match:
            gate_letter, foundation_letter = match.groups()
            return (cls.GATE_LETTERS.index(gate_letter),
                    cls.FOUNDATION_LETTERS.index(foundation_letter))
        raise ValueError(f"Could not parse notation: {notation}")


# ==============================================================================
# G₂ MANIFOLD DIRECTION NOMENCLATURE (v12.9+)
# Seven Hebrew Letters for G₂ Internal Directions
# ==============================================================================

class G2DirectionNomenclature:
    """
    7-Direction Hebrew Letter Naming Scheme for G₂ Manifold.

    The 7D G₂ holonomy manifold (TCS construction) has 7 internal directions:

    - Gח - Primary volume
    - Gג - Structural form
    - Gת - Chirality axis
    - Gנ - Primary flux
    - Gה - Modulus scaling
    - Gי - Torsion axis
    - Gמ - Attractor direction

    The 7 G₂ directions form the geometric foundation of compactification.
    """

    # Hebrew letters for the 7 directions
    HEBREW_LETTERS = ("ח", "ג", "ת", "נ", "ה", "י", "מ")

    # Transliterated names
    LETTER_NAMES = ("Chet", "Gimel", "Tav", "Nun", "Heh", "Yud", "Mem")

    # Variable names (Python/JS compatible)
    VARIABLE_NAMES = ("G_chet", "G_gimel", "G_tav", "G_nun", "G_heh", "G_yud", "G_mem")

    # Display notation (G with Hebrew subscript)
    DISPLAY_NAMES = ("Gח", "Gג", "Gת", "Gנ", "Gה", "Gי", "Gמ")

    # Historical naming labels
    SEFIROT = ("Chesed", "Gevurah", "Tiferet", "Netzach", "Hod", "Yesod", "Malkuth")

    # English translations (historical)
    SEFIROT_ENGLISH = (
        "Loving-kindness",
        "Strength",
        "Beauty",
        "Victory",
        "Splendor",
        "Foundation",
        "Kingdom"
    )

    # Geometric roles in G₂ manifold
    GEOMETRIC_ROLES = (
        "Primary volume",
        "Structural form",
        "Chirality axis",
        "Primary flux",
        "Modulus scaling",
        "Torsion axis",
        "Attractor direction"
    )

    # Historical naming labels
    ENOCHIAN_KINGS = (
        "Baligon", "Bobogel", "Babalel", "Bynepor", "Bnaspol", "Blumaza", "Bagenol"
    )

    # Planetary/Day associations (historical)
    PLANETARY_DAYS = (
        ("Sun", "Sunday"),
        ("Moon", "Monday"),
        ("Mars", "Tuesday"),
        ("Jupiter", "Thursday"),
        ("Venus", "Friday"),
        ("Mercury", "Wednesday"),
        ("Saturn", "Saturday")
    )

    # Pillar structure (historical)
    SEFIROT_PAIRS = {
        "right_pillar": ["Chesed", "Netzach"],
        "left_pillar": ["Gevurah", "Hod"],
        "middle_pillar": ["Tiferet", "Yesod", "Malkuth"]
    }

    @classmethod
    def get_direction(cls, index: int) -> dict:
        """
        Get G₂ direction by index (0-6).

        Returns dict with hebrew_letter, sefirah, geometric_role, etc.
        """
        if not 0 <= index < 7:
            raise ValueError(f"Index must be 0-6, got {index}")

        return {
            "index": index,
            "hebrew_letter": cls.HEBREW_LETTERS[index],
            "letter_name": cls.LETTER_NAMES[index],
            "variable_name": cls.VARIABLE_NAMES[index],
            "display_name": cls.DISPLAY_NAMES[index],
            "sefirah": cls.SEFIROT[index],
            "sefirah_english": cls.SEFIROT_ENGLISH[index],
            "geometric_role": cls.GEOMETRIC_ROLES[index],
            "enochian_king": cls.ENOCHIAN_KINGS[index],
            "planet": cls.PLANETARY_DAYS[index][0],
            "day": cls.PLANETARY_DAYS[index][1]
        }

    @classmethod
    def get_all_directions(cls) -> dict:
        """
        Return complete nomenclature dictionary for JSON export.

        Structure suitable for theory_output.json and website display.
        """
        directions = []
        for i in range(7):
            directions.append(cls.get_direction(i))

        return {
            "version": "12.9",
            "description": "7-Direction Hebrew Letter Naming for G₂ Manifold",
            "reference": "TCS G₂ holonomy construction",
            "structure": {
                "total_directions": 7,
                "holonomy_group": "G₂",
                "manifold_type": "TCS (Twisted Connected Sum)"
            },
            "directions": {
                cls.VARIABLE_NAMES[i]: {
                    "index": i,
                    "hebrew": cls.HEBREW_LETTERS[i],
                    "display": cls.DISPLAY_NAMES[i],
                    "sefirah": cls.SEFIROT[i],
                    "meaning": cls.SEFIROT_ENGLISH[i],
                    "geometric_role": cls.GEOMETRIC_ROLES[i],
                    "enochian_king": cls.ENOCHIAN_KINGS[i],
                    "planet": cls.PLANETARY_DAYS[i][0],
                    "day": cls.PLANETARY_DAYS[i][1]
                }
                for i in range(7)
            },
            "historical_labels": {
                "kings": list(cls.ENOCHIAN_KINGS),
                "planetary_days": [
                    {"planet": p, "day": d} for p, d in cls.PLANETARY_DAYS
                ]
            },
            "topology": {
                "b2": 4,
                "b3": 24,
                "chi_eff": 144,
                "generations": 3
            },
            "footnote": "The G₂ directions are labeled G with Hebrew letter subscripts as a mnemonic for their progressive geometric roles."
        }

    @classmethod
    def variable_to_hebrew(cls, var_name: str) -> str:
        """Convert variable name (e.g., 'G_chet') to Hebrew display (e.g., 'Gח')."""
        if var_name in cls.VARIABLE_NAMES:
            idx = cls.VARIABLE_NAMES.index(var_name)
            return cls.DISPLAY_NAMES[idx]
        raise ValueError(f"Unknown variable name: {var_name}")

    @classmethod
    def hebrew_to_variable(cls, display: str) -> str:
        """Convert Hebrew display (e.g., 'Gח') to variable name (e.g., 'G_chet')."""
        if display in cls.DISPLAY_NAMES:
            idx = cls.DISPLAY_NAMES.index(display)
            return cls.VARIABLE_NAMES[idx]
        raise ValueError(f"Unknown display name: {display}")

    @classmethod
    def get_pillar(cls, direction_index: int) -> str:
        """
        Get which pillar of the Tree of Life this direction belongs to.

        Returns: "right_pillar", "left_pillar", or "middle_pillar"
        """
        sefirah = cls.SEFIROT[direction_index]
        for pillar, sefirot in cls.SEFIROT_PAIRS.items():
            if sefirah in sefirot:
                return pillar
        return "unknown"


# ==============================================================================
# BRANE NOMENCLATURE (v12.9)
# ==============================================================================

class BraneNomenclature:
    """
    Brane Localization Factors (v12.9).

    4 branes with Greek letter subscripts:
    - Λ_Α (Exarp) = (5,1) Observable
    - Λ_Π (Bitom) = Gen 1 (3,1)
    - Λ_Υ (Hcoma) = Gen 2 (3,1)
    - Λ_Γ (Nanta) = Gen 3 (3,1)

    Sitra Shadow Coupling:
    - ק_Α_Γ = Shadow_ק = 0.576152 (Exarp↔Nanta)
    - ח_Π_Υ = Shadow_ח = 0.576152 (Bitom↔Hcoma)
    """

    # Brane names
    ENOCHIAN_NAMES = ("Exarp", "Bitom", "Hcoma", "Nanta")

    # Greek letters (Alpha, Pi, Upsilon, Gamma)
    GREEK_LETTERS = ("Α", "Π", "Υ", "Γ")
    GREEK_NAMES = ("Alpha", "Pi", "Upsilon", "Gamma")

    # Greek letter etymology (historical)
    GREEK_ETYMOLOGY = {
        "Α": "Alpha - First letter",
        "Π": "Pi",
        "Υ": "Upsilon",
        "Γ": "Gamma"
    }

    # Lambda symbols for display
    LAMBDA_SYMBOLS = ("Λ_Α", "Λ_Π", "Λ_Υ", "Λ_Γ")

    # Variable names (Python/JS)
    VARIABLE_NAMES = ("lambda_alpha", "lambda_pi", "lambda_upsilon", "lambda_gamma")

    # Elements
    ELEMENTS = ("Air", "Fire", "Water", "Earth")

    # Cardinal directions
    DIRECTIONS = ("East", "South", "West", "North")

    # Brane signatures
    SIGNATURES = ((5, 1), (3, 1), (3, 1), (3, 1))

    # Y-positions in extra dimension (fractions of πR)
    Y_POSITIONS = (0.0, 1.0/3.0, 2.0/3.0, 1.0)

    # Physics roles
    PHYSICS_ROLES = (
        "SM Observable (EM, light)",
        "Generation 1 (e, u, d - stable)",
        "Generation 2 (μ, c, s - transitional)",
        "Generation 3 (τ, t, b - heavy)"
    )

    # Historical quotes (naming reference)
    ENOCH_QUOTES = (
        "Three gates of heaven open",
        "From the first gate proceed",
        "I saw three great gates",
        "I went to the north"
    )

    # Warping parameter for brane localization (k_ג)
    # Calibrated to give warp factors: 1, ~10^-6, ~10^-12, ~10^-17
    # Formula: Λ = e^(-k_ג×y×π) where y = 0, 1/3, 2/3, 1
    K_GIMEL = 12.31  # Derived: k_ג = b₃/2 + 1/π = 12 + 0.318 ≈ 12.31

    # Sitra Shadow Coupling
    SITRA_COUPLINGS = {
        "kuf_alpha_gamma": {
            "symbol": "ק_Α_Γ",
            "value": 0.576152,
            "pair": ("Exarp", "Nanta"),
            "elements": ("Air", "Earth"),
            "description": "Observable↔Heavy Sitra coupling"
        },
        "chet_pi_upsilon": {
            "symbol": "ח_Π_Υ",
            "value": 0.576152,
            "pair": ("Bitom", "Hcoma"),
            "elements": ("Fire", "Water"),
            "description": "Gen1↔Gen2 Sitra coupling"
        }
    }

    @classmethod
    def localization_factor(cls, index: int) -> float:
        """Calculate Λ = e^(-k×y×πR) for brane at index."""
        import numpy as np
        y = cls.Y_POSITIONS[index]
        return np.exp(-cls.K_GIMEL * y * np.pi)

    @classmethod
    def get_brane(cls, index: int) -> dict:
        """Get complete brane info by index (0-3)."""
        if not 0 <= index < 4:
            raise ValueError(f"Index must be 0-3, got {index}")

        return {
            "index": index,
            "enochian": cls.ENOCHIAN_NAMES[index],
            "greek_letter": cls.GREEK_LETTERS[index],
            "greek_name": cls.GREEK_NAMES[index],
            "lambda_symbol": cls.LAMBDA_SYMBOLS[index],
            "variable_name": cls.VARIABLE_NAMES[index],
            "element": cls.ELEMENTS[index],
            "direction": cls.DIRECTIONS[index],
            "signature": cls.SIGNATURES[index],
            "y_position": cls.Y_POSITIONS[index],
            "localization_factor": cls.localization_factor(index),
            "physics_role": cls.PHYSICS_ROLES[index],
            "enoch_quote": cls.ENOCH_QUOTES[index]
        }

    @classmethod
    def get_all_branes(cls) -> dict:
        """Return complete nomenclature for JSON export."""
        import numpy as np

        branes = {}
        for i in range(4):
            var_name = cls.VARIABLE_NAMES[i]
            branes[var_name] = cls.get_brane(i)

        return {
            "version": "12.9",
            "description": "Brane Localization Factors",
            "reference": "Warped extra dimension framework",
            "greek_etymology": cls.GREEK_ETYMOLOGY,
            "branes": branes,
            "sitra_couplings": cls.SITRA_COUPLINGS,
            "warping_parameter": cls.K_GIMEL,
            "footnote": "Greek letters chosen for elemental correspondence: Α(Air), Π(Pyr/Fire), Υ(Hydor/Water), Γ(Gaia/Earth)"
        }


# ==============================================================================
# HEBREW PHYSICS NOMENCLATURE (v12.9)
# ==============================================================================

class HebrewPhysicsNomenclature:
    """
    Hebrew Letter Naming for Key Physics Parameters (v12.9).

    Maps 5 key physics parameters to Hebrew letters:
    - k_ג (k_gimel): Warping constant ≈ 12.31
    - C_כ (C_kaf): Flux normalization ≈ 27.2
    - f_ה (f_heh): Partition divisor ≈ 4.5
    - S_מ (S_mem): Instanton suppression ≈ 40
    - δ_ל (delta_lamed): Threshold correction ≈ 1.2
    """

    # k_gimel (ג): Warping constant - GEOMETRICALLY DERIVED (v14.1)
    # Geometric formula: k_ג = b₃/2 + 1/π = 12 + 0.318 = 12.318 ≈ 12.31
    K_GIMEL = 12.31  # Derived: b₃/2 + 1/π = 24/2 + 1/π = 12.318
    K_GIMEL_SYMBOL = "k_ג"
    K_GIMEL_DESCRIPTION = "Warping parameter controlling exponential hierarchy in brane tensions"
    K_GIMEL_FORMULA = "k_ג = b₃/2 + 1/π (geometric: brane spacing + G₂ holonomy)"
    K_GIMEL_APPLICATION = "Λ(y) = exp(-k_ג × y × π)"
    K_GIMEL_SIMULATION = "simulations/k_warp_geometric_v14_1.py"

    # C_kaf (כ): Flux normalization - GEOMETRICALLY DERIVED (v14.1)
    # Geometric formula: C_כ = b₃ × (b₃-7)/(b₃-9) = 24 × 17/15 = 27.2
    C_KAF = 27.2  # Derived: b₃(b₃-7)/(b₃-9) = 24×17/15 = 27.2
    C_KAF_SYMBOL = "C_כ"
    C_KAF_DESCRIPTION = "Normalizes flux quanta to give effective torsion T_ω = -b₃ / C_כ"
    C_KAF_FORMULA = "C_כ = b₃ × (b₃-7)/(b₃-9) (geometric: moduli/cycle ratio)"
    C_KAF_APPLICATION = "T_ω = -b₃ / C_כ = -24 / 27.2 ≈ -0.882"
    C_KAF_SIMULATION = "simulations/c_flux_geometric_v14_1.py"

    # f_heh (ה): Partition divisor - GEOMETRICALLY DERIVED (v14.1)
    # Geometric formula: f_ה = 9/2 = 4.5 (moduli partition)
    F_HEH = 4.5  # Derived: moduli_count/2 = 9/2 = 4.5
    F_HEH_SYMBOL = "f_ה"
    F_HEH_DESCRIPTION = "Effective partition factor from moduli distribution"
    F_HEH_FORMULA = "f_ה = (moduli count)/2 = 9/2 = 4.5"
    F_HEH_APPLICATION = "Partition factor in flux normalization between visible/hidden sectors"
    F_HEH_SIMULATION = "simulations/f_part_geometric_v14_1.py"

    # S_mem (מ): Instanton suppression
    S_MEM = 40.0  # Derived: 2π/α_GUT ≈ 2π × 6.4 ≈ 40 (instanton action)
    S_MEM_SYMBOL = "S_מ"
    S_MEM_DESCRIPTION = "Instanton action for non-perturbative Yukawa suppression"
    S_MEM_FORMULA = "Y_ij ∝ exp(-S_מ) for heavy mode suppression"

    # δ_lamed (ל): Threshold correction
    DELTA_LAMED = 1.2  # Derived: KK threshold correction coefficient (1-loop)
    DELTA_LAMED_SYMBOL = "δ_ל"
    DELTA_LAMED_DESCRIPTION = "Coefficient for KK/heavy threshold corrections in RG flow"
    DELTA_LAMED_FORMULA = "α_GUT(M_GUT) = α_GUT^tree × (1 + δ_ל × loop_factor)"

    # Complete Hebrew Letter Mapping
    HEBREW_PARAMETERS = {
        "k_gimel": {
            "hebrew": "ג",
            "symbol": "k_ג",
            "english_name": "k_gimel",
            "value": 12.31,
            "unit": "dimensionless",
            "meaning": "Bridge between observable and shadow sectors",
            "physics": "Warping parameter in brane localization Λ(y) = exp(-k_ג × y × π)",
            "derivation": "k_ג = b₃/2 + 1/π = 12 + 0.318 = 12.318 (GEOMETRIC)",
            "simulation": "simulations/k_warp_geometric_v14_1.py",
            "status": "DERIVED"
        },
        "C_kaf": {
            "hebrew": "כ",
            "symbol": "C_כ",
            "english_name": "C_kaf",
            "value": 27.2,
            "unit": "dimensionless",
            "meaning": "Shapes flux quanta into effective torsion",
            "physics": "Flux normalization: T_ω = -b₃ / C_כ",
            "derivation": "C_כ = b₃ × (b₃-7)/(b₃-9) = 24 × 17/15 (GEOMETRIC)",
            "simulation": "simulations/c_flux_geometric_v14_1.py",
            "status": "DERIVED"
        },
        "f_heh": {
            "hebrew": "ה",
            "symbol": "f_ה",
            "english_name": "f_heh",
            "value": 4.5,
            "unit": "dimensionless",
            "meaning": "Partition split between mirror branes",
            "physics": "Partition factor in flux normalization",
            "derivation": "f_ה = (moduli count)/2 = 9/2 = 4.5 (GEOMETRIC)",
            "simulation": "simulations/f_part_geometric_v14_1.py",
            "status": "DERIVED"
        },
        "S_mem": {
            "hebrew": "מ",
            "symbol": "S_מ",
            "english_name": "S_mem",
            "value": 40.0,
            "unit": "dimensionless",
            "meaning": "Seals heavy modes via instantons",
            "physics": "Instanton action for non-perturbative suppression",
            "derivation": "S_מ ≈ 8π²/g² for SU(N) instantons"
        },
        "delta_lamed": {
            "hebrew": "ל",
            "symbol": "δ_ל",
            "english_name": "delta_lamed",
            "value": 1.2,
            "unit": "dimensionless",
            "meaning": "Refines tree-level via loop corrections",
            "physics": "KK/heavy threshold corrections in RG flow",
            "derivation": "δ_ל = Σᵢ bᵢ × ln(Mᵢ/M_GUT) / (2π)"
        }
    }

    @classmethod
    def get_parameter(cls, name: str) -> dict:
        """Get complete parameter info by name."""
        if name not in cls.HEBREW_PARAMETERS:
            raise ValueError(f"Unknown parameter: {name}")
        return cls.HEBREW_PARAMETERS[name]

    @classmethod
    def get_all_parameters(cls) -> dict:
        """Return complete nomenclature for JSON export."""
        return {
            "version": "12.9",
            "description": "Hebrew Letter Naming for Physics Parameters",
            "reference": "Parameter nomenclature system",
            "parameters": cls.HEBREW_PARAMETERS,
            "footnote": "Hebrew letter subscripts provide a consistent naming convention"
        }
