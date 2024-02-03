odoo.define('stock_report.InventoryDateListView', function (require) {
    "use strict"

    var ListView = require('web.ListView');
    var InventoryDateListController = require('stock_report.InventoryDateListController');
    var viewRegistry = require('web.view_registry');

    var InventoryDateListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: InventoryDateListController,
        }),
    });

    viewRegistry.add('inventory_date_report_list', InventoryDateListView);

    return InventoryDateListView
});