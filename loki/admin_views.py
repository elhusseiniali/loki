from flask_admin.contrib.sqla import ModelView
from flask_admin.model import typefmt


# Show null values instead of empty strings.
MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({type(None): typefmt.null_formatter})


class UserView(ModelView):
    form_columns = (
        'username',
        'email',
        'password',
    )
    column_editable_list = ('username', 'email')
    column_searchable_list = ('username', 'email')
    column_type_formatters = MY_DEFAULT_FORMATTERS
