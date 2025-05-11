
from flask_paginate import Pagination

def paginate_query(query, page, per_page=5):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination
