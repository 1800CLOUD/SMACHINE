odoo.define('stock_report.InventoryDateListController', function (require) {
    "use strict"

    var ListController = require('web.ListController');
    
    var InventoryDateListController = ListController.extend({
        buttons_template: 'StockInventoryDateReport.Buttons',

        init: function (parent, model, renderer, params) {
            this.context = renderer.state.getContext();
            return this._super.apply(this, arguments);
        },

        /**
         * @override
         */
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.context.no_loc_at_date) {
                this.$buttons.find('button.o_button_loc_at_date').hide()
            }
            this.$buttons.on('click', '.o_button_loc_at_date', this._onOpenWizard.bind(this));
        },
        _onOpenWizard: function () {
            var state = this.model.get(this.handle, {raw: true});
            var stateContext = state.getContext();
            var context = {
                active_model: this.modelName,
            };
            this.do_action({
                res_model: 'stock.location.date.wizard',
                views: [[false, 'form']],
                target: 'new',
                type: 'ir.actions.act_window',
                context: context,
            });
        },
    });

    return InventoryDateListController;
});