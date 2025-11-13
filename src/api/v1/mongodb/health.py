from flask import Blueprint, jsonify
bp=Blueprint('mongodb',__name__)
@bp.get('/health')
def health():
    return jsonify(dict(backend='mongodb', status='ok'))
