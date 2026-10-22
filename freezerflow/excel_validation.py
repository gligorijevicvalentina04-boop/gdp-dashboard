"""Preflight validation for contextual Excel imports. Never writes to the database."""
from collections import Counter

HEADERS = {
    'FREEZER': {'Nom étagère', 'Étagère UID', 'Action'},
    'SHELF': {'Nom rack', 'Rack UID', 'Action'},
    'RACK': {'Position rack', 'Nom boîte', 'Boîte UID', 'Action'},
    'BOX': {'Position', 'Tube UID', 'Échantillon', 'Action'},
}
IDENTIFIERS = {'FREEZER': 'Étagère UID', 'SHELF': 'Rack UID', 'RACK': 'Boîte UID', 'BOX': 'Tube UID'}

def validate_contextual_import(rows, kind, headers):
    errors = []
    expected = HEADERS.get(kind)
    if not expected:
        return ['Niveau Excel non pris en charge.']
    missing = expected - set(headers)
    if missing:
        errors.append('Mauvais modèle Excel pour ce niveau. Colonnes manquantes : ' + ', '.join(sorted(missing)))
        return errors
    uid_field = IDENTIFIERS[kind]
    seen = {}
    for line, row in enumerate(rows, 2):
        # Les 81 positions d'un modèle de boîte sont préremplies avec ADD.
        # Une position sans données de tube reste libre et ne doit pas bloquer l'import.
        if kind == 'BOX' and not any(str(row.get(k) or '').strip() for k in ('Tube UID', 'Échantillon', 'Volume', 'Unité', 'Lot')) and str(row.get('Action') or '').strip().upper() in ('', 'ADD'):
            continue
        action = str(row.get('Action') or '').strip().upper()
        uid = str(row.get(uid_field) or '').strip()
        if action not in {'ADD', 'UPDATE', 'REMOVE'}:
            errors.append(f'Ligne {line} : action requise (ADD, UPDATE ou REMOVE).')
        if uid:
            if uid in seen:
                errors.append(f'Lignes {seen[uid]} et {line} : UID {uid} répété. Une seule action par identifiant est autorisée.')
            else:
                seen[uid] = line
        if action == 'ADD' and uid:
            errors.append(f'Ligne {line} : ADD doit laisser « {uid_field} » vide (identifiant créé par FreezerFlow).')
        if action in {'UPDATE', 'REMOVE'} and not uid:
            errors.append(f'Ligne {line} : {uid_field} obligatoire pour {action}.')
        if kind == 'RACK' and action == 'ADD' and not str(row.get('Nom boîte') or '').strip():
            errors.append(f'Ligne {line} : nom de boîte obligatoire.')
        if kind == 'BOX' and action == 'ADD' and not str(row.get('Échantillon') or '').strip():
            errors.append(f'Ligne {line} : échantillon obligatoire.')
    if not rows:
        errors.append('Le modèle ne contient aucune ligne de données.')
    return errors
