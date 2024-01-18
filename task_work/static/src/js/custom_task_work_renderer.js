//odoo.define('custom_project.custom_task_work_renderer', function (require) {
//    "use strict";
//
//    var ListRenderer = require('web.ListRenderer');
//
//    ListRenderer.include({
//        _renderBodyCell: function (record, node, colIndex, options) {
//            var fieldName = node.attrs.name;
//            if (fieldName === 'employee_ids') {
//                var employeeImages = record.data[fieldName].data.map(function (employee) {
//                    return '<img src="data:image/png;base64,' + employee.data.image_128 + '" alt="Employee Image">';
//                });
//                var superResult = this._super(record, node, colIndex, _.extend({}, options, { escape: false }));
//                return superResult + employeeImages.join('');
//            }
//            return this._super.apply(this, arguments);
//        }
//    });
//});
