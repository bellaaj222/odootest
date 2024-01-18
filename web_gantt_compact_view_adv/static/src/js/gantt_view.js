odoo.define('web_gantt_compact_view_adv.WebGanttView', function (require) {
    "use strict";
    
    var AbstractView = require('web.AbstractView');
    var WebGanttModel = require('web_gantt_compact_view_adv.WebGanttModel');
    var WebGanttRenderer = require('web_gantt_compact_view_adv.WebGanttRenderer');
    var WebGanttController = require('web_gantt_compact_view_adv.WebGanttController');
    var view_registry = require('web.view_registry');
    
    var session = require('web.session');
    var core = require('web.core');
    
    var _t = core._t;
    var _lt = core._lt;
    
    var fields_to_gather = [];

    var WebGanttView = AbstractView.extend({
        display_name: _lt('Gantt'),
        icon: 'fa fa-tasks',
        viewType: 'webganttview',
        cssLibs: [
            "/web_gantt_compact_view_adv/static/lib/dhtmlxGantt/sources/dhtmlxgantt.css"
        ],
        jsLibs: [
            "/web_gantt_compact_view_adv/static/lib/dhtmlxGantt/sources/dhtmlxgantt.js",
            "/web_gantt_compact_view_adv/static/lib/dhtmlxGantt/sources/api.js",
        ],
        config: _.extend({}, AbstractView.prototype.config, {
            Model: WebGanttModel,
            Controller: WebGanttController,
            Renderer: WebGanttRenderer,
        }),

        init: function (viewInfo, params) {
            this._super.apply(this, arguments);

            var arch = this.arch;
            var fields = this.fields;
            
            var mapping = {
                name: 'name',              
            };
    
            _.each(fields_to_gather, function (field) {
                if (arch.attrs[field]) {
                    mapping[field] = arch.attrs[field];
                }
            });

            var scale = params.context.default_scale || arch.attrs.default_scale || 'month';
    
            this.controllerParams.context = params.context || {};
            this.controllerParams.title = params.title || arch.attrs.string || _t("Gantt");            
            this.controllerParams.dateStartField = arch.attrs.date_start;
			this.controllerParams.dateStopField = arch.attrs.date_stop;
            this.controllerParams.linkModel = this.arch.attrs.link_model;

            this.loadParams.fields = fields;
            this.loadParams.mapping = mapping;
            this.loadParams.scale = scale;
            this.loadParams.initialDate = moment(params.initialDate || new Date());
            this.loadParams.defaultGroupBy = arch.attrs.default_group_by;
            
            this.loadParams.dateStartField = arch.attrs.date_start;
			this.loadParams.dateStopField = arch.attrs.date_stop;
            this.loadParams.progressField = arch.attrs.progress;
            this.loadParams.colorField = arch.attrs.color;
            this.loadParams.taskType = arch.attrs.task_type;
            this.loadParams.deadLine = arch.attrs.deadline;
            this.loadParams.showLinks = arch.attrs.show_links;
            this.loadParams.roundDndDates = arch.attrs.round_dnd_dates;
            this.loadParams.linkModel = this.arch.attrs.link_model;
            this.loadParams.taskPriority = arch.attrs.priority;

            
            this.rendererParams.dateStartField = arch.attrs.date_start;
			this.rendererParams.dateStopField = arch.attrs.date_stop;
            this.rendererParams.progressField = arch.attrs.progress;
            this.rendererParams.colorField = arch.attrs.color;
            this.rendererParams.taskType = arch.attrs.task_type;
            this.rendererParams.taskPriority = arch.attrs.priority;
            this.rendererParams.deadLine = arch.attrs.deadline;
            this.rendererParams.showLinks = arch.attrs.show_links;
            this.rendererParams.roundDndDates = arch.attrs.round_dnd_dates;
            this.rendererParams.linkModel = this.arch.attrs.link_model;
        },
    });
    
    view_registry.add('webganttview', WebGanttView);    
    return WebGanttView;    
});