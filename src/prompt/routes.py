from flask import Blueprint, render_template, jsonify, request
from flask import current_app

from src.common.utils import get_db

prompt_bp = Blueprint('prompt_bp', __name__,
                      template_folder='./templates',
                      static_folder='./static',
                      static_url_path='/')


@prompt_bp.route('/prompt')
def prompt():
    return render_template(template_name_or_list='prompt.html',
                           system=current_app.prompt_manager.get_system_prompt(),
                           user=current_app.prompt_manager.get_user_prompt())


@prompt_bp.route('/prompt/save', methods=['POST'])
def save():
    current_app.prompt_manager.update_prompt(request.get_json())
    return jsonify(message="Prompt updated"), 200


