import flask
from flask import Blueprint, render_template, redirect, url_for, current_app, jsonify, request
from redis.commands.search.query import Query
from flask_paginate import Pagination, get_page_args

from src.common.utils import get_db

cache_bp = Blueprint('cache_bp', __name__,
                      template_folder='./templates',
                      static_folder='./static',
                      static_url_path='/')


@cache_bp.route('/cache')
def cache():
    pagination = None
    conn = get_db()

    if (flask.request.args.get("q") is not None
            and len(flask.request.args.get("q"))
            and flask.request.args.get("s") == "semantic"):
        cache = current_app.llmcache.check(prompt=flask.request.args.get("q"),
                                           num_results=10,
                                           return_fields=["response", "prompt"])

        # results are returned as dict
        for entry in cache:
            entry['ttl'] = conn.ttl(entry['id'])
            entry['id'] = entry['id'].split(":")[-1]

    elif (flask.request.args.get("q") is not None
            and len(flask.request.args.get("q"))
            and flask.request.args.get("s") == "fulltext"):

        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        rs = get_db().ft("minipilot_cache_idx").search(Query(flask.request.args.get("q")).return_fields(*['id', 'prompt', 'response']).paging(offset, per_page))
        cache = rs.docs
        pagination = Pagination(page=page, per_page=10, total=rs.total, css_framework='bulma',
                                bulma_style='small', prev_label='Previous', next_label='Next page')

        # results are returned as redis.commands.search.document.Document
        for entry in cache:
            entry.ttl = conn.ttl(entry.id)
            entry.id = entry.id.split(":")[-1]
    else:
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        rs = get_db().ft("minipilot_cache_idx").search(Query("*").return_fields(*['id', 'prompt', 'response']).paging(offset, per_page))
        cache = rs.docs
        pagination = Pagination(page=page, per_page=10, total=rs.total, css_framework='bulma',
                                bulma_style='small', prev_label='Previous', next_label='Next page')

        # results are returned as redis.commands.search.document.Document
        for entry in cache:
            entry.ttl = conn.ttl(entry.id)
            entry.id = entry.id.split(":")[-1]

    return render_template('cache.html',
                           pagination=pagination,
                           question=flask.request.args.get("q"),
                           cache=cache,
                           search=flask.request.args.get("s"))


@cache_bp.route('/cache/delete')
def cache_delete():
    if flask.request.args.get("doc") is not None:
        doc_id = flask.request.args.get("doc")
        get_db().delete(f"minipilot:cache:item:{doc_id}")
    return redirect(url_for("cache_bp.cache"))


@cache_bp.route('/cache/save', methods=['POST'])
def cache_save():
    data = request.get_json()
    doc_id = data["doc"]
    response = data["response"]
    get_db().hset(f"minipilot:cache:item:{doc_id}", mapping={"response": response})
    return jsonify(message="Cache item updated"), 200


@cache_bp.route('/cache/persist', methods=['POST'])
def cache_persist():
    data = request.get_json()
    doc_id = data["doc"]

    p = get_db().pipeline(transaction=True)
    p.persist(f"minipilot:cache:item:{doc_id}")
    p.sadd("minipilot:cache:persisted", doc_id)
    p.execute()
    return jsonify(message="Cache item persisted"), 200