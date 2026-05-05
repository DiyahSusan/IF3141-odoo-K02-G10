from odoo import api, fields, models


class BetaAuditLog(models.Model):
    _name = "beta.audit.log"
    _description = "BETA Audit Log"
    _order = "action_date desc, id desc"

    action = fields.Char(required=True)
    action_type = fields.Selection(
        [
            ("create", "Create"),
            ("submit", "Submit"),
            ("validate", "Validate"),
            ("reject", "Reject"),
            ("revision", "Revision"),
            ("reset", "Reset"),
            ("export", "Export"),
            ("update", "Update"),
        ],
        default="update",
        required=True,
    )
    model_name = fields.Char(required=True)
    record_display_name = fields.Char(required=True)
    record_ref = fields.Char()
    user_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)
    action_date = fields.Datetime(required=True, default=fields.Datetime.now)
    project_id = fields.Many2one("project.project")
    document_id = fields.Many2one("beta.controlled.document")
    version = fields.Char()
    note = fields.Text()

    @api.model
    def log_action(self, record, action, note=None, action_type="update"):
        document = record if record._name == "beta.controlled.document" else False
        project = False
        if hasattr(record, "project_id") and record.project_id:
            project = record.project_id
        elif document and document.requirement_id.project_id:
            project = document.requirement_id.project_id
        self.sudo().create(
            {
                "action": action,
                "action_type": action_type,
                "model_name": record._name,
                "record_display_name": record.display_name,
                "record_ref": getattr(record, "reference", False) or str(record.id),
                "user_id": self.env.user.id,
                "project_id": project.id if project else False,
                "document_id": document.id if document else False,
                "version": getattr(record, "version", False) or False,
                "note": note or "",
            }
        )

    def _get_export_records(self):
        return self if self else self.search([])

    def action_export_csv(self):
        records = self._get_export_records()
        if records:
            self.env["beta.audit.log"].log_action(
                records[:1],
                "Audit log exported to CSV",
                f"{len(records)} rows exported.",
                action_type="export",
            )
        ids_param = ",".join(str(record.id) for record in records)
        return {
            "type": "ir.actions.act_url",
            "url": f"/beta_sisfo/audit/export/csv?ids={ids_param}",
            "target": "self",
        }

    def action_export_xlsx(self):
        records = self._get_export_records()
        if records:
            self.env["beta.audit.log"].log_action(
                records[:1],
                "Audit log exported to XLSX",
                f"{len(records)} rows exported.",
                action_type="export",
            )
        ids_param = ",".join(str(record.id) for record in records)
        return {
            "type": "ir.actions.act_url",
            "url": f"/beta_sisfo/audit/export/xlsx?ids={ids_param}",
            "target": "self",
        }

    def action_export_pdf(self):
        records = self._get_export_records()
        if records:
            self.env["beta.audit.log"].log_action(
                records[:1],
                "Audit log exported to PDF",
                f"{len(records)} rows exported.",
                action_type="export",
            )
        action = self.env.ref("beta_sisfo.action_report_beta_audit_log").report_action(records)
        return {key: value for key, value in action.items() if value is not None}
