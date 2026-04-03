from __future__ import annotations

HERO_SPECS = {
    "crystal_maiden": {
        "display": "Crystal Maiden",
        "hp": 560,
        "mana": 420,
        "atk": 46,
        "spell_power": 1.0,
        "skills": {
            "q_crystal_nova": {
                "mana_cost": 100,
                "cooldown": 11,
                "damage": 130,
                "effects": [{"type": "slow", "duration": 4, "value": 0.30}],
            },
            "w_frostbite": {
                "mana_cost": 120,
                "cooldown": 9,
                "damage": 150,
                "effects": [{"type": "root", "duration": 1.5}],
            },
            "e_arcane_aura": {
                "mana_cost": 0,
                "cooldown": 0,
                "damage": 0,
                "effects": [{"type": "mana_regen_aura", "duration": 999}],
            },
            "r_freezing_field": {
                "mana_cost": 200,
                "cooldown": 90,
                "damage": 250,
                "effects": [{"type": "slow", "duration": 2, "value": 0.25}],
            },
        },
    },
    "lina": {
        "display": "Lina",
        "hp": 580,
        "mana": 450,
        "atk": 49,
        "spell_power": 1.0,
        "skills": {
            "q_dragon_slave": {
                "mana_cost": 100,
                "cooldown": 9,
                "damage": 140,
                "effects": [],
            },
            "w_light_strike_array": {
                "mana_cost": 110,
                "cooldown": 12,
                "damage": 120,
                "effects": [{"type": "stun", "duration": 1.6}],
            },
            "e_fiery_soul": {
                "mana_cost": 0,
                "cooldown": 0,
                "damage": 0,
                "effects": [{"type": "self_haste", "duration": 8}],
            },
            "r_laguna_blade": {
                "mana_cost": 280,
                "cooldown": 70,
                "damage": 450,
                "effects": [],
            },
        },
    },
}
