
odoo.define('project_workflow_management.DiagramModel', function (require) {
    "use strict";

    require('web_diagram.DiagramModel').include({
        _fetchDiagramInfo: function () {
            if (!this.res_id) {
                return this.do_action({'type': 'history.back'});
            }
            return this._super.apply(this, arguments);
        },
    });
});
