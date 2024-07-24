import csv
import logging
import os
import secrets
from threading import Thread
import redis
import time
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify
from redis.commands.search.query import Query
from werkzeug.utils import secure_filename

from src.common.ConfigProvider import ConfigProvider
from src.common.utils import get_db
from src.plugins.csv.worker import csv_loader_task

data_bp = Blueprint('data_bp', __name__,
                      template_folder='./templates',
                      static_folder='./static',
                      static_url_path='/')


@data_bp.route('/data', methods=['GET','POST'])
def data():
    idx_overview = []
    idx_alias_info = None

    # Get assets
    RESULTS = 50
    data = []

    rs = get_db().ft("minipilot_data_idx").search(
        Query("*")
        .return_field("filename")
        .sort_by("uploaded", asc=False)
        .paging(0, RESULTS))

    for asset in rs.docs:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], asset.filename)
        if os.path.isfile(path):
            asset.id = asset.id.split(":")[-1]
            data.append(asset)
        else:
            # The path exists only in the database. The application has lost the asset
            # or the container was recreated. Remove the file
            get_db().delete(asset.id)


    # Get indexes
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

    # Get configuration
    cfg = ConfigProvider().get_config()

    return render_template('data.html',
                           idx_overview=idx_overview,
                           data=data,
                           configuration=cfg)


@data_bp.route('/data/delete', methods=['GET','POST'])
def idx_delete():
    if request.args.get('name') is not None:
        logging.warning(f"index deletion: {request.args.get('name')}")
    get_db().ft(request.args.get('name')).dropindex(delete_documents=True)
    return redirect(url_for("data_bp.data"))


@data_bp.route('/data/current', methods=['GET','POST'])
def idx_current():
    if request.args.get('name') is not None:
        get_db().ft(request.args.get('name')).aliasupdate('minipilot_rag_alias')
    return redirect(url_for("data_bp.data"))


@data_bp.route('/data/purge', methods=['GET','POST'])
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
    return redirect(url_for("data_bp.data"))


@data_bp.route('/data/upload', methods=['GET','POST'])
def upload():
    if 'asset' not in request.files:
        print('No asset uploaded')
        return redirect(url_for("data_bp.data"))
    file = request.files['asset']
    if file.filename == '':
        print('No selected file')
        return redirect(url_for("data_bp.data"))
    if file:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        # The file with filename exists, return
        if os.path.isfile(path):
            return redirect(url_for("data_bp.data"))
        # Only CSV accepted as of now
        if file.mimetype == 'text/csv':
            filename = secure_filename(file.filename)
            print(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            print('File successfully uploaded')
            get_db().hset(f"minipilot:data:{secrets.token_hex(10)}", mapping={"filename": filename,
                                                                            "uploaded": int(time.time())})
        return redirect(url_for("data_bp.data"))


@data_bp.route('/data/remove/')
def remove_file():
    # make sure the file is not linked anywhere
    filename = get_db().hget(f"minipilot:data:{request.args.get('id')}", "filename")
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    os.remove(path)

    get_db().delete(f"minipilot:data:{request.args.get('id')}")
    return redirect(url_for("data_bp.data"))


@data_bp.route('/data/work')
def idx_create():
    filename = get_db().hget(f"minipilot:data:{request.args.get('id')}", "filename")
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    # depending on the file type invoke a different worker to index a different file type
    thread = Thread(target=csv_loader_task, args=(path,))
    thread.daemon = True
    thread.start()

    # wait a second and refresh the page so the task appears immediately
    time.sleep(1)

    return redirect(url_for("data_bp.data"))


@data_bp.route('/data/info', methods=['GET'])
def info():
    filename = get_db().hget(f"minipilot:data:{request.args.get('id')}", "filename")
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    with open(path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        dict_from_csv = dict(list(csvReader)[0])
        list_of_column_names = list(dict_from_csv.keys())

    return jsonify(message="File information", info=list_of_column_names), 200


@data_bp.route('/data/config/save', methods=['POST'])
def config_save():
    keys = request.form.keys()
    cfg = ConfigProvider()

    for key in keys:
        cfg.set_key_value(key, request.form.get(key).lower() in ('true', '1', 't', 'on'))

    print(cfg.is_memory())
    print(cfg.is_semantic_cache())
    print(cfg.is_rate_limiter())

    return jsonify(message="Configuration saved"), 200