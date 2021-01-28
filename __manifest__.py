# -*- coding: utf-8 -*-

##############################################################################
#
#    Author: Al Kidhma
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Custom Sequence',
    'version': '13.1',
    'category': 'Invoice',
    'sequence': 2,
    'summary': 'Custom Sequence Generation',
    'description': """
        Custom Sequence Generation in Invoice,Quotation and Delivery.
    """,
    'author': 'Al Kidhma',
    'depends': ['base','account','product','sale','stock'],
    'data': [
        'data/sequence_data.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_view.xml',
        'views/product_category_views.xml',

            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
