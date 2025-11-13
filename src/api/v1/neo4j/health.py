from flask import Blueprint, jsonify
bp=Blueprint('neo4j',__name__)
@bp.get('/health')
def health():
    return jsonify(dict(backend='neo4j', status='ok'))
