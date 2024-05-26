import logging

import redis
from flask import Blueprint, render_template, request, redirect, url_for
from redis.commands.search.query import Query

from src.common.utils import get_db

status_bp = Blueprint('status_bp', __name__,
                      template_folder='./templates',
                      static_folder='./static',
                      static_url_path='/')


@status_bp.route('/status', methods=['GET','POST'])
def status():
    idx_overview = []
    idx_alias_info = None

    try:
        idx_alias_info = get_db().ft("minipilot_rag_alias").info()
    except:
        # the alias has not been created yet
        pass

    try:
        indexes = get_db().execute_command("FT._LIST")
        rag_indexes = [idx for idx in indexes if idx.startswith("minipilot_rag")]
        for idx in rag_indexes:
            idx_info = get_db().ft(idx).info()
            tmp = {'name': idx_info['index_name'], 'docs': str(idx_info['num_docs']), 'is_current': False}

            # check to what index the alias is pointing
            if idx_alias_info is not None:
                if idx_info['index_name'] == idx_alias_info['index_name']:
                    tmp['is_current'] = True

            idx_overview.append(tmp)
    except redis.exceptions.ResponseError as e:
        print(e)

    return render_template('status.html', idx_overview=idx_overview)


@status_bp.route('/status/delete', methods=['GET','POST'])
def idx_delete():
    if request.args.get('name') is not None:
        logging.warning(f"index deletion: {request.args.get('name')}")
    get_db().ft(request.args.get('name')).dropindex(delete_documents=True)
    return redirect(url_for("status_bp.status"))


@status_bp.route('/status/current', methods=['GET','POST'])
def idx_current():
    if request.args.get('name') is not None:
        get_db().ft(request.args.get('name')).aliasupdate('minipilot_rag_alias')
    return redirect(url_for("status_bp.status"))


@status_bp.route('/status/purge', methods=['GET','POST'])
def idx_purge():
    if request.args.get('category') is not None:
        cat_filter = f"@category:{{{request.args.get('category')}}} "
        numeric_filter = f"@updated:[-inf {request.args.get('start')}]"
        rs = get_db().ft("minipilot_page_idx").search(
            Query(cat_filter + numeric_filter)
            .return_field("url")
            .paging(0, 10000))
        for doc in rs.docs:
            get_db().delete(doc['id'])
            logging.info(f"This URL has been purged from the full-text index: {doc['id']}")
    return redirect(url_for("status_bp.status"))





